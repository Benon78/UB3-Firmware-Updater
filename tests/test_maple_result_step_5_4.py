"""
Step 5.4 - Maple completion/result interpretation regression.

No physical UB3 is programmed.
"""

import bootstrap

from ub3_updater.models.upload_result import UploadStatus
from ub3_updater.services.upload_service import UploadService
from ub3_updater.utils.process_runner import ProcessResult


service = UploadService()

print("=" * 70)
print("MAPLE COMPLETION RESULT - STEP 5.4")
print("=" * 70)

def evaluate(stdout, stderr="", return_code=0):
    return service._evaluate_maple_result(
        ProcessResult(
            command=["cmd.exe", "/d", "/c", "call", "maple_upload.bat"],
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
            started=True,
        )
    )

# 1. Normal successful transfer.
status, message, warning = evaluate("""
Starting download: [##################################################] finished!
Done!
Resetting USB to switch back to runtime mode
""")
assert status == UploadStatus.SUCCESS
assert warning == ""
print("[PASS] Normal Maple transfer = SUCCESS")

# 2. Transfer finished but USB reset failed.
status, message, warning = evaluate("""
Starting download: [##################################################] finished!
Done!
Resetting USB to switch back to runtime mode
error resetting after download: usb_reset: could not reset device
""", """
Reset via USB Serial Failed! Did you select the right serial port?
""")
assert status == UploadStatus.SUCCESS_WITH_WARNING
assert "USB runtime reset" in warning
print("[PASS] Transfer + reset failure = SUCCESS_WITH_WARNING")

# 3. Transfer reaches finished but final Done! is absent.
status, message, warning = evaluate("""
Starting download: [##################################################] finished!
Resetting USB to switch back to runtime mode
""")
assert status == UploadStatus.SUCCESS_WITH_WARNING
print("[PASS] Finished transfer without Done! is not FAILED")

# 4. Genuine DFU failure remains FAILED.
status, message, warning = evaluate(
    "Searching for DFU device [1EAF:003]...",
    "No DFU device found",
    return_code=1,
)
assert status == UploadStatus.FAILED
print("[PASS] DFU device failure remains FAILED")

# 5. Java failure remains FAILED.
status, message, warning = evaluate(
    "",
    'Exception in thread "main"\njava.lang.ArrayIndexOutOfBoundsException',
    return_code=0,
)
assert status == UploadStatus.FAILED
print("[PASS] Java exception remains FAILED")

print("=" * 70)
print("ALL STEP 5.4 MAPLE COMPLETION TESTS PASSED")
print("=" * 70)
print("No physical UB3 was programmed.")
