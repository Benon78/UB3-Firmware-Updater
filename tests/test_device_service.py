import bootstrap

from ub3_updater.services.device_service import DeviceService

service = DeviceService()

device = service.scan()

print(device)

print()

print(device.to_dict())