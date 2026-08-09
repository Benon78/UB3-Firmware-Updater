"""
=========================================================
UB3 Firmware Updater

Process Runner

Developer:
Benjamin William

Description:
Controlled external-process execution for the UB3 updater.

Responsibilities
----------------
• Start an external process
• Pass command-line arguments
• Capture stdout/stderr
• Stream process output
• Handle timeout
• Handle cancellation
• Terminate Windows process trees safely
• Return process results

This module does NOT:
• Detect USB devices
• Validate firmware
• Decide whether an upload should start
• Control the GUI
• Interpret Maple Loader output

The existing application architecture is preserved:

    UploadWorker
        ↓
    UploadService
        ↓
    ProcessRunner
        ↓
    maple_upload.bat
        ↓
    maple_loader.jar

Version:
0.5.3
=========================================================
"""

from __future__ import annotations

import os
import subprocess
import threading
import time

from dataclasses import dataclass

from pathlib import Path

from typing import Callable, Sequence


# =========================================================
# Process Result
# =========================================================

@dataclass(slots=True)
class ProcessResult:
    """
    Result returned after an external process finishes.

    This is an OS/process-level result. UploadService remains
    responsible for interpreting Maple Loader output.
    """

    command: list[str]

    return_code: int | None = None

    stdout: str = ""

    stderr: str = ""

    timed_out: bool = False

    cancelled: bool = False

    started: bool = False

    error: str = ""

    duration_seconds: float = 0.0

    @property
    def success(self) -> bool:
        """Return True when the process completed successfully."""
        return (
            self.started
            and not self.timed_out
            and not self.cancelled
            and not self.error
            and self.return_code == 0
        )

    @property
    def failed(self) -> bool:
        """Return True when the process failed at OS level."""
        return self.started and not self.success


# =========================================================
# Process Runner
# =========================================================

