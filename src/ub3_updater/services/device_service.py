"""
=========================================================
UB3 Firmware Updater

Device Service

Developer:
Benjamin William
=========================================================
"""

from dataclasses import dataclass


@dataclass
class DeviceInfo:

    connected: bool

    com_port: str

    board: str

    dfu: str

    firmware: str


class DeviceService:

    """
    Handles all communication with UB3 hardware.

    Future versions will automatically detect

    • COM Port

    • STM32 Board

    • DFU Bootloader

    • Firmware Version

    """

    def __init__(self):

        pass

    # --------------------------------------

    def get_device(self):

        """
        Temporary implementation.

        Later this function will detect
        the actual hardware.
        """

        return DeviceInfo(

            connected=False,

            com_port="--",

            board="--",

            dfu="Not Available",

            firmware="--",

        )