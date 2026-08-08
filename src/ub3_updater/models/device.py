"""
=========================================================
UB3 Firmware Updater

Device Model

Developer:
Benjamin William
=========================================================
"""

from dataclasses import dataclass


@dataclass
class Device:

    connected: bool = False

    com_port: str = "--"

    board: str = "--"

    dfu: str = "Not Available"

    firmware: str = "--"

    serial_number: str = "--"

    usb_name: str = "--"