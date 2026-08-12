"""
STEP 6.8 - LOGS & DIAGNOSTICS UI
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from PySide6.QtWidgets import QApplication, QFileDialog

from ub3_updater.models.upload_result import UploadResult
from ub3_updater.widgets.dashboard_widget import DashboardWidget

app = QApplication.instance() or QApplication(sys.argv)
dashboard = DashboardWidget()
dashboard.show()
app.processEvents()

# ---------------------------------------------------------
# Diagnostics UI
# ---------------------------------------------------------
assert dashboard.diagnostics_card.objectName() == "uploadDiagnosticsCard"
assert dashboard.diagnostics_badge.objectName() == "uploadDiagnosticsBadge"
assert dashboard.output.objectName() == "uploadOutput"
assert dashboard.copy_log_button.objectName() == "copyLogButton"
assert dashboard.clear_log_button.objectName() == "clearLogButton"
assert dashboard.save_log_button.objectName() == "saveLogButton"
print("[PASS] Diagnostics card and technical log controls created")

# ---------------------------------------------------------
# Result metadata
# ---------------------------------------------------------
result = UploadResult.success_result(
    message="Firmware upload completed successfully.",
    firmware_name="ZNA2US",
    firmware_version="1.00",
    firmware_path="resources/firmware/ZNA2US/test.bin",
    com_port="COM7",
    device_state="Maple Serial",
    return_code=0,
    duration_seconds=18.42,
)

dashboard.show_result(result, can_update=True)
app.processEvents()

assert dashboard.diagnostics_badge.isVisible()
assert dashboard.diagnostics_badge.status() == "success"
assert dashboard.diagnostic_values["firmware"].text() == "ZNA2US"
assert dashboard.diagnostic_values["version"].text() == "1.00"
assert dashboard.diagnostic_values["com_port"].text() == "COM7"
assert dashboard.diagnostic_values["device_state"].text() == "Maple Serial"
assert dashboard.diagnostic_values["duration"].text() == "18.42 s"
assert dashboard.diagnostic_values["return_code"].text() == "0"
print("[PASS] Upload result metadata displayed in diagnostics")

# ---------------------------------------------------------
# Technical log preservation
# ---------------------------------------------------------
dashboard.append_output("Opening COM7...")
dashboard.append_output("Uploading firmware...")
dashboard.append_output("UB3 returned to Maple Serial mode.")
app.processEvents()

log_text = dashboard.output.toPlainText()
assert "Opening COM7..." in log_text
assert "Uploading firmware..." in log_text
assert "UB3 returned to Maple Serial mode." in log_text
print("[PASS] Technical upload output remains visible")

# ---------------------------------------------------------
# Copy
# ---------------------------------------------------------
dashboard.copy_log()
assert QApplication.clipboard().text() == log_text
print("[PASS] Technical log can be copied")

# ---------------------------------------------------------
# Save
# ---------------------------------------------------------
original_get_save = QFileDialog.getSaveFileName
save_target = Path(os.environ.get("TEMP", ".")) / "ub3_step_6_8_test.log"
QFileDialog.getSaveFileName = staticmethod(
    lambda *args, **kwargs: (str(save_target), "Log files (*.log)")
)
try:
    dashboard.save_log()
    assert save_target.exists()
    assert save_target.read_text(encoding="utf-8") == log_text
finally:
    QFileDialog.getSaveFileName = original_get_save
    if save_target.exists():
        save_target.unlink()
print("[PASS] Technical log can be saved")

# ---------------------------------------------------------
# Clear visible log only
# ---------------------------------------------------------
dashboard.clear_output()
assert dashboard.output.toPlainText() == ""
print("[PASS] Clear removes only the visible technical log")

# ---------------------------------------------------------
# Warning and failure diagnostic states
# ---------------------------------------------------------
dashboard.show_result(
    UploadResult.success_with_warning_result(
        message="Firmware programmed successfully.",
        warning="UB3 requires attention after reconnect.",
        firmware_name="ZMJ",
        firmware_version="1.00",
        com_port="COM8",
    ),
    can_update=True,
)
assert dashboard.diagnostics_badge.status() == "warning"


dashboard.show_result(
    UploadResult.failed_result(
        message="Maple Loader failed to confirm the firmware update.",
        firmware_name="ZMZ5",
        firmware_version="1.00",
        com_port="COM9",
        return_code=1,
    ),
    can_update=True,
)
assert dashboard.diagnostics_badge.status() == "error"
assert dashboard.diagnostic_values["return_code"].text() == "1"
print("[PASS] Warning and failure states map to diagnostics correctly")

dashboard.close()

print("")
print("# STEP 6.8 - LOGS & DIAGNOSTICS UI")
print("# ALL STEP 6.8 LOGS & DIAGNOSTICS TESTS PASSED")
print("No physical UB3 was programmed.")
