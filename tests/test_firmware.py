import bootstrap

from ub3_updater.models.firmware import Firmware


firmware = Firmware(
    name="ZNA2US",
    version="1.00",
    filename="UnlockBoxIII_260123_ZNA2US-WWDG2d_1.00.bin",
    path="resources/firmware/ZNA2US/"
          "UnlockBoxIII_260123_ZNA2US-WWDG2d_1.00.bin",
    size=1024 * 512,
    checksum="",
)


print("=" * 60)
print("FIRMWARE MODEL TEST")
print("=" * 60)

print("Name        :", firmware.name)
print("Version     :", firmware.version)
print("Display     :", firmware.display_name)
print("Filename    :", firmware.filename)
print("Extension   :", firmware.extension)
print("Size        :", firmware.size)
print("Size (MB)   :", firmware.size_mb)
print("Path        :", firmware.path)
print("Exists      :", firmware.exists)

print()
print("Dictionary:")
print(firmware.to_dict())