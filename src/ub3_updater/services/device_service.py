"""
=========================================================
UB3 Firmware Updater

Device Service

Developer:
Benjamin William

Description:
Hardware detection engine.

Responsibilities:
    • Scan available COM ports
    • Identify supported UB3 devices
    • Determine hardware state
    • Build Device objects

This service NEVER:

    • Uploads firmware
    • Logs events
    • Updates the UI

Version:
0.4.0
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
    STM32_VENDOR_ID,
    SUPPORTED_DEVICES,
)


class DeviceService:

    def __init__(self):

        self.current_device = Device()

    # =====================================================
    # Public API
    # =====================================================

    def scan(self) -> Device:
        """
        Scan all COM ports and return the first supported UB3.
        """

        ports = self.scan_ports()

        for port in ports:

            device = self.identify_device(port)

            if device.connected:

                self.current_device = device

                return device

        self.current_device = Device()

        return self.current_device

    def scan_ports(self):

        return enumerate_ports()

    def get_current_device(self):

        return self.current_device

    def refresh(self):

        return self.scan()

    def is_connected(self):

        return self.current_device.connected

    def is_maple(self):

        return self.current_device.state == DeviceState.MAPLE_SERIAL

    def is_bootloader(self):

        return self.current_device.state == DeviceState.USB_SERIAL

    # =====================================================
    # Device Identification
    # =====================================================

    def identify_device(self, port):

        info = port_to_dict(port)

        return self.build_device(info)

    # =====================================================
    # Device Builder
    # =====================================================

    def build_device(self, info: dict):

        vid = ""

        if info["vid"] is not None:
            vid = f"{info['vid']:04X}"

        pid = ""

        if info["pid"] is not None:
            pid = f"{info['pid']:04X}"

        state = self.detect_state(vid, pid)

        if state == DeviceState.UNKNOWN:
            return Device()

        return Device(

            connected=True,

            state=state,

            com_port=info.get("device", ""),

            usb_name=info.get("description", ""),

            description=info.get("description", ""),

            manufacturer=info.get("manufacturer", ""),

            vid=vid,

            pid=pid,

            hwid=info.get("hwid", ""),

            location=info.get("location", ""),

            detected_at=datetime.now(),

        )

    # =====================================================
    # State Detection
    # =====================================================

    def detect_state(self, vid: str, pid: str):

        if vid != STM32_VENDOR_ID:

            return DeviceState.UNKNOWN

        profile = SUPPORTED_DEVICES.get((vid, pid))

        if profile is None:

            return DeviceState.UNKNOWN

        return DeviceState[profile["state"]]