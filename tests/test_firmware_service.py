import bootstrap

from ub3_updater.services.firmware_service import FirmwareService


service = FirmwareService()

print("=" * 70)
print("FIRMWARE SERVICE TEST")
print("=" * 70)

print()
print("Firmware Root:")
print(service.firmware_root)

print()
print("Scanning firmware...")

firmwares = service.scan()

print()
print(f"Firmware count: {len(firmwares)}")

print()

for firmware in firmwares:

    print("-" * 70)

    print("Name      :", firmware.name)
    print("Version   :", firmware.version)
    print("Filename  :", firmware.filename)
    print("Path      :", firmware.path)
    print("Size      :", firmware.size)
    print("Size (MB) :", round(firmware.size_mb, 3))
    print("Extension :", firmware.extension)
    print("Exists    :", firmware.exists)

print()
print("=" * 70)

default = service.get_default()

print("Default Firmware:")

if default:

    print(default)

else:

    print("No default firmware found.")