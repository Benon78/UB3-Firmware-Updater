"""
=========================================================
UB3 Firmware Updater

Upload Result Model

Developer:
Benjamin William

Description:
Represents the outcome of a UB3 firmware update operation.

This model separates firmware-upload business results from
the lower-level ProcessRunner result.

Version:
0.5.0
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


# =========================================================
# Upload Status
# =========================================================

class UploadStatus(str, Enum):
    """
    High-level status of a firmware upload.
    """

    SUCCESS = "Success"

    FAILED = "Failed"

    CANCELLED = "Cancelled"

    TIMEOUT = "Timeout"

    NOT_STARTED = "Not Started"

    DEVICE_NOT_READY = "Device Not Ready"

    FIRMWARE_INVALID = "Firmware Invalid"

    PROCESS_ERROR = "Process Error"


# =========================================================
# Upload Result
# =========================================================

@dataclass(slots=True)
class UploadResult:
    """
    Result of one firmware update attempt.
    """

    # -----------------------------------------------------
    # Operation
    # -----------------------------------------------------

    status: UploadStatus = UploadStatus.NOT_STARTED

    message: str = ""

    # -----------------------------------------------------
    # Firmware
    # -----------------------------------------------------

    firmware_name: str = ""

    firmware_version: str = ""

    firmware_path: str = ""

    # -----------------------------------------------------
    # Device
    # -----------------------------------------------------

    com_port: str = ""

    device_state: str = ""

    # -----------------------------------------------------
    # Process
    # -----------------------------------------------------

    command: list[str] | None = None

    return_code: int | None = None

    stdout: str = ""

    stderr: str = ""

    # -----------------------------------------------------
    # Process State
    # -----------------------------------------------------

    started: bool = False

    timed_out: bool = False

    cancelled: bool = False

    # -----------------------------------------------------
    # Timing
    # -----------------------------------------------------

    started_at: datetime | None = None

    completed_at: datetime | None = None

    duration_seconds: float = 0.0

    # =====================================================
    # Properties
    # =====================================================

    @property
    def success(self) -> bool:
        """
        Return True when the firmware upload completed
        successfully.
        """

        return self.status == UploadStatus.SUCCESS

    @property
    def failed(self) -> bool:
        """
        Return True when the firmware upload failed.
        """

        return self.status in {
            UploadStatus.FAILED,
            UploadStatus.PROCESS_ERROR,
            UploadStatus.FIRMWARE_INVALID,
            UploadStatus.DEVICE_NOT_READY,
            UploadStatus.TIMEOUT,
        }

    @property
    def is_finished(self) -> bool:
        """
        Return True when the operation reached a final
        state.
        """

        return self.status != UploadStatus.NOT_STARTED

    @property
    def display_status(self) -> str:
        """
        Return a GUI-friendly status string.
        """

        return self.status.value

    # =====================================================
    # Factory Methods
    # =====================================================

    @classmethod
    def success_result(
        cls,
        *,
        message: str = "Firmware upload completed successfully.",
        firmware_name: str = "",
        firmware_version: str = "",
        firmware_path: str = "",
        com_port: str = "",
        device_state: str = "",
        command: list[str] | None = None,
        return_code: int | None = 0,
        stdout: str = "",
        stderr: str = "",
        started: bool = True,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        duration_seconds: float = 0.0,
    ) -> UploadResult:

        return cls(
            status=UploadStatus.SUCCESS,
            message=message,
            firmware_name=firmware_name,
            firmware_version=firmware_version,
            firmware_path=firmware_path,
            com_port=com_port,
            device_state=device_state,
            command=command,
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
            started=started,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration_seconds,
        )

    @classmethod
    def failed_result(
        cls,
        message: str,
        *,
        firmware_name: str = "",
        firmware_version: str = "",
        firmware_path: str = "",
        com_port: str = "",
        device_state: str = "",
        command: list[str] | None = None,
        return_code: int | None = None,
        stdout: str = "",
        stderr: str = "",
        started: bool = False,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        duration_seconds: float = 0.0,
    ) -> UploadResult:

        return cls(
            status=UploadStatus.FAILED,
            message=message,
            firmware_name=firmware_name,
            firmware_version=firmware_version,
            firmware_path=firmware_path,
            com_port=com_port,
            device_state=device_state,
            command=command,
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
            started=started,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration_seconds,
        )

    @classmethod
    def cancelled_result(
        cls,
        message: str = "Firmware upload was cancelled.",
        **kwargs,
    ) -> UploadResult:

        return cls(
            status=UploadStatus.CANCELLED,
            message=message,
            cancelled=True,
            **kwargs,
        )

    @classmethod
    def timeout_result(
        cls,
        message: str = "Firmware upload timed out.",
        **kwargs,
    ) -> UploadResult:

        return cls(
            status=UploadStatus.TIMEOUT,
            message=message,
            timed_out=True,
            **kwargs,
        )

    @classmethod
    def device_not_ready(
        cls,
        message: str = (
            "UB3 is not ready for firmware update."
        ),
        **kwargs,
    ) -> UploadResult:

        return cls(
            status=UploadStatus.DEVICE_NOT_READY,
            message=message,
            **kwargs,
        )

    @classmethod
    def firmware_invalid(
        cls,
        message: str = "Firmware is invalid.",
        **kwargs,
    ) -> UploadResult:

        return cls(
            status=UploadStatus.FIRMWARE_INVALID,
            message=message,
            **kwargs,
        )

    @classmethod
    def process_error(
        cls,
        message: str,
        **kwargs,
    ) -> UploadResult:

        return cls(
            status=UploadStatus.PROCESS_ERROR,
            message=message,
            **kwargs,
        )

    # =====================================================
    # Serialization
    # =====================================================

    def to_dict(self) -> dict:
        """
        Convert the result into a serializable dictionary.
        """

        data = asdict(self)

        data["status"] = self.status.value

        if self.started_at is not None:

            data["started_at"] = (
                self.started_at.isoformat()
            )

        if self.completed_at is not None:

            data["completed_at"] = (
                self.completed_at.isoformat()
            )

        return data

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> UploadResult:
        """
        Reconstruct an UploadResult from a dictionary.
        """

        status_value = data.get(
            "status",
            UploadStatus.NOT_STARTED.value,
        )

        try:

            status = UploadStatus(status_value)

        except ValueError:

            status = UploadStatus.NOT_STARTED

        started_at = data.get("started_at")

        if started_at:

            started_at = datetime.fromisoformat(
                started_at
            )

        completed_at = data.get("completed_at")

        if completed_at:

            completed_at = datetime.fromisoformat(
                completed_at
            )

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

            command=data.get(
                "command",
            ),

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

            started_at=started_at,

            completed_at=completed_at,

            duration_seconds=data.get(
                "duration_seconds",
                0.0,
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