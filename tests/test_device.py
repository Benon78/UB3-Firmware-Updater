import bootstrap

from datetime import datetime

from ub3_updater.models.device import Device
from ub3_updater.models.device import DeviceState


device = Device(
    connected=True,
    state=DeviceState.MAPLE_SERIAL,
    com_port="COM3",
    usb_name="Maple Serial (COM3)",
    description="Maple Serial (COM3)",
    manufacturer="LeafLabs",
    vid="1EAF",
    pid="0004",
    hwid="USB VID:PID=1EAF:0004",
    detected_at=datetime.now(),
)

print("=" * 50)
print(device)
print("=" * 50)

print("Connected :", device.is_connected)
print("Maple     :", device.is_maple)
print("USBSerial :", device.is_usb_serial)

print("\nDictionary")
print(device.to_dict())

print("\nComparison")

device2 = Device(
    connected=True,
    state=DeviceState.MAPLE_SERIAL,
    com_port="COM3",
    usb_name="Maple Serial (COM3)",
    description="Maple Serial (COM3)",
    manufacturer="LeafLabs",
    vid="1EAF",
    pid="0004",
)

print(device.same_device(device2))