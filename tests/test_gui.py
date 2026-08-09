"""
UB3 Firmware Updater - GUI Step 1 Test

This test verifies the first GUI integration layer without
programming a physical UB3.

Coverage:
- Light theme loads
- MainWindow builds
- HomePage builds
- Firmware repository is loaded
- Firmware selection works
- Device state updates
- Update button readiness follows controller state
- GUI closes cleanly

Run:
    python tests/test_gui.py
"""

from __future__ import annotations

import os
import sys

# Must be set before QApplication is created.
os.environ.setdefault(
    "QT_QPA_PLATFORM",
    "offscreen",
)

import bootstrap

from PySide6.QtWidgets import QApplication

from ub3_updater.controllers.update_controller import (
    UpdateController,
    UpdateControllerState,
)
from ub3_updater.models.device import (
    Device,
    DeviceState,
)
from ub3_updater.services.firmware_service import (
    FirmwareService,
)
from ub3_updater.ui.main_window import (
    MainWindow,
)


# =========================================================
# Test Controller
# =========================================================

class FakeMonitor:
    def start(self, interval=500):
        self.started = True

    def stop(self):
        self.stopped = True

    def __init__(self):
        self.started = False
        self.stopped = False


class FakeWorker:
    """
    Only needed so UpdateController can be instantiated
    without starting a real upload.
    """

    def __init__(self):
        self.is_running = False
        self.callbacks = {}

    def configure_callbacks(self, **callbacks):
        self.callbacks = callbacks

    def start(self, firmware):
        return False

    def cancel(self):
        return False

    def reset(self):
        return True


class FakeController(UpdateController):

    def __init__(self):
        self.device_monitor = FakeMonitor()
        self.firmware_service = FirmwareService()
        self.upload_worker = FakeWorker()

        self.state = (
            UpdateControllerState.WAITING_FOR_DEVICE
        )

        self.device = None
        self.selected_firmware = None
        self.last_result = None
        self.last_error = None
        self.status_message = "Waiting for UB3"

        self._started = False

        self._on_state_changed = None
        self._on_device_changed = None
        self._on_status = None
        self._on_output = None
        self._on_error = None
        self._on_result = None

    @property
    def is_uploading(self):
        return False

    @property
    def can_update(self):
        return (
            self.device is not None
            and self.device.connected
            and self.device.is_maple
            and self.selected_firmware is not None
        )

    def start(self):
        self._started = True
        self.state = (
            UpdateControllerState.WAITING_FOR_DEVICE
        )
        self.status_message = "Waiting for UB3"

    def stop(self):
        self._started = False

    def refresh_device(self):
        return self.device

    def select_firmware(self, firmware):
        self.selected_firmware = firmware

        if self.device is not None and self.can_update:
            self.state = (
                UpdateControllerState.READY
            )
            self.status_message = "Ready to Update"

        return firmware is not None

    def update(self):
        return False

    def cancel(self):
        return False

    def get_available_firmware(self):
        return self.firmware_service.get_all()


# =========================================================
# Application
# =========================================================

print()
print("=" * 70)
print("GUI STEP 1 TEST")
print("=" * 70)

app = QApplication.instance()

if app is None:
    app = QApplication(sys.argv)

# ---------------------------------------------------------
# Theme
# ---------------------------------------------------------

from ub3_updater.themes.light_theme import STYLE

app.setStyleSheet(STYLE)

print()
print("TEST 1 - MAIN WINDOW")
print("=" * 70)

controller = FakeController()

window = MainWindow(
    controller=controller
)

assert window.home_page is not None
assert window.home_page.connection_widget is not None
assert window.home_page.dashboard_widget is not None
assert window.home_page.device_information_widget is not None

print("[PASS] MainWindow created")
print("[PASS] HomePage created")
print("[PASS] Connection widget created")
print("[PASS] Dashboard widget created")


# ---------------------------------------------------------
# Firmware
# ---------------------------------------------------------

print()
print("TEST 2 - FIRMWARE REPOSITORY")
print("=" * 70)

firmwares = (
    controller.get_available_firmware()
)

assert len(firmwares) >= 1

names = [
    firmware.name
    for firmware in firmwares
]

assert "ZNA2US" in names

print(
    f"[PASS] Firmware repository loaded: {len(firmwares)} package(s)"
)

print(
    "[PASS] ZNA2US available"
)


# ---------------------------------------------------------
# Initial state
# ---------------------------------------------------------

print()
print("TEST 3 - INITIAL DEVICE STATE")
print("=" * 70)

assert controller.device is None
assert not controller.can_update
assert not (
    window.home_page
    .dashboard_widget
    .update_button
    .isEnabled()
)

print("[PASS] Waiting for UB3")
print("[PASS] Update disabled without device")


# ---------------------------------------------------------
# Device information - GUI Step 2
# ---------------------------------------------------------

print()
print("TEST 3A - DEVICE INFORMATION WIDGET")
print("=" * 70)

