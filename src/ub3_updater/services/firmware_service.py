"""
=========================================================
UB3 Firmware Updater

Firmware Service

Developer:
Benjamin William

Description:
Discovers, validates, and manages firmware packages
available to the UB3 Firmware Updater.

Responsibilities
----------------
• Discover firmware files
• Build Firmware models
• Validate firmware files
• Calculate firmware checksums
• Find firmware by name/version
• Provide the default firmware

This service NEVER:
• Connects to the UB3
• Executes maple_upload.exe
• Controls the DeviceMonitor
• Updates the GUI

The actual maple_upload command is handled later by
UploadService.

Version:
0.4.0
=========================================================
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from ub3_updater.models.firmware import Firmware


class FirmwareService:

    # =====================================================
    # Configuration
    # =====================================================

    DEFAULT_FIRMWARE_ROOT = Path("resources/firmware")

    SUPPORTED_EXTENSIONS = {
        ".bin",
    }

    # =====================================================
    # Initialization
    # =====================================================

    def __init__(self, firmware_root: str | Path | None = None):

        if firmware_root is None:
            firmware_root = self.DEFAULT_FIRMWARE_ROOT

        self.firmware_root = Path(firmware_root)

        self._firmwares: list[Firmware] = []

    # =====================================================
    # Public API
    # =====================================================

    def scan(self) -> list[Firmware]:
        """
        Discover all supported firmware files.

        Firmware files are searched recursively under the
        configured firmware root directory.
        """

        self._firmwares = []

        if not self.firmware_root.exists():
            return []

        if not self.firmware_root.is_dir():
            return []

        for file_path in sorted(
            self.firmware_root.rglob("*")
        ):

            if not file_path.is_file():
                continue

            if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue

            firmware = self._build_firmware(file_path)

            if firmware is not None:
                self._firmwares.append(firmware)

        return list(self._firmwares)

    # =====================================================

    def get_all(self) -> list[Firmware]:
        """
        Return the currently discovered firmware list.

        If scan() has not been called yet, perform a scan.
        """

        if not self._firmwares:
            return self.scan()

        return list(self._firmwares)

    # =====================================================

    def refresh(self) -> list[Firmware]:
        """
        Force a new firmware discovery scan.
        """

        return self.scan()

    # =====================================================

    def find(
        self,
        name: str,
        version: str | None = None,
    ) -> Firmware | None:
        """
        Find firmware by name and optionally version.
        """

        firmwares = self.get_all()

        for firmware in firmwares:

            if firmware.name.lower() != name.lower():
                continue

            if version is not None:

                if firmware.version != version:
                    continue

            return firmware

        return None

    # =====================================================

    def get_default(self) -> Firmware | None:
        """
        Return the configured default firmware.

        The current project uses ZNA2US as the default
        firmware package.
        """

        firmware = self.find("ZNA2US")

        if firmware is not None:
            return firmware

        firmwares = self.get_all()

        if not firmwares:
            return None

        return firmwares[0]

    # =====================================================

    def validate(self, firmware: Firmware) -> tuple[bool, str]:
        """
        Validate a firmware package before uploading.

        Returns:
            (True, "") when valid.

            (False, "reason") when invalid.
        """

        if firmware is None:
            return False, "No firmware selected."

        if not firmware.path:
            return False, "Firmware path is empty."

        file_path = Path(firmware.path)

        if not file_path.exists():
            return False, (
                f"Firmware file does not exist: {file_path}"
            )

        if not file_path.is_file():
            return False, (
                f"Firmware path is not a file: {file_path}"
            )

        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return False, (
                f"Unsupported firmware format: "
                f"{file_path.suffix}"
            )

        if file_path.stat().st_size == 0:
            return False, "Firmware file is empty."

        return True, ""

    # =====================================================

    def calculate_checksum(
        self,
        firmware: Firmware,
    ) -> str:
        """
        Calculate SHA-256 checksum for a firmware file.
        """

        file_path = Path(firmware.path)

        sha256 = hashlib.sha256()

        with file_path.open("rb") as file:

            while True:

                chunk = file.read(1024 * 1024)

                if not chunk:
                    break

                sha256.update(chunk)

        return sha256.hexdigest()

    # =====================================================

    def verify_checksum(
        self,
        firmware: Firmware,
    ) -> bool:
        """
        Verify the firmware checksum when a checksum is
        available in the Firmware model.

        If no checksum has been defined, return False
        rather than assuming the file is valid.
        """

        if not firmware.checksum:
            return False

        actual = self.calculate_checksum(firmware)

        return (
            actual.lower()
            == firmware.checksum.lower()
        )

    # =====================================================
    # Firmware Builder
    # =====================================================

    def _build_firmware(
        self,
        file_path: Path,
    ) -> Firmware | None:
        """
        Build a Firmware model from a firmware file.

        Expected project structure:

            resources/
                firmware/
                    ZNA2US/
                        firmware.bin

        The parent directory is used as the firmware
        package name.
        """

        try:

            relative_path = file_path.relative_to(
                self.firmware_root
            )

        except ValueError:

            return None

        # ---------------------------------------------
        # Package name
        # ---------------------------------------------

        if len(relative_path.parts) > 1:

            name = relative_path.parts[0]

        else:

            name = file_path.stem

        # ---------------------------------------------
        # Version
        # ---------------------------------------------

        version = self._extract_version(
            file_path.name
        )

        # ---------------------------------------------
        # File information
        # ---------------------------------------------

        size = file_path.stat().st_size

        return Firmware(

            name=name,

            version=version,

            filename=file_path.name,

            path=str(file_path.resolve()),

            size=size,

        )

    # =====================================================
    # Version Detection
    # =====================================================

    @staticmethod
    def _extract_version(filename: str) -> str:
        """
        Extract a firmware version from the filename.

        Example:

            UnlockBoxIII_260123_ZNA2US-WWDG2d_1.00.ino.generic_stm32f103r.bin

        returns:

            1.00

        If no version can be identified, return an empty
        string.

        This method intentionally uses a conservative
        pattern and does not modify the filename.
        """

        import re

        match = re.search(
            r"[_-](\d+\.\d+)(?:\.[^.]+)*\.bin$",
            filename,
            re.IGNORECASE,
        )

        if match:
            return match.group(1)

        return ""