class ProcessRunner:
    """
    Controlled process runner used by application services.

    A single ProcessRunner instance owns at most one active
    process. This matches UploadService's single-upload model.

    Windows batch execution is intentionally performed with
    shell=False. For a .bat file the caller supplies the
    existing Windows wrapper explicitly, e.g.:

        cmd.exe /d /c call maple_upload.bat ...

    This keeps argument construction in UploadService and
    process execution in this class.
    """

    def __init__(self):

        self._process: subprocess.Popen | None = None

        self._cancel_requested = False

        self._lock = threading.Lock()

    # =====================================================
    # Properties
    # =====================================================

    @property
    def is_running(self) -> bool:
        """Return True when a process is currently running."""
        with self._lock:
            return (
                self._process is not None
                and self._process.poll() is None
            )

    # =====================================================
    # Run
    # =====================================================

    def run(
        self,
        command: Sequence[str | Path],
        *,
        cwd: str | Path | None = None,
        timeout: float | None = None,
        on_output: Callable[[str], None] | None = None,
        on_error: Callable[[str], None] | None = None,
    ) -> ProcessResult:
        """
        Execute an external process.

        Parameters
        ----------
        command:
            Ordered process arguments.

        cwd:
            Working directory for the process.

        timeout:
            Maximum process runtime in seconds.

        on_output:
            Callback for each stdout line.

        on_error:
            Callback for each stderr line.

        Returns
        -------
        ProcessResult
            Process-level execution result.
        """

        command_list = [
            str(item)
            for item in command
        ]

        if not command_list:
            return ProcessResult(
                command=[],
                error="Process command cannot be empty.",
            )

        # -------------------------------------------------
        # Prevent overlapping process ownership.
        # -------------------------------------------------

        if self.is_running:
            return ProcessResult(
                command=command_list,
                error="Another process is already running.",
            )

        result = ProcessResult(
            command=command_list.copy(),
        )

        with self._lock:
            self._cancel_requested = False

        start_time = time.monotonic()

        try:

            # ---------------------------------------------
            # Working directory
            # ---------------------------------------------

            working_directory = None

            if cwd is not None:
                working_directory = str(
                    Path(cwd).resolve()
                )

            # ---------------------------------------------
            # Platform process configuration
            # ---------------------------------------------

            creation_flags = 0
            popen_kwargs = {}

            if os.name == "nt":

                # Keep the Maple console hidden while creating a
                # process group so timeout/cancel can terminate
                # cmd.exe and the Java/Maple child process.
                creation_flags = (
                    getattr(
                        subprocess,
                        "CREATE_NO_WINDOW",
                        0,
                    )
                    | getattr(
                        subprocess,
                        "CREATE_NEW_PROCESS_GROUP",
                        0,
                    )
                )

            else:

                # Equivalent process-group ownership on POSIX.
                popen_kwargs["start_new_session"] = True

            # ---------------------------------------------
            # Start process
            # ---------------------------------------------

            process = subprocess.Popen(
                command_list,

                cwd=working_directory,

                stdout=subprocess.PIPE,

                stderr=subprocess.PIPE,

                stdin=subprocess.DEVNULL,

                text=True,

                encoding="utf-8",

                errors="replace",

                bufsize=1,

                creationflags=creation_flags,

                shell=False,

                **popen_kwargs,
            )

            with self._lock:
                self._process = process

            result.started = True

            # ---------------------------------------------
            # Output buffers
            # ---------------------------------------------

            stdout_lines: list[str] = []
            stderr_lines: list[str] = []

            # ---------------------------------------------
            # stdout reader
            # ---------------------------------------------

            stdout_thread = threading.Thread(
                target=self._read_stream,
                args=(
                    process.stdout,
                    stdout_lines,
                    on_output,
                ),
                name="UB3-ProcessRunner-stdout",
                daemon=True,
            )

            # ---------------------------------------------
            # stderr reader
            # ---------------------------------------------

            stderr_thread = threading.Thread(
                target=self._read_stream,
                args=(
                    process.stderr,
                    stderr_lines,
                    on_error,
                ),
                name="UB3-ProcessRunner-stderr",
                daemon=True,
            )

            stdout_thread.start()
            stderr_thread.start()

            # ---------------------------------------------
            # Wait for process
            # ---------------------------------------------

            try:

                return_code = process.wait(
                    timeout=timeout
                )

            except subprocess.TimeoutExpired:

                result.timed_out = True

                self._terminate_process()

                return_code = process.wait()

            # ---------------------------------------------
            # Wait for stream readers
            # ---------------------------------------------

            stdout_thread.join(timeout=2)
            stderr_thread.join(timeout=2)

            # ---------------------------------------------
            # Store process result
            # ---------------------------------------------

            result.return_code = return_code

            result.stdout = "".join(
                stdout_lines
            )

            result.stderr = "".join(
                stderr_lines
            )

            with self._lock:
                result.cancelled = (
                    self._cancel_requested
                )

        except FileNotFoundError as exc:

            result.error = (
                f"Executable not found: {exc}"
            )

        except PermissionError as exc:

            result.error = (
                f"Permission denied: {exc}"
            )

        except OSError as exc:

            result.error = (
                f"Unable to start process: {exc}"
            )

        except Exception as exc:

            result.error = str(exc)

        finally:

            result.duration_seconds = (
                time.monotonic()
                - start_time
            )

            with self._lock:

                self._process = None

        return result

    # =====================================================
    # Stream Reader
    # =====================================================

    @staticmethod
    def _read_stream(
        stream,
        lines: list[str],
        callback: Callable[[str], None] | None,
    ) -> None:
        """
        Read a process stream line-by-line.

        Callback failures are intentionally isolated from the
        process reader so a GUI/logging callback cannot break
        stdout/stderr collection.
        """

        if stream is None:
            return

        try:

            for line in iter(
                stream.readline,
                "",
            ):

                if not line:
                    break

                lines.append(line)

                clean_line = line.rstrip(
                    "\r\n"
                )

                if callback is not None:

                    try:
                        callback(clean_line)

                    except Exception:
                        # Output consumers must never terminate
                        # process collection.
                        pass

        finally:

            try:
                stream.close()
            except Exception:
                pass

    # =====================================================
    # Cancel
    # =====================================================

    def cancel(self) -> bool:
        """
        Cancel the currently running process.

        Returns True only when an active process existed and
        termination was requested.
        """

        with self._lock:

            process = self._process

            if (
                process is None
                or process.poll() is not None
            ):
                return False

            self._cancel_requested = True

        return self._terminate_process(
            process=process
        )

    # =====================================================
    # Termination
    # =====================================================

    def _terminate_process(
        self,
        process: subprocess.Popen | None = None,
    ) -> bool:
        """
        Terminate the active process.

        On Windows the Maple uploader is normally launched as:

            cmd.exe
                └── maple_upload.bat
                      └── java.exe
                            └── maple_loader.jar

        Terminating only cmd.exe can leave Java running. Therefore
        Windows uses taskkill /T /F for process-tree termination.
        A normal terminate/kill fallback remains available.
        """

        if process is None:

            with self._lock:
                process = self._process

        if process is None:
            return False

        if process.poll() is not None:
            return False

        try:

            if os.name == "nt":

                # /T = terminate child processes
                # /F = force termination
                taskkill = subprocess.run(
                    [
                        "taskkill",
                        "/PID",
                        str(process.pid),
                        "/T",
                        "/F",
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    check=False,
                    creationflags=getattr(
                        subprocess,
                        "CREATE_NO_WINDOW",
                        0,
                    ),
                )

                if process.poll() is None:
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=2)

                return (
                    taskkill.returncode == 0
                    or process.poll() is not None
                )

            # POSIX process group.
            try:
                import os as _os

                _os.killpg(
                    process.pid,
                    _os.SIGTERM,
                )

                process.wait(timeout=2)

            except Exception:

                process.terminate()

                try:
                    process.wait(timeout=2)

                except subprocess.TimeoutExpired:

                    process.kill()
                    process.wait(timeout=2)

            return True

        except Exception:

            try:

                process.terminate()
                process.wait(timeout=2)

                return True

            except Exception:

                try:
                    process.kill()
                    process.wait(timeout=2)

                    return True

                except Exception:

                    return False

    # =====================================================
    # Cleanup
    # =====================================================

    def cleanup(self) -> None:
        """
        Terminate any remaining process tree.
        """

        self._terminate_process()
