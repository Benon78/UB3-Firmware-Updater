import bootstrap

from pathlib import Path

from ub3_updater.models.device import DeviceState
from ub3_updater.services.upload_service import UploadService


# =========================================================
# Existing Arduino STM32 uploader
# =========================================================

MAPLE_UPLOAD = Path(
    r"C:\Benon\Personal\Set_UP\Arduino\hardware"
    r"\Arduino_STM32\Arduino_STM32-master"
    r"\tools\win\maple_upload.bat"
)


# =========================================================
# Firmware
# =========================================================

FIRMWARE = Path(
    "resources/firmware/ZNA2US/"
    "UnlockBoxIII_260123_ZNA2US-WWDG2d_1.00.ino."
    "generic_stm32f103r.bin"
)


print("=" * 70)
print("UB3 REAL FIRMWARE UPLOAD TEST")
print("=" * 70)

print()
print("Maple uploader:")
print(MAPLE_UPLOAD)

print()
print("Firmware:")
print(FIRMWARE.resolve())

print()
print("Uploader exists :", MAPLE_UPLOAD.exists())
print("Firmware exists :", FIRMWARE.exists())

if not MAPLE_UPLOAD.exists():
    raise FileNotFoundError(
        f"Maple uploader not found:\n{MAPLE_UPLOAD}"
    )

if not FIRMWARE.exists():
    raise FileNotFoundError(
        f"Firmware not found:\n{FIRMWARE.resolve()}"
    )


# =========================================================
# Create services
# =========================================================

service = UploadService(
    uploader_path=MAPLE_UPLOAD,
    timeout=120,
)


# =========================================================
# Discover firmware
# =========================================================

firmwares = service.firmware_service.scan()

firmware = None

for item in firmwares:

    if item.name.upper() == "ZNA2US":

        firmware = item
        break


if firmware is None:

    raise RuntimeError(
        "ZNA2US firmware was not found by FirmwareService."
    )


print()
print("Selected firmware:")
print("Name    :", firmware.name)
print("Version :", firmware.version)
print("File    :", firmware.filename)


# =========================================================
# Output callbacks
# =========================================================

def on_output(line: str):

    print(f"[MAPLE] {line}")


def on_error(line: str):

    print(f"[MAPLE-ERR] {line}")


# =========================================================
# WARNING
# =========================================================

print()
print("=" * 70)
print("IMPORTANT")
print("=" * 70)

print()
print("The next operation will ACTUALLY update the UB3.")
print()
print("The UB3 must currently show:")
print()
print("    Maple Serial (COM3)")
print("    VID:PID = 1EAF:0004")
print()
print("Do NOT manually put the UB3 into flash mode.")
print()
print("Maple Loader will perform the DTR reset itself.")
print()
print("=" * 70)

input(
    "Press ENTER to start the firmware update, "
    "or Ctrl+C to cancel..."
)


# =========================================================
# Upload
# =========================================================

result = service.upload(
    firmware,
    on_output=on_output,
    on_error=on_error,
)


# =========================================================
# Result
# =========================================================

print()
print("=" * 70)
print("UPLOAD RESULT")
print("=" * 70)

print()
print("Status       :", result.status)
print("Success      :", result.success)
print("Failed       :", result.failed)
print("Message      :", result.message)
print("COM Port     :", result.com_port)
print("Firmware     :", result.firmware_name)
print("Version      :", result.firmware_version)
print("Return Code  :", result.return_code)
print("Timed Out    :", result.timed_out)
print("Cancelled    :", result.cancelled)
print(
    "Duration     :",
    round(result.duration_seconds, 3),
    "seconds",
)

print()
print("Command:")

for index, argument in enumerate(
    result.command or []
):

    print(
        f"[{index}] {argument}"
    )

print()
print("=" * 70)