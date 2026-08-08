import bootstrap

from ub3_updater.services.device_service import DeviceService

service = DeviceService()

device = service.scan()

print("=" * 60)

print(device)

print("=" * 60)

print(device.to_dict())

print()

print("Connected :", service.is_connected())

print("Maple     :", service.is_maple())

print("Bootloader:", service.is_bootloader())