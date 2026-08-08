"""
=========================================================
UB3 Firmware Updater

Firmware Model

Developer:
Benjamin William

Description:
Represents a firmware package available to the UB3
Firmware Updater.

This model contains firmware metadata only.

It does NOT:
    • Scan firmware folders
    • Execute firmware uploads
    • Communicate with the UB3
    • Update the GUI

Version:
0.4.0
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


# =========================================================
# Firmware Model
# =========================================================

@dataclass(slots=True)
class Firmware:

    # -----------------------------------------------------
    # Identity
    # -----------------------------------------------------

    name: str = ""

    version: str = ""

    # -----------------------------------------------------
    # File Information
    # -----------------------------------------------------

    filename: str = ""

    path: str = ""

    # File size in bytes
    size: int = 0

    # -----------------------------------------------------
    # Integrity
    # -----------------------------------------------------

    checksum: str = ""

    checksum_algorithm: str = "SHA256"

    # -----------------------------------------------------
    # Metadata
    # -----------------------------------------------------

    description: str = ""

    created_at: datetime | None = None

    # =====================================================
    # Properties
    # =====================================================

    @property
    def file_path(self) -> Path:
        """
        Return the firmware file as a pathlib.Path.
        """

        return Path(self.path)

    @property
    def exists(self) -> bool:
        """
        Return True if the firmware file exists.
        """

        return self.file_path.is_file()

    @property
    def extension(self) -> str:
        """
        Return the firmware file extension.
        """

        return self.file_path.suffix.lower()

    @property
    def size_mb(self) -> float:
        """
        Return the firmware size in MB.
        """

        return self.size / (1024 * 1024)

    @property
    def display_name(self) -> str:
        """
        Return a user-friendly firmware name.
        """

        if self.version:

            return f"{self.name} v{self.version}"

        return self.name or self.filename

    # =====================================================
    # Validation
    # =====================================================

    def is_valid_file(self) -> bool:
        """
        Basic firmware file validation.

        This only verifies that the path points to a file.
        Firmware content validation belongs to the
        FirmwareService.
        """

        return self.exists

    # =====================================================
    # Serialization
    # =====================================================

    def to_dict(self) -> dict:
        """
        Convert the firmware model into a dictionary.
        """

        data = asdict(self)

        if self.created_at is not None:

            data["created_at"] = self.created_at.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: dict) -> Firmware:
        """
        Create a Firmware object from a dictionary.
        """

        created_at = data.get("created_at")

        if created_at:

            created_at = datetime.fromisoformat(created_at)

        return cls(
            name=data.get("name", ""),
            version=data.get("version", ""),
            filename=data.get("filename", ""),
            path=data.get("path", ""),
            size=data.get("size", 0),
            checksum=data.get("checksum", ""),
            checksum_algorithm=data.get(
                "checksum_algorithm",
                "SHA256",
            ),
            description=data.get("description", ""),
            created_at=created_at,
        )

    # =====================================================
    # String Representation
    # =====================================================

    def __str__(self) -> str:

        return self.display_name