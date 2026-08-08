"""
=========================================================
UB3 Firmware Updater

REAL UploadService Integration Test

WARNING
-------
This test performs a REAL firmware update.

It communicates with the physical UB3.

The UB3 must initially be in:

    Maple Serial
    VID:PID = 1EAF:0004

DO NOT manually switch the UB3 to USB Serial Device /
bootloader mode.

Maple Loader performs the DTR reset automatically.

=========================================================
"""

from pathlib import Path

import bootstrap

from ub3_updater.models.firmware import (
    Firmware,
)

from ub3_updater.models.upload_result import (
    UploadStatus,
)

from ub3_updater.services.device_service import (
    DeviceService,
)

from ub3_updater.services.firmware_service import (
    FirmwareService,
)

from ub3_updater.services.upload_service import (
    UploadService,
)

from ub3_updater.utils.process_runner import (
    ProcessRunner,
)


# =========================================================
# PROJECT CONFIGURATION
# =========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


# =========================================================
# MAPLE UPLOADER
# =========================================================

MAPLE_UPLOADER = Path(
    r"C:\Benon\Personal\Set_UP\Arduino"
    r"\hardware\Arduino_STM32"
    r"\Arduino_STM32-master"
    r"\tools\win\maple_upload.bat"
)


# =========================================================
# FIRMWARE
# =========================================================

FIRMWARE_PATH = (
    PROJECT_ROOT
    / "resources"
    / "firmware"
    / "ZNA2US"
    / "UnlockBoxIII_260123_ZNA2US-WWDG2d_1.00"
    ".ino.generic_stm32f103r.bin"
)


FIRMWARE_NAME = "ZNA2US"

FIRMWARE_VERSION = "1.00"


# =========================================================
# HEADER
# =========================================================

print()
print("=" * 70)
print("UB3 REAL UPLOAD SERVICE TEST")
print("=" * 70)


# =========================================================
# VALIDATE MAPLE UPLOADER
# =========================================================

print()
print("Maple uploader:")
print(MAPLE_UPLOADER)

print(
    "Uploader exists :",
    MAPLE_UPLOADER.exists(),
)


if not MAPLE_UPLOADER.exists():

    print()
    print("ERROR:")
    print(
        "Maple uploader was not found."
    )

    print()
    print(
        "Expected:"
    )

    print(
        MAPLE_UPLOADER
    )

    raise SystemExit(1)


# =========================================================
# VALIDATE FIRMWARE
# =========================================================

print()
print("Firmware:")
print(FIRMWARE_PATH)

print(
    "Firmware exists :",
    FIRMWARE_PATH.exists(),
)


if not FIRMWARE_PATH.exists():

    print()
    print("ERROR:")
    print(
        "Firmware file was not found."
    )

    print()
    print(
        "Expected:"
    )

    print(
        FIRMWARE_PATH
    )

    raise SystemExit(1)


# =========================================================
# CREATE FIRMWARE MODEL
# =========================================================

firmware = Firmware(
    name=FIRMWARE_NAME,
    version=FIRMWARE_VERSION,
    path=str(FIRMWARE_PATH),
)


print()
print("Selected firmware:")
print(
    "  Name    :",
    firmware.name,
)

print(
    "  Version :",
    firmware.version,
)

print(
    "  File    :",
    FIRMWARE_PATH.name,
)


# =========================================================
# CREATE SERVICES
# =========================================================

device_service = DeviceService()

firmware_service = FirmwareService()

process_runner = ProcessRunner()


upload_service = UploadService(
    device_service=device_service,
    firmware_service=firmware_service,
    process_runner=process_runner,
    uploader_path=MAPLE_UPLOADER,
)


# =========================================================
# DEVICE DETECTION
# =========================================================

print()
print("=" * 70)
print("DEVICE DETECTION")
print("=" * 70)

print()
print(
    "Scanning for UB3..."
)


device = device_service.scan()


# =========================================================
# DEVICE NOT FOUND
# =========================================================

if device is None:

    print()
    print(
        "No device detected."
    )

    print()
    print(
        "Connect the UB3 and make sure it appears as:"
    )

    print(
        "    Maple Serial"
    )

    print(
        "    VID:PID = 1EAF:0004"
    )

    raise SystemExit(1)


# =========================================================
# DISPLAY DEVICE
# =========================================================

print()
print("Detected device:")

print(
    "  USB Name    :",
    device.usb_name,
)

