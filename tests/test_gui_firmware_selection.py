"""
======================================================================
UB3 FIRMWARE UPDATER
GUI STEP 3 - FIRMWARE SELECTION TEST
======================================================================

Tests firmware selection using the current project architecture.

No physical UB3 is programmed.
No real USB monitoring is started.
"""

from __future__ import annotations

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import bootstrap

from PySide6.QtWidgets import QApplication

from ub3_updater.models.device import (
    Device,
    DeviceState,
)

from ub3_updater.controllers.update_controller import (
    UpdateControllerState,
)

from ub3_updater.services.firmware_service import (
    FirmwareService,
)

from ub3_updater.ui.main_window import (
    MainWindow,
)


# =====================================================================
# APPLICATION
# =====================================================================

print()
print("=" * 70)
print("GUI STEP 3 - FIRMWARE SELECTION TEST")
print("=" * 70)

app = QApplication.instance()

if app is None:
    app = QApplication(sys.argv)

from ub3_updater.themes.light_theme import STYLE

app.setStyleSheet(STYLE)


# =====================================================================
# CONTROLLER STUB
# =====================================================================

class ControllerStub:
    """
    Controller-compatible test double.

    This class intentionally does not start real USB monitoring.
    """

    def __init__(self):

        # -------------------------------------------------------------
        # Firmware service
        # -------------------------------------------------------------

        self.firmware_service = FirmwareService()

        # -------------------------------------------------------------
        # Runtime state
        # -------------------------------------------------------------

        self.selected_firmware = None
        self.device = None

        self._state = (
            UpdateControllerState.WAITING_FOR_DEVICE
        )

        self.started = False
        self.stopped = False

        # -------------------------------------------------------------
        # Callbacks
        # -------------------------------------------------------------

        self._on_device_changed = None
        self._on_state_changed = None
        self._on_status = None
        self._on_output = None
        self._on_result = None
        self._on_error = None

    # =================================================================
    # STATE
    # =================================================================

    @property
    def state(self):
        return self._state

    # =================================================================
    # UPLOAD STATE
    # =================================================================

    @property
    def is_uploading(self):
        return (
            self._state
            == UpdateControllerState.UPLOADING
        )

    # =================================================================
    # UPDATE AVAILABILITY
    # =================================================================

    @property
    def can_update(self):
        return (
            self.selected_firmware is not None
            and self.device is not None
            and self.device.connected
            and self.device.state
            == DeviceState.MAPLE_SERIAL
        )

    # =================================================================
    # LIFECYCLE
    # =================================================================

    def start(self):
        self.started = True
        return True

    def stop(self):
        self.stopped = True
        return True

    # =================================================================
    # DEVICE
    # =================================================================

    def refresh_device(self):
        return None

    # =================================================================
    # FIRMWARE
    # =================================================================

    def get_available_firmware(self):
        return self.firmware_service.get_all()

    def select_firmware(self, firmware):
        self.selected_firmware = firmware
        return firmware

    # =================================================================
    # UPDATE ACTIONS
    # =================================================================

    def update(self):
        return False

    def cancel(self):
        return False

    # =================================================================
    # CALLBACKS
    # =================================================================

    def set_on_device_changed(self, callback):
        self._on_device_changed = callback

    def set_on_state_changed(self, callback):
        self._on_state_changed = callback

    def set_on_status(self, callback):
        self._on_status = callback

    def set_on_output(self, callback):
        self._on_output = callback

    def set_on_result(self, callback):
        self._on_result = callback

    def set_on_error(self, callback):
        self._on_error = callback


# =====================================================================
# CREATE WINDOW
# =====================================================================

controller = ControllerStub()

window = MainWindow(
    controller=controller
)

home = window.home_page

dashboard = (
    home.dashboard_widget
)


# =====================================================================
# TEST 1 - MAIN WINDOW
# =====================================================================

print()
print("TEST 1 - MAIN WINDOW / CONTROLLER CONTRACT")
print("=" * 70)

assert window is not None
assert home is not None
assert dashboard is not None
assert controller.started is True

print("[PASS] MainWindow created")
print("[PASS] Controller.start() called")
print("[PASS] Dashboard widget created")


# =====================================================================
# TEST 2 - FIRMWARE PACKAGE LIST
# =====================================================================

print()
print("TEST 2 - FIRMWARE PACKAGE LIST")
print("=" * 70)

firmwares = (
    controller
    .get_available_firmware()
)

assert firmwares, (
    "Firmware repository returned no packages."
)

# The GUI must receive real Firmware objects.
assert all(
    hasattr(
        firmware,
        "is_valid_file",
    )
    for firmware in firmwares
)

print(
    f"[PASS] Firmware packages loaded: "
    f"{len(firmwares)}"
)

print(
    "[PASS] Real Firmware model objects detected"
)


# =====================================================================
# TEST 3 - ZNA2US AVAILABLE
# =====================================================================

print()
print("TEST 3 - ZNA2US FIRMWARE")
print("=" * 70)

zna2us = next(
    (
        firmware
        for firmware in firmwares
        if firmware.name == "ZNA2US"
    ),
    None,
)

assert zna2us is not None, (
    "ZNA2US firmware was not found "
    "in the firmware repository."
)

assert zna2us.version == "1.00"

