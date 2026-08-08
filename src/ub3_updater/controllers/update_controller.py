"""
=========================================================
UB3 Firmware Updater

Update Controller

Purpose
-------
Application-layer coordinator for the firmware update
workflow.

Responsibilities
----------------
• Coordinate DeviceMonitor
• Track the currently detected UB3
• Track selected firmware
• Determine whether an update can start
• Start UploadWorker
• Receive UploadWorker callbacks
• Expose application-level status
• Handle device connection/disconnection
• Return the application to a ready/waiting state
  after an upload
• Support continuous UB3 processing

This controller does NOT:

• Detect USB devices directly
• Execute maple_upload.bat
• Run subprocesses
• Validate firmware internals
• Control GUI widgets
• Implement USB communication

Architecture
------------

GUI
 │
 ▼
UpdateController
 │
 ├── DeviceMonitor
 ├── FirmwareService
 └── UploadWorker
       │
       ▼
   UploadService
       │
       ▼
   ProcessRunner
       │
       ▼
 maple_upload.bat

Version:
0.1.0
=========================================================
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable

from ub3_updater.models.device import Device
from ub3_updater.models.firmware import Firmware
from ub3_updater.models.upload_result import UploadResult
from ub3_updater.workers.upload_worker import (
    UploadWorker,
    UploadWorkerState,
)


# =========================================================
# Controller State
# =========================================================

class UpdateControllerState(Enum):
    """
    High-level application state used by the GUI.
    """

    WAITING_FOR_DEVICE = "Waiting for UB3"

    DEVICE_CONNECTED = "UB3 Connected"

    READY = "Ready to Update"

    UPLOADING = "Uploading Firmware"

    SUCCESS = "Firmware Updated Successfully"

    SUCCESS_WITH_WARNING = "Firmware Updated With Warning"

    FAILED = "Update Failed"

    CANCELLED = "Update Cancelled"

    ERROR = "Application Error"


# =========================================================
# Update Controller
# =========================================================

class UpdateController:
    """
    Coordinates the complete firmware-update workflow.
    """

    # =====================================================
    # Initialization
    # =====================================================

    def __init__(
        self,
        device_monitor=None,
        firmware_service=None,
        upload_worker: UploadWorker | None = None,
    ):
        """
        Parameters
        ----------
        device_monitor:
            Existing DeviceMonitor instance.

        firmware_service:
            Existing FirmwareService instance.

        upload_worker:
            Existing UploadWorker instance.

        All dependencies are injectable so the controller
        can be tested without physical hardware.
        """

        self.device_monitor = device_monitor

        self.firmware_service = (
            firmware_service
            if firmware_service is not None
            else self._create_firmware_service()
        )

        self.upload_worker = (
            upload_worker
            if upload_worker is not None
            else self._create_upload_worker()
        )

        # -------------------------------------------------
        # Runtime state
        # -------------------------------------------------

        self.state = (
            UpdateControllerState.WAITING_FOR_DEVICE
        )

        self.device: Device | None = None

        self.selected_firmware: Firmware | None = None

        self.last_result: UploadResult | None = None

        self.last_error: Exception | None = None

        self.status_message = (
            "Waiting for UB3"
        )

        self._started = False

        # -------------------------------------------------
        # Callbacks
        # -------------------------------------------------

        self._on_state_changed: Callable[
            [UpdateControllerState],
            None,
        ] | None = None

        self._on_device_changed: Callable[
            [Device],
            None,
        ] | None = None

        self._on_status: Callable[
            [str],
            None,
        ] | None = None

        self._on_output: Callable[
            [str],
            None,
        ] | None = None

        self._on_error: Callable[
            [str],
            None,
        ] | None = None

        self._on_result: Callable[
            [UploadResult],
            None,
        ] | None = None

        # -------------------------------------------------
        # Connect worker callbacks
        # -------------------------------------------------

        self._configure_worker()

        # -------------------------------------------------
        # Connect monitor callbacks
        # -------------------------------------------------

        self._connect_monitor()

    # =====================================================
    # Dependency Creation
    # =====================================================

    @staticmethod
    def _create_firmware_service():

        from ub3_updater.services.firmware_service import (
            FirmwareService,
        )

        return FirmwareService()

    @staticmethod
    def _create_upload_worker():

        from ub3_updater.services.upload_service import (
            UploadService,
        )

        return UploadWorker(
            upload_service=UploadService()
        )

    # =====================================================
    # Worker Configuration
    # =====================================================

    def _configure_worker(self) -> None:
        """
        Connect UploadWorker callbacks.

        The worker implementation already provides the
        callback configuration used by the worker tests.
        """

        configure = getattr(
            self.upload_worker,
            "configure_callbacks",
            None,
        )

        if callable(configure):

            configure(
                on_state_changed=self._handle_worker_state,
                on_progress=self._handle_worker_progress,
                on_completed=self._handle_worker_completed,
                on_error=self._handle_worker_error,
            )

            return

        # -------------------------------------------------
        # Fallback for individual callback APIs
        # -------------------------------------------------

        self._set_worker_callback(
            "set_on_state_changed",
            self._handle_worker_state,
        )

        self._set_worker_callback(
            "set_on_progress",
            self._handle_worker_progress,
        )

        self._set_worker_callback(
            "set_on_completed",
            self._handle_worker_completed,
        )

        self._set_worker_callback(
            "set_on_error",
            self._handle_worker_error,
        )

        self._set_worker_callback(
            "set_on_output",
            self._handle_worker_output,
        )

    def _set_worker_callback(
        self,
        method_name: str,
        callback,
    ) -> None:

        method = getattr(
            self.upload_worker,
            method_name,
            None,
        )

        if callable(method):

            method(callback)

    # =====================================================
    # Monitor Configuration
    # =====================================================

    def _connect_monitor(self) -> None:
        """
        Connect DeviceMonitor signals when available.

        The controller deliberately supports a monitor with
        Qt signals without importing Qt itself.
        """

        if self.device_monitor is None:

            return

        self._connect_signal(
            "device_changed",
            self._handle_device_changed,
        )

        self._connect_signal(
            "device_connected",
            self._handle_device_connected,
        )

        self._connect_signal(
            "device_disconnected",
            self._handle_device_disconnected,
        )

    def _connect_signal(
        self,
        signal_name: str,
        callback,
    ) -> None:

        signal = getattr(
            self.device_monitor,
            signal_name,
            None,
        )

        if signal is None:

            return

        connect = getattr(
            signal,
            "connect",
            None,
        )

        if callable(connect):

            connect(callback)

    # =====================================================
    # Callback Configuration
    # =====================================================

    def set_on_state_changed(
        self,
        callback: Callable[
            [UpdateControllerState],
            None,
        ] | None,
    ) -> None:

        self._on_state_changed = callback

    def set_on_device_changed(
        self,
        callback: Callable[
            [Device],
            None,
        ] | None,
    ) -> None:

        self._on_device_changed = callback

    def set_on_status(
        self,
        callback: Callable[
            [str],
            None,
        ] | None,
    ) -> None:

        self._on_status = callback

    def set_on_output(
        self,
        callback: Callable[
            [str],
            None,
        ] | None,
    ) -> None:

        self._on_output = callback

    def set_on_error(
        self,
        callback: Callable[
            [str],
            None,
        ] | None,
    ) -> None:

        self._on_error = callback

    def set_on_result(
        self,
        callback: Callable[
            [UploadResult],
            None,
        ] | None,
    ) -> None:

        self._on_result = callback

    # =====================================================
    # Lifecycle
    # =====================================================

    def start(self) -> None:
        """
        Start the controller and device monitoring.
        """

        if self._started:

            return

        self._started = True

        self._set_state(
            UpdateControllerState.WAITING_FOR_DEVICE,
            "Waiting for UB3",
        )

        if self.device_monitor is not None:

            start = getattr(
                self.device_monitor,
                "start",
                None,
            )

            if callable(start):

                start()

    def stop(self) -> None:
        """
        Stop device monitoring.

        A running upload is not forcibly cancelled here.
        """

        if not self._started:

            return

        if self.device_monitor is not None:

            stop = getattr(
                self.device_monitor,
                "stop",
                None,
            )

            if callable(stop):

                stop()

        self._started = False

    # =====================================================
    # Device Refresh
    # =====================================================

    def refresh_device(self) -> Device | None:
        """
        Force an immediate device scan.

        Useful for the GUI Refresh button.
        """

        if self.device_monitor is not None:

            service = getattr(
                self.device_monitor,
                "service",
                None,
            )

            if service is not None:

                scan = getattr(
                    service,
                    "scan",
                    None,
                )

                if callable(scan):

                    device = scan()

                    self._handle_device_changed(
                        device
                    )

                    return device

        return self.device

    # =====================================================
    # Firmware Selection
    # =====================================================

    def select_firmware(
        self,
        firmware: Firmware | None,
    ) -> bool:
        """
        Select firmware for the next upload.

        Returns
        -------
        bool
            True when the firmware is accepted.
        """

        if self.is_uploading:

            return False

        if firmware is None:

            self.selected_firmware = None

            self._update_ready_state()

            return False

        self.selected_firmware = firmware

        self.last_error = None

        self._update_ready_state()

        return True

    # =====================================================
    # Firmware Access
    # =====================================================

    def get_available_firmware(
        self,
    ) -> list[Firmware]:
        """
        Return available firmware packages.

        The method intentionally supports the existing
        FirmwareService without forcing a specific internal
        discovery API.
        """

        service = self.firmware_service

        for method_name in (
            "get_available",
            "get_all",
            "discover",
            "list_firmware",
            "list",
        ):

            method = getattr(
                service,
                method_name,
                None,
            )

            if not callable(method):

                continue

            result = method()

            if result is None:

                return []

            if isinstance(
                result,
                list,
            ):

                return result

            return list(result)

        return []

    # =====================================================
    # Update Availability
    # =====================================================

    @property
    def is_uploading(self) -> bool:
        """
        Return True while UploadWorker is running.
        """

        worker_running = getattr(
            self.upload_worker,
            "is_running",
            False,
        )

        if callable(worker_running):

            worker_running = worker_running()

        return bool(
            worker_running
        )

    @property
    def can_update(self) -> bool:
        """
        Return whether the Update button should be enabled.
        """

        if self.is_uploading:

            return False

        if self.device is None:

            return False

        if not self.device.connected:

            return False

        if not self._is_update_ready_device(
            self.device
        ):

            return False

        if self.selected_firmware is None:

            return False

        return True

    # =====================================================
    # Update
    # =====================================================

    def update(self) -> bool:
        """
        Start a firmware update.

        Returns
        -------
        bool
            True if the UploadWorker accepted the job.
        """

        # -------------------------------------------------
        # Already running
        # -------------------------------------------------

        if self.is_uploading:

            self._emit_error(
                "A firmware update is already running."
            )

            return False

        # -------------------------------------------------
        # Device
        # -------------------------------------------------

        if self.device is None:

            self._set_state(
                UpdateControllerState.WAITING_FOR_DEVICE,
                "Waiting for UB3",
            )

            self._emit_error(
                "No UB3 device is connected."
            )

            return False

        if not self.device.connected:

            self._set_state(
                UpdateControllerState.WAITING_FOR_DEVICE,
                "Waiting for UB3",
            )

            self._emit_error(
                "No UB3 device is connected."
            )

            return False

        # -------------------------------------------------
        # Device state
        # -------------------------------------------------

        if not self._is_update_ready_device(
            self.device
        ):

            self._emit_error(
                "UB3 must be connected in Maple Serial mode."
            )

            return False

        # -------------------------------------------------
        # Firmware
        # -------------------------------------------------

        if self.selected_firmware is None:

            self._emit_error(
                "No firmware has been selected."
            )

            return False

        # -------------------------------------------------
        # Clear previous result
        # -------------------------------------------------

        self.last_result = None

        self.last_error = None

        # -------------------------------------------------
        # Update state
        # -------------------------------------------------

        self._set_state(
            UpdateControllerState.UPLOADING,
            "Uploading Firmware...",
        )

        # -------------------------------------------------
        # Start worker
        # -------------------------------------------------

        try:

            started = self.upload_worker.start(
                self.selected_firmware
            )

        except Exception as exc:

            self.last_error = exc

            self._set_state(
                UpdateControllerState.ERROR,
                str(exc),
            )

            self._emit_error(
                str(exc)
            )

            return False

        if not started:

            self._set_state(
                UpdateControllerState.READY,
                "Ready to Update",
            )

            self._emit_error(
                "Upload worker could not start."
            )

            return False

        return True

    # =====================================================
    # Cancel
    # =====================================================

    def cancel(self) -> bool:
        """
        Cancel a running upload.
        """

        if not self.is_uploading:

            return False

        cancel = getattr(
            self.upload_worker,
            "cancel",
            None,
        )

        if not callable(cancel):

            self._emit_error(
                "Upload cancellation is not available."
            )

            return False

        return bool(
            cancel()
        )

    # =====================================================
    # Reset
    # =====================================================

    def reset_worker(self) -> bool:
        """
        Reset the worker after a completed job.

        This does not disconnect or change the current
        device.
        """

        if self.is_uploading:

            return False

        reset = getattr(
            self.upload_worker,
            "reset",
            None,
        )

        if not callable(reset):

            return False

        result = bool(
            reset()
        )

        if result:

            self.last_result = None

            self.last_error = None

            self._update_ready_state()

        return result

    # =====================================================
    # Device Events
    # =====================================================

    def _handle_device_connected(
        self,
        device: Device,
    ) -> None:

        self.device = device

        self.last_error = None

        if self._on_device_changed is not None:

            self._on_device_changed(
                device
            )

        if self.is_uploading:

            return

        if self._is_update_ready_device(
            device
        ):

            self._set_state(
                UpdateControllerState.DEVICE_CONNECTED,
                f"UB3 Connected - {device.com_port}",
            )

            self._update_ready_state()

        else:

            self._set_state(
                UpdateControllerState.DEVICE_CONNECTED,
                "UB3 Connected",
            )

    def _handle_device_disconnected(
        self,
    ) -> None:
        """
        Handle physical UB3 removal.

        A disconnected device must never remain as the
        controller's active device.
        """

        self.device = None

        # -----------------------------------------------------
        # Notify GUI/application
        # -----------------------------------------------------

        if self._on_device_changed is not None:

            self._on_device_changed(
                None
            )

        # -----------------------------------------------------
        # Do not interrupt an active upload.
        #
        # Maple firmware programming temporarily changes USB
        # state, so the upload worker remains authoritative
        # until it returns its UploadResult.
        # -----------------------------------------------------

        if self.is_uploading:

            return

        self._set_state(
            UpdateControllerState.WAITING_FOR_DEVICE,
            "Waiting for UB3",
        )

    def _handle_device_changed(
        self,
        device: Device | None,
    ) -> None:
        """
        Handle a device change notification.

        A disconnected/empty Device object is normalized to
        None at the controller level.

        The controller should expose only the currently
        connected UB3 as self.device.
        """

        # -----------------------------------------------------
        # Normalize disconnected device
        # -----------------------------------------------------

        if device is None:

            self.device = None

        elif not getattr(
            device,
            "connected",
            False,
        ):

            self.device = None

        else:

            self.device = device

        # -----------------------------------------------------
        # Notify GUI/application
        # -----------------------------------------------------

        if self._on_device_changed is not None:

            self._on_device_changed(
                self.device
            )

        # -----------------------------------------------------
        # Do not change application state while an upload
        # is running.
        #
        # Maple changes USB identity during programming.
        # UploadService owns that transition.
        # -----------------------------------------------------

        if self.is_uploading:

            return

        # -----------------------------------------------------
        # No device
        # -----------------------------------------------------

        if self.device is None:

            self._set_state(
                UpdateControllerState.WAITING_FOR_DEVICE,
                "Waiting for UB3",
            )

            return

        # -----------------------------------------------------
        # Device connected but not Maple Serial
        # -----------------------------------------------------

        if not self._is_update_ready_device(
            self.device
        ):

            self._set_state(
                UpdateControllerState.DEVICE_CONNECTED,
                "UB3 Connected",
            )

            return

        # -----------------------------------------------------
        # Maple Serial device
        # -----------------------------------------------------

        self._set_state(
            UpdateControllerState.DEVICE_CONNECTED,
            f"UB3 Connected - {self.device.com_port}",
        )

        self._update_ready_state()

    # =====================================================
    # Device Readiness
    # =====================================================

    @staticmethod
    def _is_update_ready_device(
        device: Device | None,
    ) -> bool:
        """
        Determine whether the device is in the state
        expected by UploadService.

        We intentionally support both the current
        DeviceState implementation and string-based test
        doubles.
        """

        if device is None:

            return False

        if not getattr(
            device,
            "connected",
            False,
        ):

            return False

        # -------------------------------------------------
        # Explicit helper/property
        # -------------------------------------------------

        for property_name in (
            "is_maple_serial",
            "is_ready",
        ):

            value = getattr(
                device,
                property_name,
                None,
            )

            if value is True:

                return True

        # -------------------------------------------------
        # State enum/string
        # -------------------------------------------------

        state = getattr(
            device,
            "state",
            None,
        )

        if state is None:

            return False

        state_name = getattr(
            state,
            "name",
            "",
        )

        state_value = getattr(
            state,
            "value",
            state,
        )

        state_name = str(
            state_name
        ).upper()

        state_value = str(
            state_value
        ).upper()

        return (
            "MAPLE_SERIAL" in state_name
            or "MAPLE SERIAL" in state_value
            or state_value == "MAPLE"
        )

    # =====================================================
    # Worker Events
    # =====================================================

    def _handle_worker_state(
        self,
        state: UploadWorkerState,
    ) -> None:
        """
        Translate worker state to application state.
        """

        if state == UploadWorkerState.STARTING:

            self._set_state(
                UpdateControllerState.UPLOADING,
                "Preparing firmware update...",
            )

            return

        if state == UploadWorkerState.UPLOADING:

            self._set_state(
                UpdateControllerState.UPLOADING,
                "Uploading Firmware...",
            )

            return

        if state == UploadWorkerState.COMPLETED:

            # Final state is determined by UploadResult.
            return

        if state == UploadWorkerState.FAILED:

            # Final state is determined by UploadResult.
            return

        # -------------------------------------------------
        # Support cancellation where present
        # -------------------------------------------------

        state_name = getattr(
            state,
            "name",
            "",
        )

        if (
            "CANCEL" in str(
                state_name
            ).upper()
        ):

            self._set_state(
                UpdateControllerState.CANCELLED,
                "Update Cancelled",
            )

    def _handle_worker_progress(
        self,
        message: str,
    ) -> None:

        self._set_state(
            UpdateControllerState.UPLOADING,
            str(message),
            emit_status_only=True,
        )

    def _handle_worker_output(
        self,
        message: str,
    ) -> None:

        if self._on_output is not None:

            self._on_output(
                str(message)
            )

    def _handle_worker_error(
        self,
        error: Any,
    ) -> None:

        message = str(
            error
        )

        if self._on_error is not None:

            self._on_error(
                message
            )

    def _handle_worker_completed(
        self,
        result: UploadResult,
    ) -> None:

        self.last_result = result

        # -------------------------------------------------
        # Success
        # -------------------------------------------------

        if result.success:

            if result.has_warning:

                self._set_state(
                    UpdateControllerState.SUCCESS_WITH_WARNING,
                    result.message,
                )

            else:

                self._set_state(
                    UpdateControllerState.SUCCESS,
                    result.message,
                )

        # -------------------------------------------------
        # Failure
        # -------------------------------------------------

        else:

            if result.cancelled:

                self._set_state(
                    UpdateControllerState.CANCELLED,
                    result.message,
                )

            else:

                self._set_state(
                    UpdateControllerState.FAILED,
                    result.message,
                )

        # -------------------------------------------------
        # Notify GUI/application
        # -------------------------------------------------

        if self._on_result is not None:

            self._on_result(
                result
            )

    # =====================================================
    # Ready State
    # =====================================================

    def _update_ready_state(self) -> None:
        """
        Recalculate whether the application is ready for
        another update.

        This is intentionally called after device changes
        and firmware selection changes.
        """

        if self.is_uploading:

            return

        if self.device is None:

            self._set_state(
                UpdateControllerState.WAITING_FOR_DEVICE,
                "Waiting for UB3",
            )

            return

        if not self.device.connected:

            self._set_state(
                UpdateControllerState.WAITING_FOR_DEVICE,
                "Waiting for UB3",
            )

            return

        if not self._is_update_ready_device(
            self.device
        ):

            self._set_state(
                UpdateControllerState.DEVICE_CONNECTED,
                "UB3 Connected",
            )

            return

        if self.selected_firmware is None:

            self._set_state(
                UpdateControllerState.DEVICE_CONNECTED,
                "UB3 Connected",
            )

            return

        self._set_state(
            UpdateControllerState.READY,
            "Ready to Update",
        )

    # =====================================================
    # State Handling
    # =====================================================

    def _set_state(
        self,
        state: UpdateControllerState,
        message: str,
        *,
        emit_status_only: bool = False,
    ) -> None:

        self.state = state

        self.status_message = (
            message
        )

        if not emit_status_only:

            if self._on_state_changed is not None:

                self._on_state_changed(
                    state
                )

        if self._on_status is not None:

            self._on_status(
                message
            )

    # =====================================================
    # Error
    # =====================================================

    def _emit_error(
        self,
        message: str,
    ) -> None:

        self.last_error = (
            RuntimeError(message)
        )

        if self._on_error is not None:

            self._on_error(
                message
            )

    # =====================================================
    # Properties
    # =====================================================

    @property
    def is_ready(self) -> bool:

        return (
            self.state
            == UpdateControllerState.READY
        )

    @property
    def is_waiting(self) -> bool:

        return (
            self.state
            == UpdateControllerState.WAITING_FOR_DEVICE
        )

    @property
    def com_port(self) -> str:

        if self.device is None:

            return ""

        return str(
            getattr(
                self.device,
                "com_port",
                "",
            )
        )

    @property
    def firmware_name(self) -> str:

        if self.selected_firmware is None:

            return ""

        return str(
            getattr(
                self.selected_firmware,
                "name",
                "",
            )
        )

    @property
    def firmware_version(self) -> str:

        if self.selected_firmware is None:

            return ""

        return str(
            getattr(
                self.selected_firmware,
                "version",
                "",
            )
        )

    # =====================================================
    # Debug Information
    # =====================================================

    def status_snapshot(self) -> dict[str, Any]:
        """
        Return controller state for diagnostics or GUI.
        """

        return {
            "state": self.state.value,
            "status_message": self.status_message,
            "device_connected": (
                self.device.connected
                if self.device is not None
                else False
            ),
            "com_port": self.com_port,
            "firmware_name": self.firmware_name,
            "firmware_version": self.firmware_version,
            "can_update": self.can_update,
            "is_uploading": self.is_uploading,
            "last_result": self.last_result,
            "last_error": (
                str(self.last_error)
                if self.last_error is not None
                else ""
            ),
        }