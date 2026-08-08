import bootstrap

from ub3_updater.services.config_service import ConfigService

print("Application Configuration")
print(ConfigService.app())

print()

print("Settings")
print(ConfigService.settings())

print()

print("Firmware")
print(ConfigService.firmware())