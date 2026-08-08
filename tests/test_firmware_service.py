import bootstrap

from ub3_updater.services.firmware_service import (
    FirmwareService,
)


service = FirmwareService()

print("=" * 70)
print("FIRMWARE SERVICE TEST")
print("=" * 70)

firmwares = service.scan()

print()
print("Repository:", service.firmware_root)

print(
    "Firmware count:",
    len(firmwares),
)

print()

for firmware in firmwares:

    print("-" * 70)

    print("Name        :", firmware.name)
    print("Version     :", firmware.version)
    print("Release     :", firmware.release_date)
    print("Description :", firmware.description)
    print("Target      :", firmware.target_device)
    print("Hardware    :", firmware.hardware)
    print("Filename    :", firmware.filename)
    print("Path        :", firmware.path)
    print("Metadata    :", firmware.metadata_path)
    print("Size        :", firmware.size)
    print("Valid file  :", firmware.is_valid_file())

print()
print("=" * 70)

print("Errors:")

errors = service.get_errors()

if errors:

    for error in errors:

        print("-", error)

else:

    print("None")

print()
print("=" * 70)

default = service.get_default()

print("Default firmware:")

if default:

    print(default)

else:

    print("None")