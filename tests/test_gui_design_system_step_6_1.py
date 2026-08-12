"""Step 6.1 GUI Design System regression test.

Presentation-only test. No physical UB3 is programmed and no upload
service is executed.
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import bootstrap

from PySide6.QtWidgets import QApplication

from ub3_updater.services.config_service import ConfigService
from ub3_updater.themes.design_system import (
    PRIMARY,
    PRIMARY_DARK,
    SUCCESS,
    WARNING,
    ERROR,
    NEUTRAL,
    COMBO_BOX_STYLE,
    PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE,
)
from ub3_updater.ui.main_window import MainWindow
from ub3_updater.widgets.action_button_style import (
    UPDATE_BUTTON_STYLE,
    CANCEL_BUTTON_STYLE,
    REFRESH_BUTTON_STYLE,
)
from ub3_updater.widgets.footer_widget import FooterWidget
from test_gui import FakeController

app = QApplication.instance() or QApplication(sys.argv)

from ub3_updater.themes.light_theme import STYLE
app.setStyleSheet(STYLE)

print("=" * 70)
print("GUI DESIGN SYSTEM TEST - STEP 6.1")
print("=" * 70)

# ---------------------------------------------------------
# Design tokens
# ---------------------------------------------------------
assert PRIMARY == "#2563EB"
assert PRIMARY_DARK == "#1E3A8A"
assert SUCCESS == "#10B981"
assert WARNING == "#F59E0B"
assert ERROR == "#EF4444"
assert NEUTRAL == "#6B7280"
print("[PASS] Approved UB3 semantic color tokens")

for name, style in (
    ("Primary button", PRIMARY_BUTTON_STYLE),
    ("Secondary button", SECONDARY_BUTTON_STYLE),
    ("Update button", UPDATE_BUTTON_STYLE),
    ("Cancel button", CANCEL_BUTTON_STYLE),
    ("Refresh button", REFRESH_BUTTON_STYLE),
    ("Firmware dropdown", COMBO_BOX_STYLE),
):
    assert "background" in style.lower()
    assert "border" in style.lower()
    assert "color" in style.lower()
    print(f"[PASS] {name} has explicit surface/text/border styling")

# ---------------------------------------------------------
# Actual GUI controls
# ---------------------------------------------------------
controller = FakeController()
window = MainWindow(controller=controller)
dashboard = window.home_page.dashboard_widget

assert dashboard.firmware_combo.styleSheet()
assert "background" in dashboard.firmware_combo.styleSheet().lower()
print("[PASS] Firmware dropdown receives direct UB3 styling")

assert dashboard.update_button.styleSheet()
assert "background" in dashboard.update_button.styleSheet().lower()
print("[PASS] Update button receives direct UB3 styling")

assert dashboard.cancel_button.styleSheet()
assert "background" in dashboard.cancel_button.styleSheet().lower()
print("[PASS] Cancel button receives direct UB3 styling")

assert window.version_label.text() == f"v{ConfigService.application_version()}"
print("[PASS] MainWindow version comes from app configuration")

footer = FooterWidget()
assert footer.version_label.text() == f"v{ConfigService.application_version()}"
print("[PASS] FooterWidget version comes from app configuration")

# Existing behavior contracts remain.
assert dashboard.update_button.objectName() == "updateButton"
assert dashboard.cancel_button.objectName() == "cancelButton"
assert dashboard.firmware_combo.objectName() == "firmwareCombo"
print("[PASS] Existing GUI object-name contracts preserved")

window.close()
footer.deleteLater()

print("=" * 70)
print("ALL STEP 6.1 GUI DESIGN SYSTEM TESTS PASSED")
print("=" * 70)
print("No physical UB3 was programmed.")
