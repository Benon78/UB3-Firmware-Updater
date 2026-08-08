"""
USB Helper Functions
"""

import serial.tools.list_ports


def enumerate_ports():

    return list(serial.tools.list_ports.comports())


def port_to_dict(port):

    return {

        "device": port.device,

        "description": port.description,

        "manufacturer": port.manufacturer,

        "serial_number": port.serial_number,

        "vid": port.vid,

        "pid": port.pid,

        "hwid": port.hwid,

    }