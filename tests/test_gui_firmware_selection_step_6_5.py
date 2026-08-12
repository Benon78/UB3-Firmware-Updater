"""
======================================================================
STEP 6.5 - FIRMWARE SELECTION UI
======================================================================

Presentation-focused validation of the firmware-selection experience.

The test verifies:
- real Firmware model objects remain the source of selection
- every repository firmware is displayed
- name and version are visible
- firmware details are presented
- validation state is visible
- changing selection changes the selected Firmware object
- no firmware path is rewritten or staged by the GUI
- existing Dashboard object contracts remain intact

No physical UB3 is programmed.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import bootstrap

from PySide6.QtWidgets import QApplication

from ub3_updater.models.firmware import Firmware
from ub3_updater.services.firmware_service import FirmwareService
from ub3_updater.widgets.dashboard_widget import DashboardWidget
from ub3_updater.widgets.components import (
    UB3ComboBox,
    UB3StatusBadge,
    UB3SectionHeader,
)

print()
print("=" * 70)
print("STEP 6.5 - FIRMWARE SELECTION UI")
print("=" * 70)

app = QApplication.instance() or QApplication(sys.argv)

service = FirmwareService()
firmwares = service.get_all()

assert firmwares, "Firmware repository returned no packages."

dashboard = DashboardWidget()
dashboard.set_firmwares(firmwares)

print()
print("TEST 1 - SELECTION COMPONENTS")
print("=" * 70)

assert isinstance(dashboard.firmware_combo, UB3ComboBox)
assert dashboard.firmware_combo.objectName() == "firmwareCombo"
print("[PASS] Firmware selector uses UB3ComboBox")

assert dashboard.firmware_combo.isEnabled()
print("[PASS] Firmware selector enabled")

assert dashboard.firmware_details_card.objectName() == "firmwareDetailsCard"
print("[PASS] Firmware details card created")

assert isinstance(
    dashboard.firmware_validation_badge,
    UB3StatusBadge,
)
assert dashboard.firmware_validation_badge.objectName() == "firmwareValidationBadge"
print("[PASS] Firmware validation badge created")

print()
print("TEST 2 - FIRMWARE REPOSITORY PRESENTATION")
print("=" * 70)

assert dashboard.firmware_combo.count() == len(firmwares)
print(f"[PASS] All {len(firmwares)} firmware packages displayed")

for index, firmware in enumerate(firmwares):
    text = dashboard.firmware_combo.itemText(index)
    assert firmware.name in text
    assert firmware.version in text
    assert dashboard.firmware_combo.itemData(index) is firmware
    print(f"[PASS] {firmware.name} v{firmware.version} displayed")

print()
print("TEST 3 - SELECT EACH FIRMWARE")
print("=" * 70)

for index, expected in enumerate(firmwares):
    dashboard.firmware_combo.setCurrentIndex(index)
    app.processEvents()

    selected = dashboard.selected_firmware()

    assert selected is expected
    assert selected.name == expected.name
    assert selected.version == expected.version

    info = dashboard.firmware_info.text()
    assert expected.name in info
    assert "Version:" in info
    assert "Target Device:" in info
    assert "File:" in info
    assert "Size:" in info
    assert "Status:" in info

    assert dashboard.firmware_validation_badge.status() == (
        "success" if expected.is_valid_file() else "warning"
    )

    print(
        f"[PASS] {expected.name} v{expected.version} selected and details displayed"
    )

print()
print("TEST 4 - SELECTION ISOLATION")
print("=" * 70)

if len(firmwares) >= 2:
    dashboard.firmware_combo.setCurrentIndex(0)
    app.processEvents()
    first = dashboard.selected_firmware()

    dashboard.firmware_combo.setCurrentIndex(1)
    app.processEvents()
    second = dashboard.selected_firmware()

    assert first is firmwares[0]
    assert second is firmwares[1]
    assert first.path != second.path
    print("[PASS] Changing firmware changes selected Firmware model")
    print("[PASS] Firmware paths remain isolated")

print()
print("TEST 5 - PATH INTEGRITY")
print("=" * 70)

firmware_root = service.firmware_root.resolve()

for firmware in firmwares:
    path = Path(firmware.path).resolve()

    assert path.is_file()
    assert firmware_root in path.parents
    assert "tmp" not in str(path).lower() or "resources\\firmware" in str(path).lower()
    print(f"[PASS] {firmware.name} uses repository firmware path")

print()
print("TEST 6 - EXISTING CONTRACTS")
print("=" * 70)

assert dashboard.update_button.objectName() == "updateButton"
assert dashboard.cancel_button.objectName() == "cancelButton"
assert dashboard.firmware_combo.objectName() == "firmwareCombo"
print("[PASS] Existing Dashboard object-name contracts preserved")

dashboard.close()

print()
print("=" * 70)
print("ALL STEP 6.5 FIRMWARE SELECTION UI TESTS PASSED")
print("=" * 70)
print()
print("No physical UB3 was programmed.")
