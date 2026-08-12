"""
UB3 Firmware Updater - Step 6.6 Upload / Progress UI Test

Presentation-only validation of the operator upload workflow.
No physical UB3 is programmed and no UploadService is executed.
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

print()
print("=" * 70)
print("STEP 6.6 - UPLOAD / PROGRESS UI")
print("=" * 70)

dashboard = DashboardWidget()
dashboard.show()
app.processEvents()

assert hasattr(dashboard, "progress_steps")
print("[PASS] Upload workflow phase indicators created")

assert set(dashboard.progress_steps) == {
    "Prepare", "Start", "Upload", "Reconnect", "Complete"
}
print("[PASS] Complete upload phase sequence defined")

dashboard.set_controller_state(
    "Uploading Firmware",
    "Preparing firmware update...",
    False,
)

assert dashboard.circular_progress.value() == 10
assert dashboard.progress_phase_label.text() == "Preparing"
print("[PASS] Preparing phase displayed")

dashboard.update_progress("Starting firmware upload...")
assert dashboard.circular_progress.value() == 25
assert dashboard.progress_phase_label.text() == "Starting"
print("[PASS] Maple start phase displayed")

dashboard.update_progress("Downloading firmware...")
assert dashboard.circular_progress.value() == 60
assert dashboard.progress_phase_label.text() == "Uploading"
print("[PASS] Uploading phase displayed")

dashboard.update_progress(
    "Firmware transfer completed. Resetting USB to switch back to runtime mode"
)
assert dashboard.circular_progress.value() == 92
assert dashboard.progress_phase_label.text() == "Reconnecting"
print("[PASS] Post-upload USB/re-enumeration phase displayed")

dashboard.update_progress(
    "UB3 returned to Maple Serial mode on COM3."
)
assert dashboard.circular_progress.value() == 92
assert dashboard.progress_phase_label.text() == "Reconnecting"
print("[PASS] Maple Serial recovery phase retained")

result = UploadResult.success_result(
    message="Firmware upload completed successfully.",
    firmware_name="ZNA2US",
    firmware_version="1.00",
    com_port="COM3",
)

dashboard.show_result(result, False)

assert dashboard.circular_progress.value() == 100
assert dashboard.progress_phase_label.text() == "Complete"
assert dashboard.progress_card.isVisible()
print("[PASS] Successful completion reaches 100%")

assert dashboard.cancel_button.isEnabled() is False
assert dashboard.update_button.isEnabled() is False
print("[PASS] Controls locked correctly after completion")

dashboard.clear_output()
dashboard.append_output("Maple Loader started.")
dashboard.append_output("Downloading firmware...")
dashboard.append_output("Resetting USB to switch back to runtime mode")
dashboard.append_output("UB3 returned to Maple Serial mode on COM3.")

log = dashboard.output.toPlainText()
assert "Maple Loader started." in log
assert "Downloading firmware..." in log
assert "Resetting USB" in log
assert "Maple Serial mode" in log
print("[PASS] Live Maple workflow output remains visible")

assert "bytes" in dashboard.progress_hint.text().lower()
print("[PASS] Progress remains explicitly phase-based, not byte-based")

failed = UploadResult.failed_result(
    message="Maple Loader did not report a confirmed successful firmware update.",
    firmware_name="ZNA2US",
    firmware_version="1.00",
    com_port="COM3",
)
dashboard.show_result(failed, False)

assert dashboard.progress_phase_label.text() == "Failed"
assert dashboard.progress_card.isVisible()
print("[PASS] Failure state preserves diagnostic progress context")

print()
print("=" * 70)
print("ALL STEP 6.6 UPLOAD / PROGRESS UI TESTS PASSED")
print("=" * 70)
print()
print("No physical UB3 was programmed.")
