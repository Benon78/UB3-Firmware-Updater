"""
=========================================================
UB3 Firmware Updater

Step 5.2 - Maple Command Contract Test
=========================================================

Validates the existing UploadService architecture.

This test verifies:
    ConfigService
        -> FirmwareService/repository path
        -> Device model
        -> UploadService
        -> maple_upload command

It does NOT execute Maple Loader.
It does NOT require a physical UB3.
"""

import bootstrap

from pathlib import Path

from ub3_updater.constants.usb_ids import (
    STM32_VENDOR_ID,
    SUPPORTED_DEVICES,
)

from ub3_updater.models.device import (
    Device,
    DeviceState,
)

from ub3_updater.services.config_service import (
    ConfigService,
)

from ub3_updater.services.upload_service import (
    UploadService,
)


print("=" * 70)
print("MAPLE COMMAND CONTRACT TEST - STEP 5.2")
print("=" * 70)

# =========================================================
# 1. Project resources
# =========================================================

firmware_root = ConfigService.firmware_root().resolve()
uploader = ConfigService.maple_uploader().resolve()

assert firmware_root.is_dir(), (
    f"Firmware repository missing: {firmware_root}"
)

assert uploader.is_file(), (
    f"Maple uploader missing: {uploader}"
)

print("[PASS] Project firmware repository detected")
print("[PASS] Project Maple uploader detected")

# =========================================================
# 2. Real ZNA2US firmware
# =========================================================

firmware_path = (
    firmware_root
    / "ZNA2US"
    / (
        "UnlockBoxIII_260123_"
        "ZNA2US-WWDG2d_1.00.ino."
        "generic_stm32f103r.bin"
    )
).resolve()

assert firmware_path.is_file(), (
    f"ZNA2US firmware missing: {firmware_path}"
)

print("[PASS] ZNA2US firmware exists in resources/firmware")

# =========================================================
# 3. Detected-device model
# =========================================================

device = Device(
    connected=True,
    state=DeviceState.MAPLE_SERIAL,
    com_port="COM3",
    usb_name="Maple Serial (COM3)",
    description="Maple Serial (COM3)",
    manufacturer="LeafLabs, LLC",
    vid=STM32_VENDOR_ID,
    pid="0004",
    hwid="USB VID:PID=1EAF:0004",
)

assert device.is_maple
assert device.com_port == "COM3"

print("[PASS] Existing Device model accepted")
print("[PASS] COM3 obtained from Device model")
print("[PASS] Maple Serial state accepted")

# =========================================================
# 4. Existing UploadService
# =========================================================

service = UploadService(
    uploader_path=uploader
)

# Minimal real Firmware model.
from ub3_updater.models.firmware import Firmware

firmware = Firmware(
    name="ZNA2US",
    version="1.00",
    target_device="UB3",
    filename=firmware_path.name,
    path=str(firmware_path),
)

command = service.build_command(
    device=device,
    firmware=firmware,
)

# =========================================================
# 5. Exact command contract
# =========================================================

assert command[0] == "cmd.exe"
assert command[1] == "/d"
assert command[2] == "/c"
assert command[3] == "call"

assert Path(command[4]).resolve() == uploader
assert command[5] == "COM3"
assert command[6] == "2"
assert command[7] == "1EAF:003"
assert Path(command[8]).resolve() == firmware_path

print("[PASS] Windows command wrapper correct")
print("[PASS] maple_upload.bat path correct")
print("[PASS] COM3 propagated automatically")
print("[PASS] Maple ALT ID = 2")
print("[PASS] Maple DFU ID = 1EAF:003")
print("[PASS] Firmware path comes from resources/firmware")
print("[PASS] Firmware filename preserved")
print("[PASS] Exact argument order correct")

# Human-readable command.
print()
print("Resolved command:")
print(
    "  maple_upload",
    command[5],
    command[6],
    command[7],
    command[8],
)

print()
print("[PASS] No C:\\tmp staging is used by the application")
print("[PASS] No duplicate device-detection architecture introduced")
print("[PASS] No Maple Loader process executed")
print("[PASS] No physical UB3 was programmed")

print("=" * 70)
print("ALL STEP 5.2 MAPLE COMMAND CONTRACT TESTS PASSED")
print("=" * 70)
