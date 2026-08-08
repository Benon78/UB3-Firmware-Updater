"""
=========================================================
UB3 Firmware Updater

Upload Result Model

Developer:
Benjamin William

Description:
Represents the final result of a firmware upload.

The model separates:

    SUCCESS
        Firmware was programmed successfully.

    SUCCESS_WITH_WARNING
        Firmware was programmed successfully, but a
        non-fatal warning occurred after programming.

    FAILED
        Firmware programming did not complete successfully.

    CANCELLED
        Operator/process cancellation.

    TIMEOUT
        Upload exceeded configured timeout.

    DEVICE_NOT_READY
        UB3 was not in a valid state for upload.

    FIRMWARE_INVALID
        Selected firmware is invalid.

    PROCESS_ERROR
        External uploader could not be started/executed.

    NOT_STARTED
        Upload has not started.

Important:
-----------
A process return code of 0 does NOT automatically mean
firmware programming succeeded.

Maple Loader output must be interpreted by UploadService.

Version:
0.6.0
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


# =========================================================
# Upload Status
# =========================================================

class UploadStatus(Enum):
    """
    High-level status of a firmware upload operation.
    """

    NOT_STARTED = "Not Started"

    DEVICE_NOT_READY = "Device Not Ready"

    FIRMWARE_INVALID = "Firmware Invalid"

    PROCESS_ERROR = "Process Error"

    UPLOADING = "Uploading"

    SUCCESS = "Success"

    SUCCESS_WITH_WARNING = "Success With Warning"

    FAILED = "Failed"

    CANCELLED = "Cancelled"

    TIMEOUT = "Timeout"


# =========================================================
# Upload Result
# =========================================================

@dataclass(slots=True)
class UploadResult:
    """
    Final result of a firmware upload operation.

    This object is returned by UploadService and can later
    be consumed directly by:

        • UploadWorker
        • GUI
        • LoggerService
        • Retry logic
        • Production reporting
    """

    # =====================================================
    # Core Result
    # =====================================================

    status: UploadStatus = UploadStatus.NOT_STARTED

    message: str = ""

    # =====================================================
    # Firmware Information
    # =====================================================

    firmware_name: str = ""

    firmware_version: str = ""

    firmware_path: str = ""

    # =====================================================
    # Device Information
    # =====================================================

    com_port: str = ""

    device_state: str = ""

    # =====================================================
    # Process Information
    # =====================================================

    command: list[str] | None = None

    return_code: int | None = None

    stdout: str = ""

    stderr: str = ""

    # =====================================================
    # Process State
    # =====================================================

    started: bool = False

    timed_out: bool = False

    cancelled: bool = False

    # =====================================================
    # Timing
    # =====================================================

    started_at: datetime | None = None

    completed_at: datetime | None = None

    duration_seconds: float = 0.0

    # =====================================================
    # Additional Diagnostic Information
    # =====================================================

    warning: str = ""

    error: str = ""

    # =====================================================
    # Status Properties
    # =====================================================

    @property
    def success(self) -> bool:
        """
        True when firmware programming completed successfully.

        SUCCESS_WITH_WARNING is also considered a successful
        firmware update.
        """

        return self.status in (
            UploadStatus.SUCCESS,
            UploadStatus.SUCCESS_WITH_WARNING,
        )

    # -----------------------------------------------------

    @property
    def failed(self) -> bool:
        """
        True when the firmware update failed.
        """

        return self.status in (
            UploadStatus.FAILED,
            UploadStatus.PROCESS_ERROR,
            UploadStatus.FIRMWARE_INVALID,
            UploadStatus.DEVICE_NOT_READY,
            UploadStatus.TIMEOUT,
        )

    # -----------------------------------------------------

    @property
    def has_warning(self) -> bool:
        """
        True when the upload succeeded but generated a
        non-fatal warning.
        """

        return (
            self.status
            == UploadStatus.SUCCESS_WITH_WARNING
            or bool(self.warning)
        )

    # -----------------------------------------------------

    @property
    def is_terminal(self) -> bool:
        """
        True when the operation has reached a final state.
        """

        return self.status in (
            UploadStatus.SUCCESS,
            UploadStatus.SUCCESS_WITH_WARNING,
            UploadStatus.FAILED,
            UploadStatus.CANCELLED,
            UploadStatus.TIMEOUT,
            UploadStatus.DEVICE_NOT_READY,
            UploadStatus.FIRMWARE_INVALID,
            UploadStatus.PROCESS_ERROR,
        )

    # -----------------------------------------------------

    @property
    def display_status(self) -> str:
        """
        Human-readable status suitable for the UI.
        """

        return self.status.value

    # -----------------------------------------------------

    @property
    def display_message(self) -> str:
        """
        Human-readable message suitable for the UI.
        """

        if self.message:
            return self.message

        if self.warning:
            return self.warning

        if self.error:
            return self.error

        return self.status.value

    # =====================================================
    # Factory: Not Started
    # =====================================================

    @classmethod
    def not_started(
        cls,
        message: str = "Firmware upload has not started.",
        **kwargs: Any,
    ) -> "UploadResult":

        return cls(
            status=UploadStatus.NOT_STARTED,
            message=message,
            **kwargs,
        )

    # =====================================================
    # Factory: Device Not Ready
    # =====================================================

    @classmethod
    def device_not_ready(
        cls,
        message: str,
        **kwargs: Any,
    ) -> "UploadResult":

        return cls(
            status=UploadStatus.DEVICE_NOT_READY,
            message=message,
            error=message,
            **kwargs,
        )

    # =====================================================
    # Factory: Firmware Invalid
    # =====================================================

    @classmethod
    def firmware_invalid(
        cls,
        message: str,
        **kwargs: Any,
    ) -> "UploadResult":

        return cls(
            status=UploadStatus.FIRMWARE_INVALID,
            message=message,
            error=message,
            **kwargs,
        )

    # =====================================================
    # Factory: Process Error
    # =====================================================

    @classmethod
    def process_error(
        cls,
        message: str,
        **kwargs: Any,
    ) -> "UploadResult":

        return cls(
            status=UploadStatus.PROCESS_ERROR,
            message=message,
            error=message,
            **kwargs,
        )

    # =====================================================
    # Factory: Uploading
    # =====================================================

    @classmethod
    def uploading(
        cls,
        message: str = "Firmware upload in progress.",
        **kwargs: Any,
    ) -> "UploadResult":

        return cls(
            status=UploadStatus.UPLOADING,
            message=message,
            **kwargs,
        )

    # =====================================================
    # Factory: Success
    # =====================================================

    @classmethod
    def success_result(
        cls,
        message: str = (
            "Firmware upload completed successfully."
        ),
        **kwargs: Any,
    ) -> "UploadResult":

        return cls(
            status=UploadStatus.SUCCESS,
            message=message,
            **kwargs,
        )

    # =====================================================
    # Factory: Success With Warning
    # =====================================================

    @classmethod
    def success_with_warning_result(
        cls,
        message: str,
        warning: str = "",
        **kwargs: Any,
    ) -> "UploadResult":
        """
        Create a successful upload result containing a
        non-fatal warning.

        Example:

            Firmware successfully programmed.

            Warning:
            USB reset after download could not be
            completed automatically.
        """

        return cls(
            status=UploadStatus.SUCCESS_WITH_WARNING,
            message=message,
            warning=warning,
            **kwargs,
        )

    # =====================================================
    # Factory: Failed
    # =====================================================

    @classmethod
    def failed_result(
        cls,
        message: str,
        **kwargs: Any,
    ) -> "UploadResult":

        return cls(
            status=UploadStatus.FAILED,
            message=message,
            error=message,
            **kwargs,
        )

    # =====================================================
    # Factory: Cancelled
    # =====================================================

    @classmethod
    def cancelled_result(
        cls,
        message: str = "Firmware upload was cancelled.",
        **kwargs: Any,
    ) -> "UploadResult":

        return cls(
            status=UploadStatus.CANCELLED,
            message=message,
            cancelled=True,
            **kwargs,
        )

    # =====================================================
    # Factory: Timeout
    # =====================================================

    @classmethod
    def timeout_result(
        cls,
        message: str,
        **kwargs: Any,
    ) -> "UploadResult":

        return cls(
            status=UploadStatus.TIMEOUT,
            message=message,
            error=message,
            timed_out=True,
            **kwargs,
        )

    # =====================================================
    # Serialization
    # =====================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Convert UploadResult into a serializable dictionary.

        This is used when storing upload history in logs
        or JSON files.
        """

        return {
            "status": self.status.value,

            "message": self.message,

            "firmware_name": self.firmware_name,

            "firmware_version": self.firmware_version,

            "firmware_path": self.firmware_path,

            "com_port": self.com_port,

            "device_state": self.device_state,

            "command": (
                list(self.command)
                if self.command
                else []
            ),

            "return_code": self.return_code,

            "stdout": self.stdout,

            "stderr": self.stderr,

            "started": self.started,

            "timed_out": self.timed_out,

            "cancelled": self.cancelled,

            "started_at": (
                self.started_at.isoformat()
                if self.started_at
                else None
            ),

            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at
                else None
            ),

            "duration_seconds": (
                self.duration_seconds
            ),

            "warning": self.warning,

            "error": self.error,
        }

    # =====================================================
    # Deserialization
    # =====================================================

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "UploadResult":
        """
        Reconstruct UploadResult from a dictionary.

        This is the reverse operation of to_dict().
        """

        if not isinstance(data, dict):

            raise TypeError(
                "UploadResult.from_dict() expects a dictionary."
            )

        # -------------------------------------------------
        # Status
        # -------------------------------------------------

        raw_status = data.get(
            "status",
            UploadStatus.NOT_STARTED.value,
        )

        if isinstance(
            raw_status,
            UploadStatus,
        ):

            status = raw_status

        else:

            try:

                status = UploadStatus(
                    raw_status
                )

            except ValueError:

                status = (
                    UploadStatus.NOT_STARTED
                )

        # -------------------------------------------------
        # Started timestamp
        # -------------------------------------------------

        started_at = data.get(
            "started_at"
        )

        if started_at:

            if isinstance(
                started_at,
                datetime,
            ):

                started_at_value = (
                    started_at
                )

            else:

                started_at_value = (
                    datetime.fromisoformat(
                        started_at
                    )
                )

        else:

            started_at_value = None

        # -------------------------------------------------
        # Completed timestamp
        # -------------------------------------------------

        completed_at = data.get(
            "completed_at"
        )

        if completed_at:

            if isinstance(
                completed_at,
                datetime,
            ):

                completed_at_value = (
                    completed_at
                )

            else:

                completed_at_value = (
                    datetime.fromisoformat(
                        completed_at
                    )
                )

        else:

            completed_at_value = None

        # -------------------------------------------------
        # Command
        # -------------------------------------------------

        command = data.get(
            "command",
            [],
        )

        if command is None:

            command = []

        else:

            command = list(command)

        # -------------------------------------------------
        # Build object
        # -------------------------------------------------

        return cls(
            status=status,

            message=data.get(
                "message",
                "",
            ),

            firmware_name=data.get(
                "firmware_name",
                "",
            ),

            firmware_version=data.get(
                "firmware_version",
                "",
            ),

            firmware_path=data.get(
                "firmware_path",
                "",
            ),

            com_port=data.get(
                "com_port",
                "",
            ),

            device_state=data.get(
                "device_state",
                "",
            ),

            command=command,

            return_code=data.get(
                "return_code",
            ),

            stdout=data.get(
                "stdout",
                "",
            ),

            stderr=data.get(
                "stderr",
                "",
            ),

            started=data.get(
                "started",
                False,
            ),

            timed_out=data.get(
                "timed_out",
                False,
            ),

            cancelled=data.get(
                "cancelled",
                False,
            ),

            started_at=started_at_value,

            completed_at=completed_at_value,

            duration_seconds=float(
                data.get(
                    "duration_seconds",
                    0.0,
                )
                or 0.0
            ),

            warning=data.get(
                "warning",
                "",
            ),

            error=data.get(
                "error",
                "",
            ),
        )
    # =====================================================
    # String Representation
    # =====================================================

    def __str__(self) -> str:

        return (
            f"{self.status.value}: "
            f"{self.message}"
        )