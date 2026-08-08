import bootstrap

from pathlib import Path

from ub3_updater.models.device import (
    Device,
    DeviceState,
)

from ub3_updater.models.firmware import (
    Firmware,
)

from ub3_updater.services.upload_service import (
    UploadService,
)


print("=" * 70)
print("UPLOAD SERVICE TEST")
print("=" * 70)


service = UploadService(
    uploader_path=Path(
        r"C:\Benon\Personal\Set_UP\Arduino\hardware"
        r"\Arduino_STM32\Arduino_STM32-master"
        r"\tools\win\maple_upload.bat"
    )
)


# =========================================================
# Test Device
# =========================================================

device = Device(
    connected=True,
    state=DeviceState.MAPLE_SERIAL,
    com_port="COM3",
    usb_name="Maple Serial (COM3)",
    description="Maple Serial (COM3)",
    vid="1EAF",
    pid="0004",
)


# =========================================================
# Test Firmware
# =========================================================

firmware = Firmware(
    name="ZNA2US",
    version="1.00",
    filename=(
        "UnlockBoxIII_260123_"
        "ZNA2US-WWDG2d_1.00.ino."
        "generic_stm32f103r.bin"
    ),
    path=(
        "resources/firmware/ZNA2US/"
        "UnlockBoxIII_260123_"
        "ZNA2US-WWDG2d_1.00.ino."
        "generic_stm32f103r.bin"
    ),
)


# =========================================================
# Build Command
# =========================================================

command = service.build_command(
    device=device,
    firmware=firmware,
)


print()
print("Generated command:")
print()

for index, argument in enumerate(command):

    print(
        f"[{index}] {argument}"
    )


print()
print("=" * 70)

print("Expected parameters:")
print(
    "COM port   :",
    device.com_port,
)

print(
    "ALT ID     :",
    service.MAPLE_ALT_ID,
)

print(
    "DFU ID     :",
    service.MAPLE_DFU_ID,
)

print(
    "Firmware   :",
    firmware.path,
)

print("=" * 70)