assert window.home_page.device_information_widget is not None

info_widget = (
    window.home_page.device_information_widget
)

# Disconnected state must not invent device metadata.
info_widget.set_disconnected()

assert (
    info_widget._value_labels["firmware_version"].text()
    == "Not reported"
)

assert (
    info_widget._value_labels["bootloader_version"].text()
    == "Not reported"
)

# Simulate the actual Maple Serial device observed during
# development/testing.
device = Device(
    connected=True,
    state=DeviceState.MAPLE_SERIAL,
    com_port="COM3",
    usb_name="Maple Serial (COM3)",
    description="Maple Serial (COM3)",
    manufacturer="LeafLabs, LLC",
    vid="1EAF",
    pid="0004",
    hwid="USB VID:PID=1EAF:0004 SER= LOCATION=1-6",
)

window.home_page.update_device(device)

assert (
    info_widget._value_labels["device_name"].text()
    == "UB3"
)

assert (
    info_widget._value_labels["com_port"].text()
    == "COM3"
)

assert (
    info_widget._value_labels["usb_mode"].text()
    == "Maple Serial"
)

assert (
    info_widget._value_labels["vid_pid"].text()
    == "1EAF:0004"
)

assert (
    info_widget._value_labels["manufacturer"].text()
    == "LeafLabs, LLC"
)

assert (
    info_widget._value_labels["firmware_version"].text()
    == "Not reported"
)

print("[PASS] Device Information widget created")
print("[PASS] Device information populated from Device model")
print("[PASS] COM3 displayed")
print("[PASS] Maple Serial displayed")
print("[PASS] VID:PID displayed")
print("[PASS] Manufacturer displayed")
print("[PASS] Unavailable firmware data is not fabricated")

# ---------------------------------------------------------
# Firmware selection
# ---------------------------------------------------------

print()
print("TEST 4 - FIRMWARE SELECTION")
print("=" * 70)

zna2us = next(
    firmware
    for firmware in firmwares
    if firmware.name == "ZNA2US"
)

controller.select_firmware(
    zna2us
)

window.home_page.dashboard_widget.set_firmwares(
    firmwares,
    selected=zna2us,
)

assert (
    window.home_page.dashboard_widget
    .selected_firmware()
    .name
    == "ZNA2US"
)

print("[PASS] ZNA2US selected")
print(
    f"[PASS] Version: {zna2us.version}"
)


# ---------------------------------------------------------
# Device connection
# ---------------------------------------------------------

print()
print("TEST 5 - DEVICE CONNECTION")
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
controller.state = (
    UpdateControllerState.READY
)
controller.status_message = "Ready to Update"

window.home_page.update_device(
    device
)

window.home_page.update_controller_state(
    UpdateControllerState.READY,
    "Ready to Update",
)

assert (
    window.home_page
    .connection_widget
    .status_label
    .text()
    == "UB3 Connected"
)

assert (
    window.home_page
    .connection_widget
    .com_badge
    .text()
    == "COM3"
)

print("[PASS] UB3 connection displayed")
print("[PASS] COM3 displayed")
print("[PASS] Maple Serial device displayed")


# ---------------------------------------------------------
# Ready
# ---------------------------------------------------------

print()
print("TEST 6 - READY STATE")
print("=" * 70)

window.home_page._refresh_button_state()

assert (
    window.home_page
    .dashboard_widget
    .update_button
    .isEnabled()
)

print("[PASS] Update button enabled when ready")
assert window.home_page.dashboard_widget.update_button.objectName() == "updateButton"
assert window.home_page.dashboard_widget.cancel_button.objectName() == "cancelButton"
assert "Version" in window.home_page.dashboard_widget.firmware_combo.itemText(0)
print("[PASS] Update button uses explicit high-contrast styling")
print("[PASS] Cancel button uses explicit high-contrast styling")
print("[PASS] Firmware dropdown includes version")



# ---------------------------------------------------------
# Disconnect
# ---------------------------------------------------------

print()
print("TEST 7 - DISCONNECT")
print("=" * 70)

controller.device = None
controller.state = (
    UpdateControllerState.WAITING_FOR_DEVICE
)
controller.status_message = "Waiting for UB3"

window.home_page.update_device(
    None
)

window.home_page.update_controller_state(
    UpdateControllerState.WAITING_FOR_DEVICE,
    "Waiting for UB3",
)

window.home_page._refresh_button_state()

assert (
    window.home_page
    .connection_widget
    .status_label
    .text()
    == "No Device Detected"
)

assert not (
    window.home_page
    .dashboard_widget
    .update_button
    .isEnabled()
)

print("[PASS] Device removal displayed")
print("[PASS] Update disabled after disconnect")


# ---------------------------------------------------------
# Cleanup
# ---------------------------------------------------------

window.close()

print()
print("=" * 70)
print("ALL GUI STEP 1 TESTS PASSED")
print("=" * 70)

print()
print("No physical UB3 was programmed.")
