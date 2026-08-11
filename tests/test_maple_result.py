import bootstrap

from ub3_updater.models.upload_result import (
    UploadStatus,
)

from ub3_updater.services.upload_service import (
    UploadService,
)

from ub3_updater.utils.process_runner import (
    ProcessResult,
)


service = UploadService()


print("=" * 70)
print("MAPLE RESULT INTERPRETER TEST")
print("=" * 70)


# =========================================================
# TEST 1
# Successful upload + USB reset warning
# =========================================================

process = ProcessResult(
    command=[
        "cmd.exe",
        "/d",
        "/c",
        "call",
        "maple_upload.bat",
        "COM3",
        "2",
        "1EAF:003",
        r"C:\tmp\firmware.bin",
    ],

    return_code=0,

    stdout="""
maple_loader v0.1
Resetting to bootloader via DTR pulse
Searching for DFU device [1EAF:003]...
Found it!
Opening USB Device 0x1eaf:0x0003...
Starting download: [##################################################] finished!
Done!
Resetting USB to switch back to runtime mode
error resetting after download: usb_reset: could not reset device
""",

    stderr="""
Reset via USB Serial Failed! Did you select the right serial port?
Assuming the board is in perpetual bootloader mode and continuing...
""",

    started=True,

    duration_seconds=18.469,
)


status, message, warning = (
    service._evaluate_maple_result(
        process
    )
)


print()
print("TEST 1 - SUCCESS WITH WARNING")
print("Status  :", status)
print("Message :", message)
print("Warning :", warning)

assert (
    status
    == UploadStatus.SUCCESS_WITH_WARNING
), (
    "Expected SUCCESS_WITH_WARNING, "
    f"got {status}"
)


# =========================================================
# TEST 2
# Completely successful upload
# =========================================================

process = ProcessResult(
    command=[
        "cmd.exe",
        "/d",
        "/c",
        "call",
        "maple_upload.bat",
        "COM3",
        "2",
        "1EAF:003",
        r"C:\tmp\firmware.bin",
    ],

    return_code=0,

    stdout="""
maple_loader v0.1
Searching for DFU device [1EAF:003]...
Found it!
Starting download: [##################################################] finished!
Done!
Resetting USB to switch back to runtime mode
""",

    stderr="",

    started=True,

    duration_seconds=18.0,
)


status, message, warning = (
    service._evaluate_maple_result(
        process
    )
)


print()
print("TEST 2 - SUCCESS")
print("Status  :", status)
print("Message :", message)
print("Warning :", warning)

assert (
    status
    == UploadStatus.SUCCESS
), (
    "Expected SUCCESS, "
    f"got {status}"
)
assert warning == "", (
    "Normal Maple runtime reset message must not "
    f"produce a warning; got: {warning}"
)


# =========================================================
# TEST 3
# DFU device not found
# =========================================================

process = ProcessResult(
    command=[
        "cmd.exe",
        "/d",
        "/c",
        "call",
        "maple_upload.bat",
        "COM3",
        "2",
        "1EAF:003",
        r"C:\tmp\firmware.bin",
    ],

    return_code=1,

    stdout="""

Searching for DFU device [1EAF:003]...
""",

    stderr="""
No DFU device found
""",

    started=True,

    duration_seconds=5.0,
)


status, message, warning = (
    service._evaluate_maple_result(
        process
    )
)


print()
print("TEST 3 - DFU NOT FOUND")
print("Status  :", status)
print("Message :", message)
print("Warning :", warning)

assert (
    status
    == UploadStatus.FAILED
), (
    "Expected FAILED, "
    f"got {status}"
)


# =========================================================
# TEST 4
# Java exception
# =========================================================

process = ProcessResult(
    command=[
        "cmd.exe",
        "/d",
        "/c",
        "call",
        "maple_upload.bat",
        "COM3",
        "2",
        "1EAF:003",
        r"C:\tmp\firmware.bin",
    ],

    return_code=0,

    stdout="",

    stderr="""
Exception in thread "main"
java.lang.ArrayIndexOutOfBoundsException
""",

    started=True,

    duration_seconds=1.0,
)


status, message, warning = (
    service._evaluate_maple_result(
        process
    )
)


print()
print("TEST 4 - JAVA EXCEPTION")
print("Status  :", status)
print("Message :", message)
print("Warning :", warning)

assert (
    status
    == UploadStatus.FAILED
), (
    "Expected FAILED, "
    f"got {status}"
)


# =========================================================
# FINAL
# =========================================================

print()
print("=" * 70)
print("ALL TESTS PASSED")
print("=" * 70)