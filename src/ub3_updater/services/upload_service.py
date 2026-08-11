"""
=========================================================
UB3 Firmware Updater

Upload Service

Developer:
Benjamin William

Description:
Coordinates firmware uploads using the proven Maple
Loader workflow.

Proven manual command:

    maple_upload COM3 2 1EAF:003 C:\\tmp\\firmware.bin

Important device logic:

    Maple Serial
        -> valid starting state for firmware update

    USB Serial Device
        -> bootloader/flash state
        -> NOT a valid starting state

The COM port is detected automatically by DeviceService.
The user does not manually select COM3/COM7.

Version:
0.5.7
=========================================================
"""

from __future__ import annotations

import shutil

from datetime import datetime

from pathlib import Path

from typing import Callable


from ub3_updater.models.device import (
    Device,
    DeviceState,
)

from ub3_updater.models.firmware import (
    Firmware,
)

from ub3_updater.models.upload_result import (
    UploadResult,
    UploadStatus,
)

from ub3_updater.services.device_service import (
    DeviceService,
)

from ub3_updater.services.firmware_service import (
    FirmwareService,
)

from ub3_updater.utils.process_runner import (
    ProcessResult,
    ProcessRunner,
)

from ub3_updater.services.config_service import (
    ConfigService,
)

from ub3_updater.services.maple_resource_service import (
    MapleResourceService,
)


