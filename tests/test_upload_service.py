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

from ub3_updater.services.config_service import (
    ConfigService,
)


print("=" * 70)
print("UPLOAD SERVICE TEST")
print("=" * 70)


service = UploadService(
    uploader_path=ConfigService.maple_uploader()
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
    path=str(
        (
            ConfigService.firmware_root()
            / "ZNA2US"
            / (
                "UnlockBoxIII_260123_"
                "ZNA2US-WWDG2d_1.00.ino."
                "generic_stm32f103r.bin"
            )
        ).resolve()
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

# =========================================================
# Step 5.2 Contract
# =========================================================

assert command[0] == "cmd.exe"
assert command[1:4] == ["/d", "/c", "call"]
assert Path(command[4]).resolve() == ConfigService.maple_uploader().resolve()
assert command[5] == "COM3"
assert command[6] == "2"
assert command[7] == "1EAF:003"
assert Path(command[8]).resolve() == Path(firmware.path).resolve()

print("[PASS] Maple command uses detected COM port")
print("[PASS] Maple ALT ID = 2")
print("[PASS] Maple DFU ID = 1EAF:003")
print("[PASS] Firmware path comes from resources/firmware")
print("[PASS] Firmware filename is preserved")
print("[PASS] Exact command contract validated")
print()
print("No Maple Loader was executed.")
print("No physical UB3 was programmed.")
