import bootstrap

from ub3_updater.services.firmware_service import FirmwareService

firmware = FirmwareService.available_firmware()

print()

print(firmware)

print()

print(FirmwareService.get_firmware_file("ZNA2US"))