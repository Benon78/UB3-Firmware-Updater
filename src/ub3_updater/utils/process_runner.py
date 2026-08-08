"""
=========================================================
UB3 Firmware Updater

Process Runner

Developer:
Benjamin William

Description:
Controlled Windows process execution for the UB3 updater.

This module is responsible for running external tools
such as the Maple/Arduino firmware uploader.

Responsibilities
----------------
• Start an external process
• Pass command-line arguments
• Capture stdout/stderr
• Stream process output
• Handle timeout
• Handle cancellation
• Return process results

This module does NOT:
• Detect USB devices
• Validate firmware
• Decide whether an upload should start
• Control the GUI
• Interpret Maple Loader output

Version:
0.5.0
=========================================================
"""

from __future__ import annotations

import subprocess
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Sequence


# =========================================================
# Process Result
# =========================================================

@dataclass(slots=True)
class ProcessResult:
    """
    Result returned after an external process finishes.
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
        """
        Return True only when the process completed
        successfully.
        """

        return (
            self.started
            and not self.timed_out
            and not self.cancelled
            and not self.error
            and self.return_code == 0
        )

    @property
    def failed(self) -> bool:

        return self.started and not self.success


# =========================================================
# Process Runner
# =========================================================

class ProcessRunner:
    """
    Controlled process runner used by the upload layer.
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
        """
        Return True when a process is currently running.
        """

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
        Execute an external process and wait for completion.

        Parameters
        ----------
        command:
            Complete command and arguments.

        cwd:
            Working directory for the process.

        timeout:
            Maximum execution time in seconds.
            None means no timeout.

        on_output:
            Callback invoked for each stdout line.

        on_error:
            Callback invoked for each stderr line.
        """

        command_list = [
            str(item)
            for item in command
        ]

        result = ProcessResult(
            command=command_list,
        )

        self._cancel_requested = False

        start_time = __import__("time").monotonic()

        try:

            working_directory = None

            if cwd is not None:

                working_directory = str(
                    Path(cwd).resolve()
                )

            # -----------------------------------------
            # Windows subprocess
            # -----------------------------------------

            creation_flags = 0

            if hasattr(
                subprocess,
                "CREATE_NO_WINDOW",
            ):

                creation_flags = (
                    subprocess.CREATE_NO_WINDOW
                )

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
            )

            with self._lock:

                self._process = process

            result.started = True

            # -----------------------------------------
            # Output collection
            # -----------------------------------------

            stdout_lines: list[str] = []

            stderr_lines: list[str] = []

            stdout_thread = threading.Thread(
                target=self._read_stream,
                args=(
                    process.stdout,
                    stdout_lines,
                    on_output,
                ),
                daemon=True,
            )

            stderr_thread = threading.Thread(
                target=self._read_stream,
                args=(
                    process.stderr,
                    stderr_lines,
                    on_error,
                ),
                daemon=True,
            )

            stdout_thread.start()

            stderr_thread.start()

            # -----------------------------------------
            # Wait
            # -----------------------------------------

            try:

                return_code = process.wait(
                    timeout=timeout
                )

            except subprocess.TimeoutExpired:

                result.timed_out = True

                self._terminate_process()

                return_code = process.wait()

            # -----------------------------------------
            # Threads
            # -----------------------------------------

            stdout_thread.join(timeout=2)

            stderr_thread.join(timeout=2)

            result.return_code = return_code

            result.stdout = "".join(stdout_lines)

            result.stderr = "".join(stderr_lines)

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
                __import__("time").monotonic()
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

                clean_line = line.rstrip("\r\n")

                if callback is not None:

                    callback(clean_line)

        finally:

            stream.close()

    # =====================================================
    # Cancel
    # =====================================================

    def cancel(self) -> bool:
        """
        Request cancellation of the running process.

        Returns True when a running process was terminated.
        """

        self._cancel_requested = True

        return self._terminate_process()

    # =====================================================
    # Termination
    # =====================================================

    def _terminate_process(self) -> bool:

        with self._lock:

            process = self._process

        if process is None:

            return False

        if process.poll() is not None:

            return False

        try:

            process.terminate()

            try:

                process.wait(timeout=2)

            except subprocess.TimeoutExpired:

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
        Terminate any remaining process.
        """

        self._terminate_process()