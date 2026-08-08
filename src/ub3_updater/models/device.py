"""
=========================================================
UB3 Device Manager

Device Model

Developer:
Benjamin William

Description:
Represents a detected UB3 device.

This model is shared between:

• Device Service
• Device Monitor
• Upload Service
• Logger Service
• UI

Version:
0.3.0
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


# ---------------------------------------------------------
# Device State
# ---------------------------------------------------------

class DeviceState(Enum):
    DISCONNECTED = "Disconnected"
    RUNTIME = "Runtime"
    DFU = "DFU Bootloader"
    UNKNOWN = "Unknown"


# ---------------------------------------------------------
# Device Model
# ---------------------------------------------------------

@dataclass(slots=True)
class Device:

    # ----------------------------
    # Status
    # ----------------------------

    connected: bool = False

    state: DeviceState = DeviceState.DISCONNECTED

    # ----------------------------
    # USB
    # ----------------------------

    com_port: str = "--"

    vid: str = ""

    pid: str = ""

    manufacturer: str = ""

    description: str = ""

    hwid: str = ""

    # ----------------------------
    # UB3 Information
    # ----------------------------

    board: str = "--"

    firmware: str = "Unknown"

    serial_number: str = "--"

    usb_name: str = "--"

    # ----------------------------
    # Detection Time
    # ----------------------------

    last_seen: datetime | None = None

    # =====================================================
    # Properties
    # =====================================================

    @property
    def is_connected(self) -> bool:
        return self.connected

    @property
    def is_runtime(self) -> bool:
        return self.state == DeviceState.RUNTIME

    @property
    def is_dfu(self) -> bool:
        return self.state == DeviceState.DFU

    @property
    def display_name(self) -> str:

        if self.usb_name != "--":
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

        if self.last_seen is not None:
            data["last_seen"] = self.last_seen.isoformat()

        return data

    @classmethod
    def from_dict(cls, data):

        state = DeviceState(data.get("state", "Disconnected"))

        last_seen = data.get("last_seen")

        if last_seen:
            last_seen = datetime.fromisoformat(last_seen)

        return cls(
            connected=data.get("connected", False),
            state=state,
            com_port=data.get("com_port", "--"),
            vid=data.get("vid", ""),
            pid=data.get("pid", ""),
            manufacturer=data.get("manufacturer", ""),
            description=data.get("description", ""),
            hwid=data.get("hwid", ""),
            board=data.get("board", "--"),
            firmware=data.get("firmware", "Unknown"),
            serial_number=data.get("serial_number", "--"),
            usb_name=data.get("usb_name", "--"),
            last_seen=last_seen,
        )

    # =====================================================
    # String Representation
    # =====================================================

    def __str__(self):

        if not self.connected:
            return "No Device Connected"

        return (
            f"{self.display_name} | "
            f"{self.state.value} | "
            f"{self.com_port}"
        )