print(
    "  State       :",
    device.state,
)

print(
    "  COM Port    :",
    device.com_port,
)

print(
    "  VID         :",
    device.vid,
)

print(
    "  PID         :",
    device.pid,
)

print(
    "  Description :",
    device.description,
)

print(
    "  Manufacturer:",
    device.manufacturer,
)


# =========================================================
# DEVICE VALIDATION
# =========================================================

print()
print("=" * 70)
print("DEVICE VALIDATION")
print("=" * 70)

print()


# ---------------------------------------------------------
# Connected
# ---------------------------------------------------------

if not device.connected:

    print(
        "[FAIL] Device is not connected."
    )

    raise SystemExit(1)


print(
    "[PASS] Device is connected"
)


# ---------------------------------------------------------
# Maple Serial
# ---------------------------------------------------------

if not device.is_maple:

    print(
        "[FAIL] UB3 is not in Maple Serial mode."
    )

    print()

    print(
        "Current state :",
        device.state,
    )

    print(
        "Current port  :",
        device.com_port,
    )

    print(
        "VID           :",
        device.vid,
    )

    print(
        "PID           :",
        device.pid,
    )

    print()

    print(
        "Required state:"
    )

    print(
        "    Maple Serial"
    )

    print(
        "    VID:PID = 1EAF:0004"
    )

    print()

    print(
        "Do NOT manually switch the UB3 to "
        "USB Serial Device."
    )

    raise SystemExit(1)


print(
    "[PASS] UB3 is in Maple Serial mode"
)


# ---------------------------------------------------------
# VID
# ---------------------------------------------------------

if device.vid.upper() != "1EAF":

    print(
        "[FAIL] Unexpected USB VID:",
        device.vid,
    )

    raise SystemExit(1)


print(
    "[PASS] USB VID = 1EAF"
)


# ---------------------------------------------------------
# PID
# ---------------------------------------------------------

if device.pid.upper() != "0004":

    print(
        "[FAIL] Unexpected USB PID:",
        device.pid,
    )

    raise SystemExit(1)


print(
    "[PASS] USB PID = 0004"
)


# ---------------------------------------------------------
# COM port
# ---------------------------------------------------------

if not device.com_port:

    print(
        "[FAIL] No COM port detected."
    )

    raise SystemExit(1)


print(
    "[PASS] COM port automatically detected:",
    device.com_port,
)


# =========================================================
# FIRMWARE INFORMATION
# =========================================================

print()
print("=" * 70)
print("SELECTED FIRMWARE")
print("=" * 70)

print()

print(
    "Name    :",
    firmware.name,
)

print(
    "Version :",
    firmware.version,
)

print(
    "File    :",
    FIRMWARE_PATH.name,
)


# =========================================================
# REAL UPDATE WARNING
# =========================================================

print()
print("=" * 70)
print("WARNING")
print("=" * 70)

print()

print(
    "The next operation will ACTUALLY update"
)

print(
    "the connected UB3 firmware."
)

print()

print(
    "Current device:"
)

print(
    f"    Maple Serial ({device.com_port})"
)

print(
    f"    VID:PID = {device.vid}:{device.pid}"
)

print()

print(
    "Firmware:"
)

print(
    f"    {firmware.name}"
)

print(
    f"    Version {firmware.version}"
)

print()

print(
    "IMPORTANT:"
)

print(
    "Do NOT manually switch the UB3 into"
)

print(
    "USB Serial Device / flash mode."
)

print()

print(
    "Maple Loader will perform the DTR reset."
)

print()


# =========================================================
# FINAL CONFIRMATION
# =========================================================

print("=" * 70)

confirmation = input(
    "Type UPDATE to start the REAL firmware update: "
)


if confirmation.strip().upper() != "UPDATE":

    print()
    print(
        "Operation cancelled by operator."
    )

    raise SystemExit(0)


# =========================================================
# START REAL UPLOAD
# =========================================================

print()
print("=" * 70)
print("STARTING REAL FIRMWARE UPDATE")
print("=" * 70)

print()

print(
    f"Device : Maple Serial ({device.com_port})"
)

print(
    f"Firmware: {firmware.name} {firmware.version}"
)

print()

print(
    "Starting UploadService.upload()..."
)

print()


# =========================================================
# ACTUAL UPLOAD
# =========================================================

try:

    result = upload_service.upload(
        firmware
    )

