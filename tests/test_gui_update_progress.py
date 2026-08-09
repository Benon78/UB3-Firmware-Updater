"""
UB3 Firmware Updater - Step 4.5 GUI Progress Test

Validates the operator-facing update progress UI.

No physical UB3 is used.
No UploadService is executed.
"""

from __future__ import annotations

import os
import sys

os.environ.setdefault(
    "QT_QPA_PLATFORM",
    "offscreen",
)

import bootstrap  # noqa: F401

from PySide6.QtWidgets import QApplication

from ub3_updater.models.upload_result import (
    UploadResult,
    UploadStatus,
)
from ub3_updater.widgets.dashboard_widget import (
    DashboardWidget,
    CircularProgressWidget,
)


# =========================================================
# Qt application
# =========================================================

app = QApplication.instance()

if app is None:
    app = QApplication(sys.argv)


print()
print("=" * 70)
print("GUI STEP 4.5 - UPDATE PROGRESS TEST")
print("=" * 70)


# =========================================================
# TEST 1 - DASHBOARD CREATION
# =========================================================

print()
print("=" * 70)
print("TEST 1 - DASHBOARD PROGRESS COMPONENTS")
print("=" * 70)

dashboard = DashboardWidget()

assert dashboard is not None
print("[PASS] Dashboard widget created")

assert dashboard.progress_bar is not None
print("[PASS] Linear progress bar created")

assert dashboard.circular_progress is not None
assert isinstance(
    dashboard.circular_progress,
    CircularProgressWidget,
)
print("[PASS] Circular progress indicator created")

assert dashboard.progress_card is not None
print("[PASS] Progress card created")


# =========================================================
# TEST 2 - INITIAL STATE
# =========================================================

print()
print("=" * 70)
print("TEST 2 - INITIAL PROGRESS STATE")
print("=" * 70)

assert dashboard.circular_progress.value() == 0
print("[PASS] Initial circular progress is 0%")

assert dashboard.progress_bar.value() == 0
print("[PASS] Initial linear progress is 0%")

assert dashboard.progress_card.isHidden() is True
print("[PASS] Progress card hidden while idle")


# =========================================================
# TEST 3 - STARTING PHASE
# =========================================================

print()
print("=" * 70)
print("TEST 3 - STARTING PHASE")
print("=" * 70)

dashboard.set_controller_state(
    "Uploading Firmware",
    "Preparing firmware update...",
    False,
)

assert dashboard.progress_card.isHidden() is False
print("[PASS] Progress card shown during update")

assert dashboard.circular_progress.value() == 10
print("[PASS] Preparing phase = 10%")

assert dashboard.progress_bar.value() == 10
print("[PASS] Linear progress = 10%")

assert (
    dashboard.progress_phase_label.text()
    == "Preparing"
)
print("[PASS] Preparing phase displayed")


# =========================================================
# TEST 4 - STARTING MAPLE LOADER
# =========================================================

print()
print("=" * 70)
print("TEST 4 - MAPLE LOADER START")
print("=" * 70)

dashboard.update_progress(
    "Starting firmware upload..."
)

assert dashboard.circular_progress.value() == 25
print("[PASS] Starting phase = 25%")

assert dashboard.progress_bar.value() == 25
print("[PASS] Linear progress = 25%")

assert (
    dashboard.progress_phase_label.text()
    == "Starting"
)
print("[PASS] Starting phase displayed")


dashboard.update_progress(
    "Maple Loader started."
)

assert dashboard.circular_progress.value() == 25
print("[PASS] Maple Loader start retained at 25%")


# =========================================================
# TEST 5 - UPLOADING PHASE
# =========================================================

print()
print("=" * 70)
print("TEST 5 - UPLOADING PHASE")
print("=" * 70)

dashboard.update_progress(
    "Opening COM3..."
)

assert dashboard.circular_progress.value() == 60
print("[PASS] Opening COM phase = 60%")

dashboard.update_progress(
    "Downloading firmware..."
)

assert dashboard.circular_progress.value() == 60
print("[PASS] Downloading phase = 60%")

assert (
    dashboard.progress_phase_label.text()
    == "Uploading"
)
print("[PASS] Uploading phase displayed")


# =========================================================
# TEST 6 - TRANSFER COMPLETION
# =========================================================

print()
print("=" * 70)
print("TEST 6 - TRANSFER COMPLETION")
print("=" * 70)

dashboard.update_progress(
    "Firmware transfer completed."
)

assert dashboard.circular_progress.value() == 85
print("[PASS] Transfer completion phase = 85%")

assert dashboard.progress_bar.value() == 85
print("[PASS] Linear progress = 85%")

