"""
=========================================================
UB3 Firmware Updater

Firmware Model

Developer:
Benjamin William

Description:
Represents one firmware package in the local UB3
firmware repository.

Firmware metadata is stored separately from the binary
and loaded by FirmwareService.

Version:
0.5.0
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class Firmware:

    # =====================================================
    # Firmware Identity
    # =====================================================

    name: str = ""

    version: str = ""

    release_date: str = ""

    description: str = ""

    target_device: str = ""

    hardware: str = ""

    # =====================================================
    # Firmware File
    # =====================================================

    filename: str = ""

    path: str = ""

    metadata_path: str = ""

    size: int = 0

    # =====================================================
    # Integrity
    # =====================================================

    checksum: str = ""

    checksum_algorithm: str = "SHA256"

    # =====================================================
    # Internal Metadata
    # =====================================================

    created_at: datetime | None = None

    # =====================================================
    # Properties
    # =====================================================

    @property
    def file_path(self) -> Path:

        return Path(self.path)

    @property
    def metadata_file_path(self) -> Path:

        return Path(self.metadata_path)

    @property
    def exists(self) -> bool:

        return self.file_path.is_file()

    @property
    def metadata_exists(self) -> bool:

        return self.metadata_file_path.is_file()

    @property
    def extension(self) -> str:

        return self.file_path.suffix.lower()

    @property
    def size_mb(self) -> float:

        return self.size / (1024 * 1024)

    @property
    def display_name(self) -> str:

        if self.name and self.version:

            return f"{self.name} v{self.version}"

        if self.name:

            return self.name

        return self.filename

    # =====================================================
    # Validation
    # =====================================================

    def is_valid_file(self) -> bool:

        return (
            self.exists
            and self.extension == ".bin"
            and self.size > 0
        )

    # =====================================================
    # Serialization
    # =====================================================

    def to_dict(self) -> dict:

        data = asdict(self)

        if self.created_at is not None:

            data["created_at"] = (
                self.created_at.isoformat()
            )

        return data

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> Firmware:

        created_at = data.get("created_at")

        if created_at:

            created_at = datetime.fromisoformat(
                created_at
            )

        return cls(

            name=data.get("name", ""),

            version=data.get("version", ""),

            release_date=data.get(
                "release_date",
                "",
            ),

            description=data.get(
                "description",
                "",
            ),

            target_device=data.get(
                "target_device",
                "",
            ),

            hardware=data.get(
                "hardware",
                "",
            ),

            filename=data.get(
                "filename",
                "",
            ),

            path=data.get(
                "path",
                "",
            ),

            metadata_path=data.get(
                "metadata_path",
                "",
            ),

            size=data.get(
                "size",
                0,
            ),

            checksum=data.get(
                "checksum",
                "",
            ),

            checksum_algorithm=data.get(
                "checksum_algorithm",
                "SHA256",
            ),

            created_at=created_at,
        )

    # =====================================================
    # String
    # =====================================================

    def __str__(self) -> str:

        return self.display_name