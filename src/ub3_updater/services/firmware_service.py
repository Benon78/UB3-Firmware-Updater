"""
=========================================================
UB3 Firmware Updater

Firmware Service

Developer:
Benjamin William

Description:
Discovers and validates firmware packages stored in the
local firmware repository.

Responsibilities
----------------
• Discover firmware packages
• Read firmware.json metadata
• Locate firmware binaries
• Validate firmware packages
• Detect duplicate firmware names
• Calculate checksums
• Find firmware by name/version
• Provide the default firmware

This service does NOT:
• Upload firmware
• Communicate with USB devices
• Execute external processes
• Control the GUI

Version:
0.5.0
=========================================================
"""

from __future__ import annotations

import hashlib
import json
import re

from pathlib import Path

from ub3_updater.models.firmware import Firmware


class FirmwareService:

    # =====================================================
    # Configuration
    # =====================================================

    DEFAULT_FIRMWARE_ROOT = Path(
        "resources/firmware"
    )

    METADATA_FILENAME = "firmware.json"

    SUPPORTED_EXTENSIONS = {
        ".bin",
    }

    DEFAULT_FIRMWARE_NAME = "ZNA2US"

    # =====================================================
    # Initialization
    # =====================================================

    def __init__(
        self,
        firmware_root: str | Path | None = None,
    ):

        if firmware_root is None:

            firmware_root = (
                self.DEFAULT_FIRMWARE_ROOT
            )

        self.firmware_root = Path(
            firmware_root
        )

        self._firmwares: list[Firmware] = []

        self._errors: list[str] = []

    # =====================================================
    # Discovery
    # =====================================================

    def scan(self) -> list[Firmware]:
        """
        Discover firmware packages.

        Each firmware package must have a dedicated
        directory containing firmware.json and a .bin file.
        """

        self._firmwares = []

        self._errors = []

        if not self.firmware_root.exists():

            self._errors.append(
                "Firmware repository does not exist: "
                f"{self.firmware_root}"
            )

            return []

        if not self.firmware_root.is_dir():

            self._errors.append(
                "Firmware repository is not a directory: "
                f"{self.firmware_root}"
            )

            return []

        package_directories = sorted(
            path
            for path in self.firmware_root.iterdir()
            if path.is_dir()
        )

        for package_directory in package_directories:

            firmware = self._load_package(
                package_directory
            )

            if firmware is not None:

                self._firmwares.append(
                    firmware
                )

        self._remove_duplicates()

        return list(self._firmwares)

    # =====================================================
    # Repository Information
    # =====================================================

    def get_all(self) -> list[Firmware]:

        if not self._firmwares:

            return self.scan()

        return list(self._firmwares)

    def refresh(self) -> list[Firmware]:

        return self.scan()

    def get_errors(self) -> list[str]:

        return list(self._errors)

    # =====================================================
    # Find
    # =====================================================

    def find(
        self,
        name: str,
        version: str | None = None,
    ) -> Firmware | None:

        for firmware in self.get_all():

            if (
                firmware.name.lower()
                != name.lower()
            ):
                continue

            if version is not None:

                if firmware.version != version:

                    continue

            return firmware

        return None

    # =====================================================

    def get_default(self) -> Firmware | None:

        firmware = self.find(
            self.DEFAULT_FIRMWARE_NAME
        )

        if firmware is not None:

            return firmware

        firmwares = self.get_all()

        if not firmwares:

            return None

        return firmwares[0]

    # =====================================================
    # Validation
    # =====================================================

    def validate(
        self,
        firmware: Firmware,
    ) -> tuple[bool, str]:

        if firmware is None:

            return False, "No firmware selected."

        if not firmware.name:

            return False, "Firmware name is missing."

        if not firmware.version:

            return False, "Firmware version is missing."

        if not firmware.path:

            return False, "Firmware path is missing."

        firmware_path = Path(
            firmware.path
        )

        if not firmware_path.exists():

            return False, (
                "Firmware file does not exist: "
                f"{firmware_path}"
            )

        if not firmware_path.is_file():

            return False, (
                "Firmware path is not a file: "
                f"{firmware_path}"
            )

        if (
            firmware_path.suffix.lower()
            not in self.SUPPORTED_EXTENSIONS
        ):

            return False, (
                "Unsupported firmware file type: "
                f"{firmware_path.suffix}"
            )

        if firmware_path.stat().st_size <= 0:

            return False, "Firmware file is empty."

        if firmware.target_device:

            if firmware.target_device.upper() != "UB3":

                return False, (
                    "Firmware target device is not UB3: "
                    f"{firmware.target_device}"
                )

        return True, ""

    # =====================================================
    # Package Loading
    # =====================================================

    def _load_package(
        self,
        package_directory: Path,
    ) -> Firmware | None:

        metadata_path = (
            package_directory
            / self.METADATA_FILENAME
        )

        if not metadata_path.is_file():

            self._errors.append(
                "Missing firmware metadata: "
                f"{metadata_path}"
            )

            return None

        try:

            metadata = self._read_metadata(
                metadata_path
            )

        except (OSError, json.JSONDecodeError) as exc:

            self._errors.append(
                "Unable to read firmware metadata "
                f"{metadata_path}: {exc}"
            )

            return None

        firmware_path = self._resolve_binary(
            package_directory,
            metadata,
        )

        if firmware_path is None:

            self._errors.append(
                "No firmware .bin file found in: "
                f"{package_directory}"
            )

            return None

        firmware = Firmware(

            name=str(
                metadata.get(
                    "name",
                    package_directory.name,
                )
            ).strip(),

            version=str(
                metadata.get(
                    "version",
                    "",
                )
            ).strip(),

            release_date=str(
                metadata.get(
                    "release_date",
                    "",
                )
            ).strip(),

            description=str(
                metadata.get(
                    "description",
                    "",
                )
            ).strip(),

            target_device=str(
                metadata.get(
                    "target_device",
                    metadata.get(
                        "hardware",
                        "",
                    ),
                )
            ).strip(),

            hardware=str(
                metadata.get(
                    "hardware",
                    "",
                )
            ).strip(),

            filename=firmware_path.name,

            path=str(
                firmware_path.resolve()
            ),

            metadata_path=str(
                metadata_path.resolve()
            ),

            size=firmware_path.stat().st_size,

            checksum=str(
                metadata.get(
                    "checksum",
                    "",
                )
            ).strip(),

            checksum_algorithm=str(
                metadata.get(
                    "checksum_algorithm",
                    "SHA256",
                )
            ).strip(),

        )

        valid, error = self.validate(
            firmware
        )

        if not valid:

            self._errors.append(
                f"{firmware.display_name}: {error}"
            )

            return None

        return firmware

    # =====================================================
    # Metadata
    # =====================================================

    @staticmethod
    def _read_metadata(
        metadata_path: Path,
    ) -> dict:

        with metadata_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if not isinstance(data, dict):

            raise ValueError(
                "Firmware metadata must be a JSON object."
            )

        return data

    # =====================================================
    # Binary Resolution
    # =====================================================

    def _resolve_binary(
        self,
        package_directory: Path,
        metadata: dict,
    ) -> Path | None:

        # ---------------------------------------------
        # Preferred: explicit file in metadata
        # ---------------------------------------------

        filename = metadata.get("file")

        if filename:

            candidate = (
                package_directory
                / str(filename)
            )

            if (
                candidate.is_file()
                and candidate.suffix.lower()
                in self.SUPPORTED_EXTENSIONS
            ):

                return candidate

        # ---------------------------------------------
        # Alternative metadata key
        # ---------------------------------------------

        filename = metadata.get("filename")

        if filename:

            candidate = (
                package_directory
                / str(filename)
            )

            if (
                candidate.is_file()
                and candidate.suffix.lower()
                in self.SUPPORTED_EXTENSIONS
            ):

                return candidate

        # ---------------------------------------------
        # Fallback: exactly one .bin
        # ---------------------------------------------

        binaries = sorted(
            path
            for path in package_directory.iterdir()
            if (
                path.is_file()
                and path.suffix.lower()
                in self.SUPPORTED_EXTENSIONS
            )
        )

        if len(binaries) == 1:

            return binaries[0]

        if len(binaries) > 1:

            self._errors.append(
                "Multiple firmware binaries found "
                f"without an explicit file entry: "
                f"{package_directory}"
            )

        return None

    # =====================================================
    # Duplicate Detection
    # =====================================================

    def _remove_duplicates(self) -> None:

        unique: dict[
            tuple[str, str],
            Firmware,
        ] = {}

        for firmware in self._firmwares:

            key = (
                firmware.name.lower(),
                firmware.version,
            )

            if key in unique:

                self._errors.append(
                    "Duplicate firmware detected: "
                    f"{firmware.display_name}"
                )

                continue

            unique[key] = firmware

        self._firmwares = list(
            unique.values()
        )

    # =====================================================
    # Checksum
    # =====================================================

    def calculate_checksum(
        self,
        firmware: Firmware,
    ) -> str:

        algorithm = (
            firmware.checksum_algorithm
            or "SHA256"
        ).lower()

        if algorithm != "sha256":

            raise ValueError(
                "Unsupported checksum algorithm: "
                f"{firmware.checksum_algorithm}"
            )

        sha256 = hashlib.sha256()

        with Path(
            firmware.path
        ).open("rb") as file:

            while True:

                chunk = file.read(
                    1024 * 1024
                )

                if not chunk:

                    break

                sha256.update(chunk)

        return sha256.hexdigest()

    # =====================================================

    def verify_checksum(
        self,
        firmware: Firmware,
    ) -> bool:

        if not firmware.checksum:

            return False

        actual = self.calculate_checksum(
            firmware
        )

        return (
            actual.lower()
            == firmware.checksum.lower()
        )