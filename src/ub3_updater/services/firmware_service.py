"""
=========================================================
UB3 Device Manager

Firmware Service

Developer:
Benjamin William

Version:
0.2.0
=========================================================
"""

from pathlib import Path
import json

from ub3_updater.services.config_service import ConfigService
from ub3_updater.services.logger_service import LoggerService


class FirmwareService:

    @staticmethod
    def firmware_root():

        cfg = ConfigService.app()

        project = Path(__file__).resolve().parents[3]

        return project / cfg["paths"]["firmware"]

    @classmethod
    def available_firmware(cls):

        firmware_list = []

        root = cls.firmware_root()

        if not root.exists():

            LoggerService.warning("Firmware directory not found.")

            return firmware_list

        for folder in root.iterdir():

            if not folder.is_dir():

                continue

            metadata = folder / "firmware.json"

            if not metadata.exists():

                continue

            with open(metadata, encoding="utf-8") as file:

                info = json.load(file)

            firmware_list.append(info)

        LoggerService.info(
            f"{len(firmware_list)} firmware package(s) loaded."
        )

        return firmware_list

    @classmethod
    def get_firmware_file(cls, firmware_name):

        root = cls.firmware_root()

        for folder in root.iterdir():

            metadata = folder / "firmware.json"

            if not metadata.exists():

                continue

            with open(metadata, encoding="utf-8") as file:

                info = json.load(file)

            if info["name"] == firmware_name:

                return folder / info["file"]

        return None