class UploadService:
    """
    Firmware upload orchestration service.

    Responsibilities
    ----------------
    1. Validate firmware.
    2. Freshly detect the connected UB3.
    3. Verify the UB3 is in Maple Serial mode.
    4. Automatically obtain the current COM port.
    5. Prepare firmware for Maple Loader.
    6. Build the Maple Loader command.
    7. Execute the upload process.
    8. Interpret Maple Loader output.
    9. Return UploadResult.

    This service does NOT:
    - Detect devices continuously.
    - Control the GUI.
    - Manually select COM ports.
    - Put the UB3 into bootloader mode itself.
    """

    # =====================================================
    # Maple Loader Configuration
    # =====================================================

    # Maple DFU alternate interface.
    MAPLE_ALT_ID = "2"

    # Maple DFU VID:PID.
    MAPLE_DFU_ID = "1EAF:003"

    # =====================================================
    # Default Uploader
    # =====================================================

    DEFAULT_UPLOADER = (
        ConfigService.maple_uploader()
    )

    DEVELOPMENT_MAPLE_UPLOADER = Path(
        r"C:\Benon\Personal\Set_UP\Arduino"
        r"\hardware\Arduino_STM32"
        r"\Arduino_STM32-master"
        r"\tools\win"
        r"\maple_upload.bat"
    )
    # =====================================================
    # Upload Timeout
    # =====================================================

    DEFAULT_TIMEOUT = 120

    # Post-upload USB re-enumeration verification.
    #
    # This does NOT alter the Maple upload command. It only verifies
    # that the UB3 returns to normal Maple Serial operation after
    # maple_upload.bat/maple_loader.jar completes.
    POST_UPLOAD_REENUMERATION_TIMEOUT = 20.0
    POST_UPLOAD_REENUMERATION_INTERVAL = 0.25

    # =====================================================
    # Maple Success Markers
    # =====================================================

    MAPLE_SUCCESS_MARKERS = (
        "Done!",
        "Resetting USB to switch back to runtime mode",
    )

    # =====================================================
    # Maple Fatal Failure Markers
    # =====================================================

    MAPLE_FATAL_FAILURE_MARKERS = (
        "Exception in thread",
        "ArrayIndexOutOfBoundsException",
        "Starting download failed",
        "Download failed",
        "No DFU device found",
        "Couldn't find the DFU device",
        "Could not find DFU device",
        "Could not open USB device",
        "Unable to open USB device",
        "No such file or directory",
    )

    # =====================================================
    # Initialization
    # =====================================================

    def __init__(
        self,
        device_service: DeviceService | None = None,
        firmware_service: FirmwareService | None = None,
        process_runner: ProcessRunner | None = None,
        device_monitor=None,
        uploader_path: str | Path | None = None,
        timeout: float | None = None,
    ):
        """
        Initialize UploadService.
        """

        self.device_service = (
            device_service
            if device_service is not None
            else DeviceService()
        )

        self.firmware_service = (
            firmware_service
            if firmware_service is not None
            else FirmwareService()
        )

        self.process_runner = (
            process_runner
            if process_runner is not None
            else ProcessRunner()
        )

        self.device_monitor = device_monitor

        self.uploader_path = Path(
            uploader_path
            if uploader_path is not None
            else self.resolve_default_uploader()
        ).resolve()

        self.timeout = (
            timeout
            if timeout is not None
            else self.DEFAULT_TIMEOUT
        )

    # =====================================================
    # Upload
    # =====================================================

    def upload(
        self,
        firmware: Firmware,
        *,
        on_output: Callable[[str], None] | None = None,
        on_error: Callable[[str], None] | None = None,
    ) -> UploadResult:
        """
        Perform a firmware upload.

        IMPORTANT:
        A fresh device scan is performed immediately before
        every upload.

        This prevents a stale COM port from being used after
        the UB3 has been disconnected/reconnected.
        """

        started_at = datetime.now()

        # =================================================
        # 1. Validate firmware
        # =================================================

        if firmware is None:

            return UploadResult.firmware_invalid(
                "No firmware was selected."
            )

        valid, error = (
            self.firmware_service.validate(
                firmware
            )
        )

        if not valid:

            return UploadResult.firmware_invalid(
                error,
                firmware_name=firmware.name,
                firmware_version=firmware.version,
                firmware_path=firmware.path,
            )

        # =================================================
        # 2. FRESHLY DETECT CURRENT UB3
        # =================================================

        """
        Do NOT use:

            get_current_device()

        as the primary source here.

        The COM port may have changed since the previous
        detection.

        Example:

            Previous:
                Maple Serial -> COM3

            Disconnect

            Reconnect:
                Maple Serial -> COM7

        The upload must use COM7.

        Therefore every upload performs a fresh scan.
        """

        device = self.device_service.scan()

        # =================================================
        # 3. Validate freshly detected device
        # =================================================

        validation_error = (
            self._validate_device(device)
        )

        if validation_error:

            return UploadResult.device_not_ready(
                validation_error,
                firmware_name=firmware.name,
                firmware_version=firmware.version,
                firmware_path=firmware.path,
                com_port=(
                    device.com_port
                    if device is not None
                    else ""
                ),
                device_state=self._state_value(
                    device
                ),
            )

        # =================================================
        # 4. Validate uploader
        # =================================================

        uploader_error = (
            self._validate_uploader()
        )

        if uploader_error:

            return UploadResult.process_error(
                uploader_error,
                firmware_name=firmware.name,
                firmware_version=firmware.version,
                firmware_path=firmware.path,
                com_port=device.com_port,
                device_state=self._state_value(
                    device
                ),
            )

        # =================================================
        # 5. Build command
        # =================================================

        try:

            command = self.build_command(
                device=device,
                firmware=firmware,
            )

        except FileNotFoundError as exc:

            return UploadResult.process_error(
                str(exc),
                firmware_name=firmware.name,
                firmware_version=firmware.version,
                firmware_path=firmware.path,
                com_port=device.com_port,
                device_state=self._state_value(
                    device
                ),
            )

        except OSError as exc:

            return UploadResult.process_error(
                (
                    "Unable to prepare firmware for "
                    f"upload: {exc}"
                ),
                firmware_name=firmware.name,
                firmware_version=firmware.version,
                firmware_path=firmware.path,
                com_port=device.com_port,
                device_state=self._state_value(
                    device
                ),
            )

        except ValueError as exc:

            return UploadResult.process_error(
                str(exc),
                firmware_name=firmware.name,
                firmware_version=firmware.version,
                firmware_path=firmware.path,
                com_port=device.com_port,
                device_state=self._state_value(
                    device
                ),
            )

        # =================================================
        # 6. Pause DeviceMonitor
        # =================================================

        self._pause_monitor()

        try:

            process_result = (
                self.process_runner.run(
                    command,
                    cwd=self.uploader_path.parent,
                    timeout=self.timeout,
                    on_output=on_output,
                    on_error=on_error,
                )
            )

        finally:

            # Always restore monitoring.
            self._resume_monitor()

        # =================================================
        # 7. Build UploadResult
        # =================================================

        return self._build_upload_result(
            process_result=process_result,
            firmware=firmware,
            device=device,
            started_at=started_at,
            on_output=on_output,
        )

    # =====================================================
    # Prepare Firmware
    # =====================================================

    def _prepare_firmware(
        self,
        firmware: Firmware,
    ) -> Path:
        """
        Resolve and validate the selected firmware file.

        The production firmware source is the project firmware
        repository managed by FirmwareService:

            resources/firmware/<package>/<firmware>.bin

        The previous C:\\tmp staging directory was only used for
        the manual CMD workflow and is not part of the application
        runtime architecture.

        No copy is created here. The original repository firmware
        path is passed to Maple Loader.
        """

        if firmware is None:

            raise ValueError(
                "Firmware is required."
            )

        if not firmware.path:

            raise ValueError(
                "Firmware path is required."
            )

        source = Path(
            firmware.path
        ).resolve()

        if not source.exists():

            raise FileNotFoundError(
                "Firmware file not found: "
                f"{source}"
            )

        if not source.is_file():

            raise OSError(
                "Firmware path is not a file: "
                f"{source}"
            )

        return source

    # =====================================================
    # Build Command
    # =====================================================

    def build_command(
        self,
        device: Device,
        firmware: Firmware,
    ) -> list[str]:
        """
        Build the Maple Loader command.

        Proven Maple command:

            maple_upload COM3 2 1EAF:003 <firmware>

        The firmware argument is the selected binary from the
        project firmware repository. C:\\tmp was only the staging
        location used during earlier manual CMD testing.

        Application representation:

            [0] cmd.exe
            [1] /d
            [2] /c
            [3] call
            [4] maple_upload.bat
            [5] COM3
            [6] 2
            [7] 1EAF:003
            [8] resources/firmware/<package>/<firmware>.bin

        COM port is obtained from the freshly detected
        Device object.
        """

        # -------------------------------------------------
        # Validate device
        # -------------------------------------------------

        if device is None:

            raise ValueError(
                "Device is required."
            )

        if not device.com_port:

            raise ValueError(
                "Device COM port is required."
            )

        # -------------------------------------------------
        # Validate firmware
        # -------------------------------------------------

        if firmware is None:

            raise ValueError(
                "Firmware is required."
            )

        if not firmware.path:

            raise ValueError(
                "Firmware path is required."
            )

        # -------------------------------------------------
        # Resolve selected firmware from the repository
        # -------------------------------------------------

        upload_firmware = (
            self._prepare_firmware(
                firmware
            )
        )

        # -------------------------------------------------
        # Resolve uploader
        # -------------------------------------------------

        uploader = (
            self.uploader_path.resolve()
        )

        if not uploader.exists():

            raise FileNotFoundError(
                "Maple uploader not found: "
                f"{uploader}"
            )

        if not uploader.is_file():

            raise OSError(
                "Maple uploader path is not a file: "
                f"{uploader}"
            )

        # -------------------------------------------------
        # Build Windows argument list
        # -------------------------------------------------

        return [
            "cmd.exe",
            "/d",
            "/c",
            "call",
            str(uploader),
            device.com_port,
            self.MAPLE_ALT_ID,
            self.MAPLE_DFU_ID,
            str(upload_firmware),
        ]

    # =====================================================
    # Device Validation
    # =====================================================

    @staticmethod
    def _validate_device(
        device: Device | None,
    ) -> str | None:
        """
        Validate that the freshly detected device is ready.

        Valid starting state:

            Maple Serial

        Invalid starting state:

            USB Serial Device
        """

        # -------------------------------------------------
        # No device
        # -------------------------------------------------

        if device is None:

            return (
                "No UB3 device detected."
            )

        # -------------------------------------------------
        # Disconnected
        # -------------------------------------------------

        if not device.connected:

            return (
                "No UB3 device is connected."
            )

        # -------------------------------------------------
        # Maple Serial
        # -------------------------------------------------

        if device.state == DeviceState.MAPLE_SERIAL:

            if not device.com_port:

                return (
                    "UB3 COM port could not be determined."
                )

            return None

        # -------------------------------------------------
        # USB Serial / Bootloader
        # -------------------------------------------------

        if device.state == DeviceState.USB_SERIAL:

            return (
                "UB3 is in flash/bootloader mode. "
                "Firmware update must start from "
                "Maple Serial mode."
            )

        # -------------------------------------------------
        # Unknown state
        # -------------------------------------------------

        return (
            "UB3 is not in Maple Serial mode."
        )

    # =====================================================
    # Uploader Validation
    # =====================================================

    def _validate_uploader(self) -> str | None:
        """
        Verify the Maple uploader and, when using the bundled
        project runtime, verify the complete Maple resource set.

        The production uploader is resolved from:

            resources/tools/maple/

        A caller may still inject another uploader_path for
        controlled tests or development integration tests.
        """

        if not self.uploader_path.exists():

            return (
                "Maple uploader was not found: "
                f"{self.uploader_path}"
            )

        if not self.uploader_path.is_file():

            return (
                "Maple uploader path is not a file: "
                f"{self.uploader_path}"
            )

        # -------------------------------------------------
        # Bundled runtime validation
        # -------------------------------------------------

        configured_uploader = (
            ConfigService.maple_uploader()
            .resolve()
        )

        if self.uploader_path == configured_uploader:

            validation = (
                MapleResourceService(
                    resource_root=configured_uploader.parent
                ).validate()
            )

            if not validation.valid:

                details = ""

                if validation.missing_files:

                    details = (
                        " Missing: "
                        + ", ".join(
                            validation.missing_files
                        )
                    )

                return (
                    "Bundled Maple Loader runtime is "
                    f"incomplete.{details}"
                )

        return None

    # =====================================================
    # Device Monitor Pause
    # =====================================================

    def _pause_monitor(self) -> None:
        """
        Pause DeviceMonitor while Maple Loader is operating.
        """

        if self.device_monitor is None:

            return

        pause = getattr(
            self.device_monitor,
            "pause",
            None,
        )

        if callable(pause):

            pause()

    # =====================================================
    # Device Monitor Resume
    # =====================================================

    def _resume_monitor(self) -> None:
        """
        Resume DeviceMonitor after Maple Loader finishes.
        """

        if self.device_monitor is None:

            return

        resume = getattr(
            self.device_monitor,
            "resume",
            None,
        )

        if callable(resume):

            resume()

    # =====================================================
    # Build Upload Result
    # =====================================================

    def _build_upload_result(
        self,
        process_result: ProcessResult,
        firmware: Firmware,
        device: Device,
        started_at: datetime,
        on_output: Callable[[str], None] | None = None,
    ) -> UploadResult:
        """
        Convert ProcessResult into UploadResult.

        Maple Loader output is interpreted separately from
        the operating-system process result.
        """

        completed_at = datetime.now()

        common = {
            "firmware_name": firmware.name,
            "firmware_version": firmware.version,
            "firmware_path": firmware.path,
            "com_port": device.com_port,
            "device_state": self._state_value(device),
            "command": process_result.command,
            "return_code": process_result.return_code,
            "stdout": process_result.stdout,
            "stderr": process_result.stderr,
            "started": process_result.started,
            "started_at": started_at,
            "completed_at": completed_at,
            "duration_seconds": (
                process_result.duration_seconds
            ),
        }

        # =================================================
        # Cancelled
        # =================================================

        if process_result.cancelled:

            return UploadResult.cancelled_result(
                "Firmware upload was cancelled.",
                **common,
            )

        # =================================================
        # Timeout
        # =================================================

        if process_result.timed_out:

            return UploadResult.timeout_result(
                (
                    "Firmware upload exceeded the "
                    f"{self.timeout}-second timeout."
                ),
                **common,
            )

        # =================================================
        # Process startup error
        # =================================================

        if process_result.error:

            return UploadResult.process_error(
                process_result.error,
                **common,
            )

        # =================================================
        # Interpret Maple Loader
        # =================================================

        status, message, warning = (
            self._evaluate_maple_result(
                process_result
            )
        )

        # =================================================
        # Post-upload runtime verification
        # =================================================
        #
        # Maple Loader remains responsible for the actual
        # DTR -> DFU -> download -> reset sequence.
        #
        # We only verify:
        #
        #     DFU -> USB reconnect -> Maple Serial
        #
        # No alternative uploader or DFU implementation is used.

        transfer_completed = (
            self._maple_transfer_completed(
                process_result
            )
        )

        if transfer_completed:

            runtime_device = (
                self._wait_for_maple_serial(
                    timeout=(
                        self.POST_UPLOAD_REENUMERATION_TIMEOUT
                    ),
                    interval=(
                        self.POST_UPLOAD_REENUMERATION_INTERVAL
                    ),
                    on_output=on_output,
                )
            )

            if runtime_device is not None:

                common["com_port"] = (
                    runtime_device.com_port
                )

                common["device_state"] = (
                    self._state_value(
                        runtime_device
                    )
                )

                return UploadResult.success_result(
                    message=(
                        "Firmware upload completed successfully. "
                        "UB3 returned to Maple Serial mode "
                        f"on {runtime_device.com_port}."
                    ),
                    **common,
                )

            return UploadResult.success_with_warning_result(
                message=(
                    "Firmware transfer completed successfully, "
                    "but the UB3 did not return to Maple Serial "
                    "mode within "
                    f"{self.POST_UPLOAD_REENUMERATION_TIMEOUT:.0f} "
                    "seconds."
                ),
                warning=(
                    "The Maple upload command was executed without "
                    "changing its parameters. The firmware download "
                    "completed, but Windows did not detect the UB3 "
                    "again in normal Maple Serial mode. Check the "
                    "USB connection/device state before continuing."
                ),
                **common,
            )

        if status == UploadStatus.SUCCESS:

            return UploadResult.success_result(
                message=message,
                **common,
            )

        if (
            status
            == UploadStatus.SUCCESS_WITH_WARNING
        ):

            return UploadResult.success_with_warning_result(
                message=message,
                warning=warning,
                **common,
            )

        return UploadResult.failed_result(
            message,
            **common,
        )


    # =====================================================
    # Maple Transfer Detection
    # =====================================================

    @staticmethod
    def _maple_transfer_completed(
        process_result: ProcessResult,
    ) -> bool:
        """
        Return True when Maple Loader reached the firmware
        download completion point.
        """

        output = (
            (process_result.stdout or "")
            + "\n"
            + (process_result.stderr or "")
        ).lower()

        return (
            "starting download:" in output
            and "finished!" in output
        )

    # =====================================================
    # Post-upload Maple Serial Verification
    # =====================================================

    def _wait_for_maple_serial(
        self,
        *,
        timeout: float,
        interval: float,
        on_output: Callable[[str], None] | None = None,
    ) -> Device | None:
        """
        Wait for the UB3 to re-enumerate in normal Maple Serial
        mode after Maple Loader completes.

        This performs fresh DeviceService scans only. It does not
        manipulate USB, send DFU commands, reset the board, or
        change the Maple upload command.
        """

        import time

        deadline = (
            time.monotonic()
            + max(0.0, timeout)
        )

        last_state = None

        if on_output is not None:
            try:
                on_output(
                    "Verifying UB3 USB re-enumeration..."
                )
            except Exception:
                pass

        while time.monotonic() <= deadline:

            device = self.device_service.scan()

            if (
                device is not None
                and device.connected
                and device.state
                == DeviceState.MAPLE_SERIAL
                and device.com_port
            ):
                if on_output is not None:
                    try:
                        on_output(
                            "UB3 returned to Maple Serial "
                            f"mode on {device.com_port}."
                        )
                    except Exception:
                        pass

                return device

            current_state = (
                self._state_value(device)
                if device is not None
                else ""
            )

            if (
                current_state
                and current_state != last_state
                and on_output is not None
            ):
                try:
                    on_output(
                        "Waiting for UB3 runtime USB "
                        f"re-enumeration: {current_state}"
                    )
                except Exception:
                    pass

            last_state = current_state

            remaining = (
                deadline
                - time.monotonic()
            )

            if remaining <= 0:
                break

            time.sleep(
                min(
                    max(0.01, interval),
                    remaining,
                )
            )

        if on_output is not None:
            try:
                on_output(
                    "UB3 did not return to Maple Serial "
                    "mode within the post-upload timeout."
                )
            except Exception:
                pass

        return None

    # =====================================================
    # Maple Result Evaluation
    # =====================================================

    def _evaluate_maple_result(
        self,
        process_result: ProcessResult,
    ) -> tuple[UploadStatus, str, str]:
        """
        Interpret Maple Loader output.

        Returns
        -------
        tuple
            (
                status,
                message,
                warning
            )

        Important:
        ----------
        Process return code 0 alone is NOT enough.

        Maple Loader can return 0 while reporting a Java
        exception or another fatal failure.

        Likewise, a USB reset error occurring AFTER
        "Done!" does not mean the firmware transfer failed.
        """

        stdout = (
            process_result.stdout
            or ""
        )

        stderr = (
            process_result.stderr
            or ""
        )

        output = (
            stdout
            + "\n"
            + stderr
        )

        output_lower = (
            output.lower()
        )

        # =================================================
        # 1. Fatal failure detection
        # =================================================

        for marker in (
            self.MAPLE_FATAL_FAILURE_MARKERS
        ):

            if marker.lower() in output_lower:

                return (
                    UploadStatus.FAILED,

                    (
                        "Maple Loader reported a fatal "
                        f"failure: {marker}"
                    ),

                    "",
                )

        # =================================================
        # 2. Detect successful firmware transfer
        # =================================================

        # Maple Loader's actual transfer-completion line is:
        #
        #     Starting download: [...] finished!
        #
        # "Done!" normally follows it, but the Java/USB reset path
        # can terminate before that final informational line is
        # flushed. The transfer itself is already complete when
        # the download line reaches "finished!".
        download_finished = (
            "starting download:"
            in output_lower
            and "finished!"
            in output_lower
        )

        done_found = (
            "done!"
            in output_lower
        )

        # =================================================
        # 3. Detect post-upload reset warning
        # =================================================

        # "Resetting USB to switch back to runtime mode" is a
        # normal Maple Loader completion message. It must NOT be
        # interpreted as a warning by itself.
        #
        # Only an actual reset error is a warning.
        reset_warning = (
            "error resetting after download"
            in output_lower
            or
            "usb_reset:"
            in output_lower
            or
            "could not reset device"
            in output_lower
            or
            "reset via usb serial failed"
            in output_lower
            or
            "failed to reset"
            in output_lower
        )

        # =================================================
        # 4. Successful transfer
        # =================================================

        if download_finished:

            # -------------------------------------------------
            # Successful transfer + reset warning
            #
            # A missing "Done!" line is not treated as a failed
            # firmware write when the download itself reached
            # "finished!". This is important because Maple Loader
            # can enter its USB reset/re-enumeration path before
            # flushing the final "Done!" text.
            # -------------------------------------------------

            if reset_warning or not done_found:

                return (
                    UploadStatus.SUCCESS_WITH_WARNING,

                    (
                        "Firmware was programmed successfully."
                    ),

                    (
                        "Firmware programming completed, "
                        "but Maple Loader did not complete "
                        "the automatic USB runtime reset. "
                        "The UB3 may require reconnection."
                    ),
                )

            # -------------------------------------------------
            # Completely successful
            # -------------------------------------------------

            return (
                UploadStatus.SUCCESS,

                (
                    "Firmware upload completed successfully."
                ),

                "",
            )

        # =================================================
        # 5. Non-zero process exit
        # =================================================

        if process_result.return_code not in (
            None,
            0,
        ):

            message = (
                "Maple firmware uploader failed "
                f"with exit code "
                f"{process_result.return_code}."
            )

            if stderr.strip():

                message = stderr.strip()

            return (
                UploadStatus.FAILED,
                message,
                "",
            )

        # =================================================
        # 6. No confirmed success
        # =================================================

        return (
            UploadStatus.FAILED,

            (
                "Maple Loader did not report a confirmed "
                "successful firmware update."
            ),

            "",
        )

    #=========================
    # Cancel Upload
    # =====================================================

    def cancel(self) -> bool:
        """
        Cancel the active upload process.
        """

        return self.process_runner.cancel()

    # =====================================================
    # State Helper
    # =====================================================

    @staticmethod
    def _state_value(
        device: Device | None,
    ) -> str:
        """
        Convert DeviceState to a string.
        """

        if device is None:

            return ""

        state = device.state

        if hasattr(
            state,
            "value",
        ):

            return state.value

        return str(state)

    # =====================================================
    # Default Uploader Resolution
    # =====================================================

    @classmethod
    def resolve_default_uploader(cls) -> Path:
        """
        Resolve the production Maple uploader from the bundled
        project resources.

        The previous development Arduino installation is not used
        as a runtime fallback. It was only part of manual/development
        testing and must not become a deployment dependency.
        """

        return (
            ConfigService.maple_uploader()
            .resolve()
        )
