"""
STEP 6.9 - COMPLETE GUI WORKFLOW INTEGRATION

Validates that the Home page presents one coherent operator
workflow while preserving the existing controller, device,
firmware, worker, and upload contracts.

No physical UB3 is programmed.
"""
from __future__ import annotations
import os, sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import bootstrap
from PySide6.QtWidgets import QApplication

from ub3_updater.controllers.update_controller import UpdateControllerState
from ub3_updater.models.device import Device, DeviceState
from ub3_updater.models.upload_result import UploadResult
from ub3_updater.services.firmware_service import FirmwareService
from ub3_updater.ui.main_window import MainWindow

app = QApplication.instance() or QApplication(sys.argv)

class ControllerStub:
    def __init__(self):
        self.firmware_service = FirmwareService()
        self.selected_firmware = None
        self.device = None
        self.status_message = "Waiting for UB3"
        self._state = UpdateControllerState.WAITING_FOR_DEVICE
        self._callbacks = {}

    @property
    def state(self): return self._state
    @property
    def is_uploading(self):
        return self._state == UpdateControllerState.UPLOADING
    @property
    def can_update(self):
        return bool(
            self.selected_firmware
            and self.device
            and self.device.connected
            and self._state != UpdateControllerState.UPLOADING
        )

    def start(self): return True
    def stop(self): return True
    def refresh_device(self): return self.device
    def get_available_firmware(self): return self.firmware_service.get_all()
    def select_firmware(self, firmware):
        self.selected_firmware = firmware
        return firmware
    def cancel(self): return False
    def set_on_device_changed(self, cb): self._callbacks["device"] = cb
    def set_on_state_changed(self, cb): self._callbacks["state"] = cb
    def set_on_status(self, cb): self._callbacks["status"] = cb
    def set_on_output(self, cb): self._callbacks["output"] = cb
    def set_on_result(self, cb): self._callbacks["result"] = cb
    def set_on_error(self, cb): self._callbacks["error"] = cb

    def validate_before_update(self, expected_device=None):
        class Validation:
            valid = True
            message = "Ready"
        return Validation()

    def confirm_update(self, validation): return False
    def reset_worker(self): return True

print("=" * 70)
print("STEP 6.9 - COMPLETE GUI WORKFLOW INTEGRATION")
print("=" * 70)

controller = ControllerStub()
window = MainWindow(controller=controller)
window.show()
home = window.home_page
app.processEvents()

assert home.workflow_summary_card.objectName() == "workflowSummaryCard"
assert set(home.workflow_step_widgets) == {"connect", "select", "update", "result"}
print("[PASS] Unified four-stage workflow summary created")

assert home.workflow_step_widgets["connect"]["badge"].text() == "Waiting"
assert home.workflow_step_widgets["select"]["badge"].text() == "Select firmware"
assert home.workflow_step_widgets["update"]["badge"].text() == "Unavailable"
assert home.workflow_step_widgets["result"]["badge"].text() == "Awaiting result"
print("[PASS] Initial workflow state is clear")

device = Device(
    connected=True,
    state=DeviceState.MAPLE_SERIAL,
    com_port="COM7",
    usb_name="Maple Serial (COM7)",
    description="Maple Serial (COM7)",
    manufacturer="LeafLabs, LLC",
    vid="1EAF",
    pid="0004",
)
# The real controller remains the source of truth for the current device.
# Mirror that contract in the test stub before exercising the HomePage view.
controller.device = device
home.update_device(device)
assert home.workflow_step_widgets["connect"]["badge"].text() == "Connected"
print("[PASS] Device connection advances workflow")

firmware = controller.firmware_service.get_all()[0]
home._firmware_changed(firmware)
assert home.workflow_step_widgets["select"]["badge"].text() == "Selected"
assert home.workflow_step_widgets["update"]["badge"].text() == "Ready"
print("[PASS] Firmware selection advances workflow to Ready")

controller._state = UpdateControllerState.UPLOADING
home.update_controller_state(
    UpdateControllerState.UPLOADING,
    "Uploading Firmware",
)
assert home.workflow_step_widgets["update"]["badge"].text() == "In progress"
assert home.workflow_step_widgets["update"]["badge"].status() == "warning"
print("[PASS] Active upload state is clearly represented")

controller._state = UpdateControllerState.SUCCESS
result = UploadResult.success_result(
    message="Firmware upload completed successfully.",
    firmware_name=firmware.name,
    firmware_version=firmware.version,
    firmware_path=str(firmware.path),
    com_port="COM7",
    device_state="Maple Serial",
    return_code=0,
    duration_seconds=10.0,
)
home.show_result(result)
assert home.workflow_step_widgets["result"]["badge"].text() == "Success"
assert home.workflow_step_widgets["result"]["badge"].status() == "success"
print("[PASS] Successful result completes the workflow")

controller._state = UpdateControllerState.FAILED
home.update_controller_state(
    UpdateControllerState.FAILED,
    "Update Failed",
)
assert home.workflow_step_widgets["result"]["badge"].text() == "Failed"
assert home.workflow_step_widgets["result"]["badge"].status() == "error"
print("[PASS] Failure result remains visible and diagnostic")

assert home.left_scroll_area.horizontalScrollBarPolicy().name == "ScrollBarAlwaysOff"
assert home.right_scroll_area.horizontalScrollBarPolicy().name == "ScrollBarAlwaysOff"
print("[PASS] Home workflow preserves independent vertical scrolling")

window.close()
print("=" * 70)
print("ALL STEP 6.9 COMPLETE GUI WORKFLOW TESTS PASSED")
print("=" * 70)
print("No physical UB3 was programmed.")
