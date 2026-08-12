"""
UB3 Firmware Updater - Step 6.4 Device Information UI Test

Validates the redesigned device-information presentation and the
horizontal connection-status scroll container.

No physical UB3 is required.
"""
from __future__ import annotations
import os, sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import bootstrap
from PySide6.QtWidgets import QApplication

from ub3_updater.controllers.update_controller import UpdateControllerState
from ub3_updater.models.device import Device, DeviceState
from ub3_updater.services.firmware_service import FirmwareService
from ub3_updater.ui.main_window import MainWindow

app = QApplication.instance() or QApplication(sys.argv)

from ub3_updater.themes.light_theme import STYLE
app.setStyleSheet(STYLE)

class ControllerStub:
    def __init__(self):
        self.firmware_service = FirmwareService()
        self.selected_firmware = None
        self.device = None
        self._state = UpdateControllerState.WAITING_FOR_DEVICE
    @property
    def state(self): return self._state
    @property
    def is_uploading(self): return False
    @property
    def can_update(self): return bool(self.selected_firmware and self.device and self.device.connected)
    def start(self): return True
    def stop(self): return True
    def refresh_device(self): return None
    def get_available_firmware(self): return self.firmware_service.get_all()
    def select_firmware(self, firmware): self.selected_firmware = firmware; return firmware
    def update(self): return False
    def cancel(self): return False

    # MainWindow controller callback contract.
    # The real UpdateController provides these registrations; the
    # Step 6.4 test stub must expose the same interface so the test
    # exercises the actual MainWindow construction path.
    def set_on_device_changed(self, callback): self._on_device_changed = callback
    def set_on_state_changed(self, callback): self._on_state_changed = callback
    def set_on_status(self, callback): self._on_status = callback
    def set_on_output(self, callback): self._on_output = callback
    def set_on_result(self, callback): self._on_result = callback
    def set_on_error(self, callback): self._on_error = callback

print("=" * 70)
print("STEP 6.4 - DEVICE INFORMATION UI")
print("=" * 70)

window = MainWindow(controller=ControllerStub())
home = window.home_page
info = home.device_information_widget
connection = home.connection_widget

assert info.objectName() == "deviceInformationCard"
assert info._value_labels["device_name"].text() == "Not reported"
print("[PASS] Device information card uses UB3 presentation")

assert connection.connection_status_scroll.objectName() == "connectionStatusScroll"
assert connection.connection_status_scroll.horizontalScrollBarPolicy().name == "ScrollBarAsNeeded"
assert connection.connection_status_scroll.verticalScrollBarPolicy().name == "ScrollBarAlwaysOff"
print("[PASS] Connection status has horizontal scrolling and no vertical scrolling")

device = Device(
    connected=True,
    state=DeviceState.MAPLE_SERIAL,
    com_port="COM17",
    usb_name="Maple Serial (COM17)",
    description="Maple Serial (COM17)",
    manufacturer="LeafLabs, LLC",
    vid="1EAF",
    pid="0004",
    hwid="USB VID:PID=1EAF:0004 SER= LOCATION=1-6",
)
home.update_device(device)

expected = {
    "device_name": "UB3",
    "board_id": "Not reported",
    "bootloader_version": "Not reported",
    "firmware_version": "Not reported",
    "hardware_version": "Not reported",
    "device_type": "Not reported",
    "com_port": "COM17",
    "usb_mode": "Maple Serial",
    "vid_pid": "1EAF:0004",
    "manufacturer": "LeafLabs, LLC",
}
for key, value in expected.items():
    assert info._value_labels[key].text() == value, (key, info._value_labels[key].text(), value)
assert "USB VID:PID=1EAF:0004" in info._value_labels["hardware_id"].text()
print("[PASS] Device information renders actual Device model data")

assert connection.com_badge.text() == "COM17"
assert connection.connection_badge.status() == "success"
print("[PASS] Connection status preserves automatic COM detection")

home.update_device(None)
for label in info._value_labels.values():
    assert label.text() == "Not reported"
assert connection.com_badge.text() == "--"
print("[PASS] Disconnect clears device information safely")

window.close()
print("=" * 70)
print("ALL STEP 6.4 DEVICE INFORMATION UI TESTS PASSED")
print("=" * 70)
print("No physical UB3 was programmed.")