print("[PASS] ZNA2US available")
print("[PASS] ZNA2US version is 1.00")


# =====================================================================
# TEST 4 - FIRMWARE DROPDOWN
# =====================================================================

print()
print("TEST 4 - FIRMWARE DROPDOWN")
print("=" * 70)

combo = dashboard.firmware_combo

assert combo is not None

assert combo.count() > 0

# -------------------------------------------------------------
# Collect every visible combo item.
# -------------------------------------------------------------

items = [
    combo.itemText(index)
    for index in range(combo.count())
]

print()
print("Firmware dropdown items:")

for index, text in enumerate(items):
    print(
        f"  [{index}] {text}"
    )

# -------------------------------------------------------------
# Do NOT assume ZNA2US is item 0.
# -------------------------------------------------------------

zna_items = [
    text
    for text in items
    if "ZNA2US" in text
]

assert zna_items, (
    "ZNA2US is not displayed in the "
    "firmware dropdown."
)

assert any(
    "Version" in text
    for text in zna_items
), (
    "ZNA2US is displayed but its version "
    "is not shown in the dropdown."
)

assert any(
    "1.00" in text
    for text in zna_items
), (
    "ZNA2US Version 1.00 is not shown "
    "in the dropdown."
)

print(
    "[PASS] ZNA2US appears in firmware dropdown"
)

print(
    "[PASS] Firmware dropdown includes version"
)

print(
    "[PASS] ZNA2US Version 1.00 displayed"
)


# =====================================================================
# TEST 5 - SELECT ZNA2US
# =====================================================================

print()
print("TEST 5 - SELECT ZNA2US")
print("=" * 70)

# Find the actual ZNA2US item instead of assuming index 0.

zna_index = next(
    (
        index
        for index in range(combo.count())
        if "ZNA2US" in combo.itemText(index)
        and "1.00" in combo.itemText(index)
    ),
    -1,
)

assert zna_index >= 0

combo.setCurrentIndex(
    zna_index
)

# Give Qt a chance to process the signal.
app.processEvents()

selected = dashboard.selected_firmware()

assert selected is not None

assert selected.name == "ZNA2US"

assert selected.version == "1.00"

print(
    "[PASS] ZNA2US selected"
)

print(
    "[PASS] Version 1.00 selected"
)


# =====================================================================
# TEST 6 - FIRMWARE INFORMATION
# =====================================================================

print()
print("TEST 6 - FIRMWARE INFORMATION")
print("=" * 70)

info = dashboard.firmware_info.text()

assert "ZNA2US" in info

assert "Version:" in info

assert "Target Device:" in info

assert "File:" in info

assert "Size:" in info

assert "Status:" in info

print(
    "[PASS] Firmware name displayed"
)

print(
    "[PASS] Firmware version displayed"
)

print(
    "[PASS] Target device displayed"
)

print(
    "[PASS] Firmware filename displayed"
)

print(
    "[PASS] Firmware size displayed"
)

print(
    "[PASS] Firmware validation status displayed"
)


# =====================================================================
# TEST 7 - DEVICE + FIRMWARE READY
# =====================================================================

print()
print("TEST 7 - DEVICE + FIRMWARE READY")
print("=" * 70)

device = Device(
    connected=True,
    state=DeviceState.MAPLE_SERIAL,
    com_port="COM3",
    usb_name="Maple Serial (COM3)",
    description="Maple Serial (COM3)",
    manufacturer="LeafLabs, LLC",
    vid="1EAF",
    pid="0004",
)

controller.device = device

controller.selected_firmware = (
    zna2us
)

# Update the GUI device information.

home.update_device(
    device
)

# Update controller state.

controller._state = (
    UpdateControllerState.READY
)

# Refresh dashboard readiness.

home._refresh_button_state()

assert controller.can_update is True

assert dashboard.update_button.isEnabled()

print(
    "[PASS] Maple Serial device accepted"
)

print(
    "[PASS] Firmware selected"
)

print(
    "[PASS] Update button enabled"
)


# =====================================================================
# TEST 8 - BUTTON IDENTITY
# =====================================================================

print()
print("TEST 8 - BUTTON IDENTITY")
print("=" * 70)

assert (
    dashboard.update_button.objectName()
    == "updateButton"
)

assert (
    dashboard.cancel_button.objectName()
    == "cancelButton"
)

print(
    "[PASS] Update button object name correct"
)

print(
    "[PASS] Cancel button object name correct"
)


# =====================================================================
# TEST 9 - DISCONNECT
# =====================================================================

print()
print("TEST 9 - DEVICE DISCONNECT")
print("=" * 70)

controller.device = None

controller._state = (
    UpdateControllerState.WAITING_FOR_DEVICE
)

home.update_device(
    None
)

home._refresh_button_state()

assert (
    not dashboard.update_button.isEnabled()
)

print(
    "[PASS] Device removal handled"
)

print(
    "[PASS] Update disabled after disconnect"
)


# =====================================================================
# CLEANUP
# =====================================================================

window.close()

print()
print("=" * 70)
print(
    "ALL GUI STEP 3 FIRMWARE SELECTION "
    "TESTS PASSED"
)
print("=" * 70)

print()
print(
    "No physical UB3 was programmed."
)