except KeyboardInterrupt:

    print()
    print(
        "Upload interrupted by operator."
    )

    raise SystemExit(130)

except Exception as exc:

    print()
    print("=" * 70)
    print("UNEXPECTED UPLOAD ERROR")
    print("=" * 70)

    print()
    print(
        type(exc).__name__
    )

    print(
        str(exc)
    )

    raise


# =========================================================
# UPLOAD RESULT
# =========================================================

print()
print("=" * 70)
print("UPLOAD RESULT")
print("=" * 70)

print()

print(
    "Status       :",
    result.status,
)

print(
    "Success      :",
    result.success,
)

print(
    "Failed       :",
    result.failed,
)

print(
    "Has Warning  :",
    result.has_warning,
)

print(
    "Message      :",
    result.message,
)

print(
    "Warning      :",
    result.warning,
)

print(
    "Error        :",
    result.error,
)

print(
    "COM Port     :",
    result.com_port,
)

print(
    "Firmware     :",
    result.firmware_name,
)

print(
    "Version      :",
    result.firmware_version,
)

print(
    "Return Code  :",
    result.return_code,
)

print(
    "Timed Out    :",
    result.timed_out,
)

print(
    "Cancelled    :",
    result.cancelled,
)

print(
    "Duration     :",
    result.duration_seconds,
)


# =========================================================
# COMMAND
# =========================================================

print()
print("=" * 70)
print("EXECUTED COMMAND")
print("=" * 70)

print()

if result.command:

    for index, argument in enumerate(
        result.command
    ):

        print(
            f"[{index}] {argument}"
        )

else:

    print(
        "No command recorded."
    )


# =========================================================
# FINAL INTERPRETATION
# =========================================================

print()
print("=" * 70)
print("FINAL INTERPRETATION")
print("=" * 70)

print()


# ---------------------------------------------------------
# SUCCESS
# ---------------------------------------------------------

if (
    result.status
    == UploadStatus.SUCCESS
):

    print(
        "SUCCESS"
    )

    print()

    print(
        "Firmware programming completed successfully."
    )

    print()

    print(
        "The UB3 should now be running the new firmware."
    )


# ---------------------------------------------------------
# SUCCESS WITH WARNING
# ---------------------------------------------------------

elif (
    result.status
    == UploadStatus.SUCCESS_WITH_WARNING
):

    print(
        "SUCCESS WITH WARNING"
    )

    print()

    print(
        "Firmware programming completed successfully."
    )

    print()

    print(
        "Post-upload warning:"
    )

    print(
        result.warning
    )

    print()

    print(
        "The USB reset warning occurred after the"
    )

    print(
        "firmware transfer had already completed."
    )


# ---------------------------------------------------------
# CANCELLED
# ---------------------------------------------------------

elif (
    result.status
    == UploadStatus.CANCELLED
):

    print(
        "CANCELLED"
    )

    print()

    print(
        result.message
    )


# ---------------------------------------------------------
# TIMEOUT
# ---------------------------------------------------------

elif (
    result.status
    == UploadStatus.TIMEOUT
):

    print(
        "TIMEOUT"
    )

    print()

    print(
        result.message
    )


# ---------------------------------------------------------
# DEVICE NOT READY
# ---------------------------------------------------------

elif (
    result.status
    == UploadStatus.DEVICE_NOT_READY
):

    print(
        "DEVICE NOT READY"
    )

    print()

    print(
        result.message
    )


# ---------------------------------------------------------
# FIRMWARE INVALID
# ---------------------------------------------------------

elif (
    result.status
    == UploadStatus.FIRMWARE_INVALID
):

    print(
        "FIRMWARE INVALID"
    )

    print()

    print(
        result.message
    )


# ---------------------------------------------------------
# PROCESS ERROR
# ---------------------------------------------------------

elif (
    result.status
    == UploadStatus.PROCESS_ERROR
):

    print(
        "PROCESS ERROR"
    )

    print()

    print(
        result.message
    )


# ---------------------------------------------------------
# FAILURE
# ---------------------------------------------------------

else:

    print(
        "UPLOAD FAILED"
    )

    print()

    print(
        result.message
    )

    if result.error:

        print()

        print(
            "Error:"
        )

        print(
            result.error
        )


# =========================================================
# COMPLETE
# =========================================================

print()
print("=" * 70)
print("REAL UPLOAD SERVICE TEST COMPLETE")
print("=" * 70)
print()