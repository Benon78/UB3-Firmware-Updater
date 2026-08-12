"""
STEP 6.7 - SUCCESS / WARNING / FAILURE UX
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import bootstrap  # noqa: F401

from PySide6.QtWidgets import QApplication

from ub3_updater.models.upload_result import UploadResult
from ub3_updater.widgets.dashboard_widget import DashboardWidget


app = QApplication.instance() or QApplication(sys.argv)

dashboard = DashboardWidget()
dashboard.show()
app.processEvents()


# ---------------------------------------------------------
# SUCCESS
# ---------------------------------------------------------

dashboard.show_result(
    UploadResult.success_result(
        message="Firmware upload completed successfully.",
        firmware_name="ZNA2US",
        firmware_version="1.00",
        com_port="COM3",
    ),
    can_update=True,
)
app.processEvents()

assert dashboard.result_banner.isVisible()
assert dashboard.result_banner.status() == "success"
assert "successfully" in dashboard.result_banner.message().lower()
assert dashboard.update_button.isEnabled()
assert not dashboard.cancel_button.isEnabled()

print("[PASS] Success result banner displayed")
print("[PASS] Success result uses semantic success state")
print("[PASS] Success result preserves update availability")


# ---------------------------------------------------------
# SUCCESS WITH WARNING
# ---------------------------------------------------------

dashboard.show_result(
    UploadResult.success_with_warning_result(
        message="Firmware was programmed successfully.",
        warning="UB3 requires reconnection.",
        firmware_name="ZMJ",
        firmware_version="1.00",
        com_port="COM3",
    ),
    can_update=True,
)
app.processEvents()

assert dashboard.result_banner.isVisible()
assert dashboard.result_banner.status() == "warning"
assert "warning" in dashboard.result_banner.message().lower()
assert dashboard.update_button.isEnabled()

print("[PASS] Success-with-warning banner displayed")
print("[PASS] Warning result uses semantic warning state")


# ---------------------------------------------------------
# FAILURE
# ---------------------------------------------------------

dashboard.show_result(
    UploadResult.failed_result(
        message="Maple Loader failed to confirm the firmware update.",
        firmware_name="ZMZ5",
        firmware_version="1.00",
        com_port="COM3",
    ),
    can_update=True,
)
app.processEvents()

assert dashboard.result_banner.isVisible()
assert dashboard.result_banner.status() == "error"
assert "failed" in dashboard.result_banner.message().lower()
assert dashboard.update_button.isEnabled()
assert not dashboard.cancel_button.isEnabled()

print("[PASS] Failure result banner displayed")
print("[PASS] Failure result uses semantic error state")
print("[PASS] Failure result keeps retry/update available")


# ---------------------------------------------------------
# CANCELLED
# ---------------------------------------------------------

dashboard.show_result(
    UploadResult.cancelled_result(),
    can_update=True,
)
app.processEvents()

assert dashboard.result_banner.isVisible()
assert dashboard.result_banner.status() == "info"
assert "cancelled" in dashboard.result_banner.message().lower()

print("[PASS] Cancelled result banner displayed")
print("[PASS] Cancelled result uses informational state")


# ---------------------------------------------------------
# NEW UPLOAD CLEARS TERMINAL RESULT
# ---------------------------------------------------------

dashboard.set_controller_state(
    "Uploading Firmware",
    "Preparing firmware update...",
    False,
)
app.processEvents()

assert not dashboard.result_banner.isVisible()
assert not dashboard.update_button.isEnabled()
assert dashboard.cancel_button.isEnabled()

print("[PASS] New upload clears previous terminal result")
print("[PASS] New upload locks Update and enables Cancel")


dashboard.close()

print("")
print("# STEP 6.7 - SUCCESS / WARNING / FAILURE UX")
print("# ALL STEP 6.7 RESULT UX TESTS PASSED")
print("No physical UB3 was programmed.")
