"""
=========================================================
UB3 Firmware Updater

Device Model

Developer:
Benjamin William

Description:
Represents a USB device detected by Windows.

This class contains ONLY hardware detection information.

Business logic such as firmware version, upload state,
or update progress belongs to other services.

Version:
0.4.0
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


# =========================================================
# Hardware Mode
# =========================================================

class DeviceState(Enum):
    DISCONNECTED = "Disconnected"

    MAPLE_SERIAL = "Maple Serial"

    USB_SERIAL = "USB Serial Device"

    UNKNOWN = "Unknown"


# =========================================================
# Device
# =========================================================

@dataclass(slots=True)
class Device:

    # ----------------------------------------
    # Hardware State
    # ----------------------------------------

    connected: bool = False

    state: DeviceState = DeviceState.DISCONNECTED

    # ----------------------------------------
    # USB Information
    # ----------------------------------------

    com_port: str = ""

    usb_name: str = ""

    description: str = ""

    manufacturer: str = ""

    vid: str = ""

    pid: str = ""

    hwid: str = ""

    location: str = ""

    # ----------------------------------------
    # Detection
    # ----------------------------------------

    detected_at: datetime | None = None

    # =====================================================
    # Properties
    # =====================================================

    @property
    def is_connected(self):

        return self.connected

    @property
    def is_maple(self):

        return self.state == DeviceState.MAPLE_SERIAL

    @property
    def is_usb_serial(self):

        return self.state == DeviceState.USB_SERIAL

    @property
    def display_name(self):

        if self.usb_name:
            return self.usb_name

        if self.description:
            return self.description

        return "Unknown Device"

    # =====================================================
    # Serialization
    # =====================================================

    def to_dict(self):

        data = asdict(self)

        data["state"] = self.state.value

        if self.detected_at:

            data["detected_at"] = self.detected_at.isoformat()

        return data

    @classmethod
    def from_dict(cls, data):

        detected = data.get("detected_at")

        if detected:

            detected = datetime.fromisoformat(detected)

        return cls(

            connected=data.get("connected", False),

            state=DeviceState(data.get("state", "Disconnected")),

            com_port=data.get("com_port", ""),

            usb_name=data.get("usb_name", ""),

            description=data.get("description", ""),

            manufacturer=data.get("manufacturer", ""),

            vid=data.get("vid", ""),

            pid=data.get("pid", ""),

            hwid=data.get("hwid", ""),

            location=data.get("location", ""),

            detected_at=detected,
        )

    # =====================================================
    # Hardware Comparison
    # =====================================================

    def same_device(self, other):

        if other is None:
            return False

        return (

            self.connected == other.connected

            and self.state == other.state

            and self.com_port == other.com_port

            and self.vid == other.vid

            and self.pid == other.pid

            and self.description == other.description
        )

    # =====================================================
    # String
    # =====================================================

    def __str__(self):

        if not self.connected:

            return "No Device Connected"

        return (
            f"{self.display_name} | "
            f"{self.state.value} | "
            f"{self.com_port}"
        )