assert (
    dashboard.progress_phase_label.text()
    == "Finalizing"
)
print("[PASS] Finalizing phase displayed")


# =========================================================
# TEST 7 - SUCCESS RESULT
# =========================================================

print()
print("=" * 70)
print("TEST 7 - SUCCESS RESULT")
print("=" * 70)

success_result = UploadResult.success_result(
    message=(
        "Firmware was programmed successfully."
    ),
    firmware_name="ZNA2US",
    firmware_version="1.00",
    com_port="COM3",
)

dashboard.show_result(
    success_result,
    False,
)

assert dashboard.circular_progress.value() == 100
print("[PASS] Successful update reaches 100%")

assert dashboard.progress_bar.value() == 100
print("[PASS] Linear progress reaches 100%")

assert dashboard.progress_card.isHidden() is False
print("[PASS] Progress summary remains visible")

assert (
    dashboard.status_label.text()
    == "Firmware Updated Successfully"
)
print("[PASS] Success status displayed")

assert (
    dashboard.cancel_button.isEnabled()
    is False
)
print("[PASS] Cancel disabled after success")


# =========================================================
# TEST 8 - SUCCESS WITH WARNING
# =========================================================

print()
print("=" * 70)
print("TEST 8 - SUCCESS WITH WARNING")
print("=" * 70)

warning_result = (
    UploadResult.success_with_warning_result(
        message=(
            "Firmware was programmed successfully."
        ),
        warning=(
            "USB reset warning reported after download."
        ),
        firmware_name="ZNA2US",
        firmware_version="1.00",
        com_port="COM3",
    )
)

dashboard.show_result(
    warning_result,
    False,
)

assert dashboard.circular_progress.value() == 100
print("[PASS] Warning result reaches 100%")

assert (
    dashboard.status_label.text()
    == "Success With Warning"
)
print("[PASS] Success-with-warning status displayed")


# =========================================================
# TEST 9 - FAILED RESULT
# =========================================================

print()
print("=" * 70)
print("TEST 9 - FAILED RESULT")
print("=" * 70)

failed_result = UploadResult.failed_result(
    message="Firmware programming failed.",
    firmware_name="ZNA2US",
    firmware_version="1.00",
    com_port="COM3",
)

dashboard.show_result(
    failed_result,
    False,
)

assert (
    dashboard.status_label.text()
    == "Update Failed"
)
print("[PASS] Failure status displayed")

assert (
    dashboard.progress_card.isHidden() is False
    is False
)
print("[PASS] Progress summary remains visible after failure")


# =========================================================
# TEST 10 - OUTPUT AUTO-SCROLL
# =========================================================

print()
print("=" * 70)
print("TEST 10 - LIVE LOG")
print("=" * 70)

dashboard.clear_output()

dashboard.append_output(
    "Maple Loader started."
)

dashboard.append_output(
    "Opening COM3..."
)

dashboard.append_output(
    "Downloading firmware..."
)

text = dashboard.output.toPlainText()

assert "Maple Loader started." in text
assert "Opening COM3..." in text
assert "Downloading firmware..." in text

print("[PASS] Live output displayed")

scrollbar = dashboard.output.verticalScrollBar()

assert (
    scrollbar.value()
    == scrollbar.maximum()
)

print("[PASS] Log automatically scrolls to latest output")


# =========================================================
# TEST 11 - NO FABRICATED BYTE PROGRESS
# =========================================================

print()
print("=" * 70)
print("TEST 11 - PROGRESS INTEGRITY")
print("=" * 70)

assert (
    "bytes" in dashboard.progress_hint.text().lower()
)

print(
    "[PASS] Progress explicitly identified as workflow phase"
)

assert (
    dashboard.progress_bar.minimum()
    == 0
)

assert (
    dashboard.progress_bar.maximum()
    == 100
)

print(
    "[PASS] Progress bar uses controlled 0-100 workflow scale"
)


# =========================================================
# FINAL
# =========================================================

print()
print("=" * 70)
print("FINAL VALIDATION")
print("=" * 70)

print("[PASS] Dashboard progress components")
print("[PASS] Initial state")
print("[PASS] Preparing phase")
print("[PASS] Maple Loader start phase")
print("[PASS] Uploading phase")
print("[PASS] Transfer completion phase")
print("[PASS] Successful completion")
print("[PASS] Success with warning")
print("[PASS] Failure handling")
print("[PASS] Live output")
print("[PASS] Progress integrity")

print()
print("=" * 70)
print("ALL GUI STEP 4.5 PROGRESS TESTS PASSED")
print("=" * 70)

print()
print("No physical UB3 was programmed.")
