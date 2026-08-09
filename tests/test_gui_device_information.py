"""
UB3 Firmware Updater - GUI Step 2 Device Information Test

No physical UB3 is required.
"""

from __future__ import annotations

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import bootstrap

from PySide6.QtWidgets import QApplication

from ub3_updater.models.device import Device, DeviceState
from ub3_updater.ui.main_window import MainWindow
from ub3_updater.controllers.update_controller import (
    UpdateController,
    UpdateControllerState,
)
from ub3_updater.services.firmware_service import FirmwareService


class FakeController(UpdateController):
    def __init__(self):
        self.firmware_service = FirmwareService()
        self.device = None
        self.selected_firmware = None
        self.state = UpdateControllerState.WAITING_FOR_DEVICE
        self.status_message = "Waiting for UB3"

    @property
    def can_update(self):
        return (
            self.device is not None
            and self.device.connected
            and self.device.is_maple
            and self.selected_firmware is not None
        )

    @property
    def is_uploading(self):
        return False

    def start(self):
        pass

    def stop(self):
        pass

    def refresh_device(self):
        return self.device

    def select_firmware(self, firmware):
        self.selected_firmware = firmware
        return firmware is not None

    def update(self):
        return False

    def cancel(self):
        return False

    def get_available_firmware(self):
        return self.firmware_service.get_all()



print()
print("=" * 70)
print("GUI STEP 2 - DEVICE INFORMATION TEST")
print("=" * 70)

app = QApplication.instance() or QApplication(sys.argv)

from ub3_updater.themes.light_theme import STYLE
app.setStyleSheet(STYLE)

controller = FakeController()
window = MainWindow(controller=controller)

info = window.home_page.device_information_widget

# ---------------------------------------------------------
# Test 1 - initial state
# ---------------------------------------------------------

print()
print("TEST 1 - INITIAL DEVICE INFORMATION")
print("=" * 70)

assert info._value_labels["device_name"].text() == "Not reported"
assert info._value_labels["com_port"].text() == "Not reported"
assert info._value_labels["firmware_version"].text() == "Not reported"

print("[PASS] Device information starts empty")
print("[PASS] Firmware version is not fabricated")

# ---------------------------------------------------------
# Test 2 - connected Maple Serial device
# ---------------------------------------------------------

print()
print("TEST 2 - MAPLE SERIAL DEVICE")
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
    hwid="USB VID:PID=1EAF:0004 SER= LOCATION=1-6",
)

window.home_page.update_device(device)

assert info._value_labels["device_name"].text() == "UB3"
assert info._value_labels["com_port"].text() == "COM3"
assert info._value_labels["usb_mode"].text() == "Maple Serial"
assert info._value_labels["vid_pid"].text() == "1EAF:0004"
assert info._value_labels["manufacturer"].text() == "LeafLabs, LLC"
assert "1EAF:0004" in info._value_labels["hardware_id"].text()

print("[PASS] Device name")
print("[PASS] COM port")
print("[PASS] Maple Serial mode")
print("[PASS] VID:PID")
print("[PASS] Manufacturer")
print("[PASS] Hardware ID")

# ---------------------------------------------------------
# Test 3 - unavailable fields
# ---------------------------------------------------------

print()
print("TEST 3 - UNAVAILABLE DEVICE METADATA")
print("=" * 70)

assert info._value_labels["board_id"].text() == "Not reported"
assert info._value_labels["bootloader_version"].text() == "Not reported"
assert info._value_labels["firmware_version"].text() == "Not reported"
assert info._value_labels["hardware_version"].text() == "Not reported"
assert info._value_labels["device_type"].text() == "Not reported"

print("[PASS] Board ID explicitly marked unavailable")
print("[PASS] Bootloader version explicitly marked unavailable")
print("[PASS] Firmware version explicitly marked unavailable")
print("[PASS] Hardware version explicitly marked unavailable")
print("[PASS] Device type explicitly marked unavailable")

# ---------------------------------------------------------
# Test 4 - disconnect
# ---------------------------------------------------------

print()
print("TEST 4 - DEVICE DISCONNECT")
print("=" * 70)

window.home_page.update_device(None)

for label in info._value_labels.values():
    assert label.text() == "Not reported"

print("[PASS] Device information cleared after disconnect")

window.close()

print()
print("=" * 70)
print("ALL GUI STEP 2 TESTS PASSED")
print("=" * 70)
print("No physical UB3 was programmed.")
