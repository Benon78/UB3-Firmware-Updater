import bootstrap

from ub3_updater.models.device import Device
from ub3_updater.models.device import DeviceState

device = Device(
    connected=True,
    state=DeviceState.RUNTIME,
    com_port="COM3",
    firmware="1.00",
    usb_name="STM32 Virtual COM Port",
)

print(device)

print(device.is_runtime)

print(device.to_dict())