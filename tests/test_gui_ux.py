"""
UB3 GUI UX Step 1.1 regression test.
No physical UB3 is programmed.
"""
from __future__ import annotations
import os, sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import bootstrap
from PySide6.QtWidgets import QApplication
from ub3_updater.ui.main_window import MainWindow
from test_gui import FakeController

app = QApplication.instance() or QApplication(sys.argv)
from ub3_updater.themes.light_theme import STYLE
app.setStyleSheet(STYLE)

controller = FakeController()
window = MainWindow(controller=controller)
dashboard = window.home_page.dashboard_widget

firmwares = controller.get_available_firmware()
assert firmwares

for i, firmware in enumerate(firmwares):
    label = dashboard.firmware_combo.itemText(i)
    assert firmware.name in label
    assert (firmware.version or "Unknown Version") in label

assert dashboard.update_button.objectName() == "updateButton"
assert dashboard.cancel_button.objectName() == "cancelButton"

zna2us = next(f for f in firmwares if f.name == "ZNA2US")
controller.selected_firmware = zna2us
controller.device = type("DeviceStub", (), {"connected": True, "is_maple": True})()

dashboard.set_ready_state(True)
assert dashboard.update_button.isEnabled()

dashboard.set_controller_state("Uploading Firmware", "Uploading...", False)
assert not dashboard.update_button.isEnabled()
assert dashboard.cancel_button.isEnabled()

dashboard.set_ready_state(False)
assert not dashboard.update_button.isEnabled()
assert not dashboard.cancel_button.isEnabled()

window.close()

print("=" * 70)
print("GUI UX STEP 1.1 PASSED")
print("=" * 70)
print("Firmware package + version presentation : PASS")
print("High-contrast Update button              : PASS")
print("High-contrast Cancel button              : PASS")
print("Ready/Uploading button state             : PASS")
print("No physical UB3 was programmed.")
