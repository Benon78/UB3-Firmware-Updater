"""
UB3 Firmware Updater - GUI Step 6.3 Home / Connect UI Test

Presentation-focused regression test.

Validates the redesigned Home / Connect presentation while
preserving the existing HomePage/controller/device contracts.

No physical UB3 is required.
No firmware is programmed.
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
        self.status_message = "Waiting for UB3"
        self._state = UpdateControllerState.WAITING_FOR_DEVICE
        self.started = False
        self.refresh_count = 0
        self._callbacks = {}

    @property
    def state(self): return self._state
    @property
    def is_uploading(self): return False
    @property
    def can_update(self):
        return bool(self.selected_firmware and self.device and self.device.connected)
    def start(self): self.started=True; return True
    def stop(self): return True
    def refresh_device(self): self.refresh_count += 1
    def get_available_firmware(self): return self.firmware_service.get_all()
    def select_firmware(self, firmware): self.selected_firmware=firmware; return firmware
    def update(self): return False
    def cancel(self): return False
    def set_on_device_changed(self, cb): self._callbacks["device"]=cb
    def set_on_state_changed(self, cb): self._callbacks["state"]=cb
    def set_on_status(self, cb): self._callbacks["status"]=cb
    def set_on_output(self, cb): self._callbacks["output"]=cb
    def set_on_result(self, cb): self._callbacks["result"]=cb
    def set_on_error(self, cb): self._callbacks["error"]=cb

print("=" * 70)
print("STEP 6.3 - HOME / CONNECT UI")
print("=" * 70)

controller=ControllerStub()
window=MainWindow(controller=controller)
home=window.home_page

assert home is not None
assert home.home_status_badge is not None
assert home.home_status_hint is not None
assert home.left_scroll_area is not None
assert home.right_scroll_area is not None
print("[PASS] Home / Connect presentation created")

assert home.home_status_badge.text() == "Waiting for UB3"
assert home.home_status_badge.status() == "neutral"
assert "Connect a UB3" in home.home_status_hint.text()
print("[PASS] Initial waiting-for-device state is clear")

assert home.connection_widget.connection_badge.status() == "error"
assert home.connection_widget.status_label.text() == "No Device Detected"
print("[PASS] Connection card shows disconnected state")

device=Device(
    connected=True,
    state=DeviceState.MAPLE_SERIAL,
    com_port="COM7",
    usb_name="Maple Serial (COM7)",
    description="Maple Serial (COM7)",
    manufacturer="LeafLabs, LLC",
    vid="1EAF",
    pid="0004",
)
home.update_device(device)

assert home.home_status_badge.text() == "UB3 Connected"
assert home.home_status_badge.status() == "success"
assert "COM7" in home.home_status_hint.text()
assert home.connection_widget.connection_badge.status() == "success"
assert home.connection_widget.com_badge.text() == "COM7"
print("[PASS] Connected state uses automatic detected COM port")

home.update_controller_state(
    UpdateControllerState.READY,
    "Ready to Update",
)
assert home.home_status_badge.text() == "Ready"
assert home.home_status_badge.status() == "success"
print("[PASS] Ready state presented as operator-ready")

home.update_controller_state(
    UpdateControllerState.UPLOADING,
    "Uploading",
)
assert home.home_status_badge.text() == "Uploading"
assert home.home_status_badge.status() == "warning"
print("[PASS] Uploading state presented distinctly")

home.update_device(None)
assert home.home_status_badge.text() == "Waiting for UB3"
assert home.home_status_badge.status() == "neutral"
assert home.connection_widget.com_badge.text() == "--"
print("[PASS] Disconnect returns to waiting state")

assert home.refresh_button.objectName() == "refreshButton"
assert home.dashboard_widget.update_button.objectName() == "updateButton"
assert home.dashboard_widget.cancel_button.objectName() == "cancelButton"
print("[PASS] Existing GUI control contracts preserved")

assert home.left_scroll_area.objectName() == "leftHomeScrollArea"
assert home.right_scroll_area.objectName() == "rightHomeScrollArea"
print("[PASS] Existing two-column scroll architecture preserved")

window.close()
print("=" * 70)
print("ALL STEP 6.3 HOME / CONNECT UI TESTS PASSED")
print("=" * 70)
print("No physical UB3 was programmed.")
