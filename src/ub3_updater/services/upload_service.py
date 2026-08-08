"""
=========================================================
UB3 Firmware Updater

Upload Service

Developer:
Benjamin William
=========================================================
"""

import subprocess
from pathlib import Path

from ub3_updater.services.serial_service import SerialService
from ub3_updater.services.dfu_service import DFUService


class UploadService:

    def __init__(self):

        self.serial = SerialService()

        self.dfu = DFUService()

    # ---------------------------------------------------

    def upload(self, com_port, firmware_path):

        """
        Complete firmware upload sequence.
        """

        # Step 1

        if not self.serial.reset_to_bootloader(com_port):

            return False, "Failed to reset UB3."

        # Step 2

        if not self.dfu.wait_for_device():

            return False, "DFU device not detected."

        # Step 3

        success, message = self.dfu.flash_firmware(
            firmware_path
        )

        return success, message