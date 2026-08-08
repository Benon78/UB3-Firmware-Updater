"""
=========================================================
UB3 Device Manager

Device Service

Developer:
Benjamin William

Description:
Central hardware detection engine.

Responsible for:

• Detecting COM ports
• Detecting Runtime devices
• Detecting DFU Bootloader
• Building Device objects

Does NOT perform uploads.
=========================================================
"""

from __future__ import annotations

from datetime import datetime

from ub3_updater.models.device import Device
from ub3_updater.models.device import DeviceState

from ub3_updater.utils.usb_helper import (
    enumerate_ports,
    port_to_dict,
)

from ub3_updater.constants.usb_ids import (
    STM32_RUNTIME_VENDOR,
    KNOWN_DEVICE_NAMES,
)

from ub3_updater.services.logger_service import LoggerService


class DeviceService:

    def __init__(self):

        self.current_device = Device()

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def scan(self) -> Device:
        """
        Scan all serial ports and return the detected device.
        """

        ports = enumerate_ports()

        for port in ports:

            info = port_to_dict(port)

            device = self._build_device(info)

            if device.connected:

                self.current_device = device

                return device

        self.current_device = Device()

        return self.current_device

    def refresh(self) -> Device:
        """
        Refresh current device information.
        """

        return self.scan()

    def is_connected(self) -> bool:

        return self.current_device.connected

    def get_current_device(self) -> Device:

        return self.current_device

    # --------------------------------------------------
    # Detection
    # --------------------------------------------------

    def _build_device(self, info: dict) -> Device:

        vendor = ""

        if info["vid"] is not None:
            vendor = f"{info['vid']:04X}"

        pid = ""

        if info["pid"] is not None:
            pid = f"{info['pid']:04X}"

        description = info.get("description") or ""

        manufacturer = info.get("manufacturer") or ""

        hwid = info.get("hwid") or ""

        # ------------------------------------------
        # Runtime Device
        # ------------------------------------------

        if self._is_runtime(vendor, description):

            LoggerService.info(
                f"Runtime device detected on {info['device']}"
            )

            return Device(

                connected=True,

                state=DeviceState.RUNTIME,

                com_port=info["device"],

                vid=vendor,

                pid=pid,

                manufacturer=manufacturer,

                description=description,

                hwid=hwid,

                board="STM32",

                firmware="Unknown",

                serial_number=info.get("serial_number") or "--",

                usb_name=description,

                last_seen=datetime.now()

            )

        # ------------------------------------------
        # DFU Bootloader
        # ------------------------------------------

        if self._is_dfu(hwid):

            LoggerService.info(
                "STM32 DFU Bootloader detected."
            )

            return Device(

                connected=True,

                state=DeviceState.DFU,

                com_port=info["device"],

                vid=vendor,

                pid=pid,

                manufacturer=manufacturer,

                description=description,

                hwid=hwid,

                board="STM32",

                firmware="Unknown",

                serial_number=info.get("serial_number") or "--",

                usb_name=description,

                last_seen=datetime.now()

            )

        return Device()

    # --------------------------------------------------
    # Detection Rules
    # --------------------------------------------------

    @staticmethod
    def _is_runtime(vendor: str, description: str) -> bool:

        if vendor == STM32_RUNTIME_VENDOR:
            return True

        return any(
            name.lower() in description.lower()
            for name in KNOWN_DEVICE_NAMES
        )

    @staticmethod
    def _is_dfu(hwid: str) -> bool:

        return "1EAF" in hwid.upper()

    # --------------------------------------------------
    # Convenience Methods
    # --------------------------------------------------

    def runtime_connected(self) -> bool:

        return self.current_device.is_runtime

    def dfu_connected(self) -> bool:

        return self.current_device.is_dfu