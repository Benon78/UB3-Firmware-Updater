"""
=========================================================
UB3 Firmware Updater

DFU Service

Developer:
Benjamin William
=========================================================
"""

import subprocess
import time
from pathlib import Path


class DFUService:

    def __init__(self):

        self.tools = (
            Path(__file__).parent.parent
            / "resources"
            / "tools"
        )

        self.dfu_util = self.tools / "dfu-util.exe"

    # -------------------------------------------------

    def detect(self):

        """
        Detect STM32 DFU device.
        """

        try:

            result = subprocess.run(

                [str(self.dfu_util), "-l"],

                capture_output=True,

                text=True,

            )

            output = result.stdout.upper()

            if "1EAF" in output:

                return True

            return False

        except Exception:

            return False

    def wait_for_device(self,timeout=8,):

        start = time.time()

        while time.time() - start < timeout:

            if self.detect():

                return True

            time.sleep(0.25)

        return False
        
    def flash_firmware(self, firmware):

        command = [

            str(self.dfu_util),

            "-a",

            "2",

            "-d",

            "1EAF:0003",

            "-D",

            str(firmware),

        ]

        try:

            result = subprocess.run(

                command,

                capture_output=True,

                text=True,

            )

            if result.returncode == 0:

                return True, "Firmware uploaded successfully."

            return False, result.stderr

        except Exception as e:

            return False, str(e)