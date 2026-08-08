import bootstrap

from ub3_updater.models.upload_result import (
    UploadResult,
    UploadStatus,
)


print("=" * 70)
print("UPLOAD RESULT TEST")
print("=" * 70)


# ---------------------------------------------------------
# Success
# ---------------------------------------------------------

success = UploadResult.success_result(
    firmware_name="ZNA2US",
    firmware_version="1.00",
    com_port="COM3",
    return_code=0,
    duration_seconds=12.4,
)

print()
print("SUCCESS")
print(success)
print(success.to_dict())


# ---------------------------------------------------------
# Device Not Ready
# ---------------------------------------------------------

device = UploadResult.device_not_ready(
    "UB3 must be connected in Maple Serial mode."
)

print()
print("DEVICE NOT READY")
print(device)
print("Success:", device.success)
print("Failed :", device.failed)


# ---------------------------------------------------------
# Firmware Invalid
# ---------------------------------------------------------

firmware = UploadResult.firmware_invalid(
    "Firmware file does not exist."
)

print()
print("FIRMWARE INVALID")
print(firmware)
print("Success:", firmware.success)
print("Failed :", firmware.failed)


# ---------------------------------------------------------
# Timeout
# ---------------------------------------------------------

timeout = UploadResult.timeout_result(
    "Firmware update timed out."
)

print()
print("TIMEOUT")
print(timeout)
print("Success:", timeout.success)
print("Failed :", timeout.failed)


# ---------------------------------------------------------
# Serialization
# ---------------------------------------------------------

data = success.to_dict()

restored = UploadResult.from_dict(data)

print()
print("SERIALIZATION")
print("Original :", success)
print("Restored :", restored)

print()
print("Status:", restored.status)
print(
    "Status type:",
    type(restored.status),
)

print()
print("=" * 70)

# =========================================================
# TEST 5 - Serialization round trip
# =========================================================

original = UploadResult.success_with_warning_result(
    message="Firmware programmed successfully.",
    warning=(
        "USB reset after download could not "
        "be completed automatically."
    ),
    firmware_name="ZNA2US",
    firmware_version="1.00",
    com_port="COM3",
    duration_seconds=18.469,
)

data = original.to_dict()

restored = UploadResult.from_dict(
    data
)

print()
print("SERIALIZATION")

print("Original :", original.status)
print("Restored :", restored.status)

print(
    "Firmware :",
    restored.firmware_name
)

print(
    "Version  :",
    restored.firmware_version
)

print(
    "COM Port :",
    restored.com_port
)

print(
    "Warning  :",
    restored.warning
)

print(
    "Success  :",
    restored.success
)

print(
    "Has Warn :",
    restored.has_warning
)