"""
=========================================================
UB3 Firmware Updater

Serial Service

Developer:
Benjamin William
=========================================================
"""

import time
import serial
import serial.tools.list_ports


class SerialService:

    def __init__(self):
        pass

    # -----------------------------------------------------

    def get_ports(self):

        """
        Return all available COM ports.
        """

        return list(serial.tools.list_ports.comports())

    # -----------------------------------------------------

    def reset_to_bootloader(self, com_port):

        """
        Send DTR pulse to place UB3 into DFU mode.
        Equivalent to maple_loader.
        """

        try:

            ser = serial.Serial(com_port)

            ser.dtr = False

            time.sleep(0.10)

            ser.dtr = True

            time.sleep(0.20)

            ser.close()

            return True

        except Exception as e:

            print(e)

            return False