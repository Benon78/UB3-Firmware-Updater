"""
=========================================================
UB3 Firmware Updater

Device Service

Developer:
Benjamin William
=========================================================
"""
from ub3_updater.models.device import Device
from ub3_updater.utils.usb_helper import (
    enumerate_ports,
    port_to_dict,
)

from ub3_updater.constants.usb_ids import (
    STM32_RUNTIME_VENDOR,
    KNOWN_DEVICE_NAMES,
)


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

        ports = enumerate_ports()

        for port in ports:

            info = port_to_dict(port)

            vendor = ""

            if info["vid"] is not None:
                vendor = f"{info['vid']:04X}"

            description = info["description"] or ""

            manufacturer = info["manufacturer"] or ""

            hwid = info["hwid"] or ""

            # ---------------------------------
            # Detect STM32 Runtime Device
            # ---------------------------------

            if vendor == STM32_RUNTIME_VENDOR:

                return Device(

                    connected=True,

                    com_port=info["device"],

                    board="STM32",

                    dfu="Runtime",

                    firmware="Unknown",

                    serial_number=info["serial_number"] or "--",

                    usb_name=description,

                )

            # ---------------------------------
            # Detect by Description
            # ---------------------------------

            if any(name.lower() in description.lower()
                for name in KNOWN_DEVICE_NAMES):

                return Device(

                    connected=True,

                    com_port=info["device"],

                    board="STM32",

                    dfu="Runtime",

                    firmware="Unknown",

                    serial_number=info["serial_number"] or "--",

                    usb_name=description,

                )

            # ---------------------------------
            # Detect Maple Bootloader
            # ---------------------------------

            if "1EAF" in hwid.upper():

                return Device(

                    connected=True,

                    com_port=info["device"],

                    board="STM32",

                    dfu="Bootloader",

                    firmware="Unknown",

                    serial_number=info["serial_number"] or "--",

                    usb_name=description,

                )

        return Device()