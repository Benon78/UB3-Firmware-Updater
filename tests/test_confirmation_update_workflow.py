"""
======================================================================
UB3 FIRMWARE UPDATER
STEP 4.3 - CONFIRMATION TO FINAL VALIDATION WORKFLOW TEST
======================================================================

Validates the safety boundary between the confirmation dialog and
UploadWorker.

No physical UB3 is programmed.
"""

from pathlib import Path
import tempfile

import bootstrap

from ub3_updater.controllers.update_controller import (
    UpdateController,
    UpdateControllerState,
)
from ub3_updater.models.device import Device, DeviceState
from ub3_updater.models.firmware import Firmware
from ub3_updater.models.pre_update_validation import (
    PreUpdateValidationResult,
)
from ub3_updater.workers.upload_worker import UploadWorkerState


# =====================================================================
# TEST DOUBLES
# =====================================================================

class FakeSignal:
    def __init__(self):
        self.callbacks = []

    def connect(self, callback):
        self.callbacks.append(callback)

    def emit(self, *args):
        for callback in list(self.callbacks):
            callback(*args)


class FakeDeviceService:
    def __init__(self, device=None):
        self.current_device = device
        self.scan_count = 0

    def scan(self):
        self.scan_count += 1
        return self.current_device


class FakeDeviceMonitor:
    def __init__(self, device=None):
        self.service = FakeDeviceService(device)
        self.device_changed = FakeSignal()
        self.device_connected = FakeSignal()
        self.device_disconnected = FakeSignal()
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True


class FakeFirmwareService:
    def __init__(self, firmware):
        self.firmware = firmware

    def validate(self, firmware):
        if firmware is None:
            return False, "No firmware selected."

        if not firmware.is_valid_file():
            return False, "Firmware file does not exist or is invalid."

        return True, ""

    def get_all(self):
        return [self.firmware]

    def get_available(self):
        return [self.firmware]


class FakeUploadWorker:
    def __init__(self):
        self.state = UploadWorkerState.IDLE
        self.is_running = False
        self.start_count = 0
        self.firmware = None

        self._on_state_changed = None
        self._on_progress = None
        self._on_completed = None
        self._on_error = None
        self._on_output = None

    def configure_callbacks(
        self,
        on_state_changed=None,
        on_progress=None,
        on_completed=None,
        on_error=None,
    ):
        self._on_state_changed = on_state_changed
        self._on_progress = on_progress
        self._on_completed = on_completed
        self._on_error = on_error

    def set_on_output(self, callback):
        self._on_output = callback

    def start(self, firmware):
        if self.is_running:
            return False

        self.firmware = firmware
        self.start_count += 1
        self.is_running = True
        self.state = UploadWorkerState.UPLOADING

        if self._on_state_changed:
            self._on_state_changed(self.state)

        return True

    def cancel(self):
        if not self.is_running:
            return False
        self.is_running = False
        self.state = UploadWorkerState.CANCELLED
        return True

    def reset(self):
        if self.is_running:
            return False
        self.state = UploadWorkerState.IDLE
        self.firmware = None
        return True


# =====================================================================
# HELPERS
# =====================================================================

def make_device(com_port="COM3"):
    return Device(
        connected=True,
        state=DeviceState.MAPLE_SERIAL,
        com_port=com_port,
        usb_name=f"Maple Serial ({com_port})",
        description=f"Maple Serial ({com_port})",
        manufacturer="LeafLabs, LLC",
        vid="1EAF",
        pid="0004",
        hwid="USB VID:PID=1EAF:0004",
    )


def make_firmware(path, name="ZNA2US", version="1.00"):
    return Firmware(
        name=name,
        version=version,
        target_device="UB3",
        filename=Path(path).name,
        path=str(path),
        size=Path(path).stat().st_size,
    )


def make_validation(device, firmware):
    return PreUpdateValidationResult(
        valid=True,
        message="Pre-update validation passed.",
        device=device,
        firmware=firmware,
        checks={
            "device_connected": True,
            "maple_serial": True,
            "same_device": True,
            "firmware_selected": True,
            "firmware_valid": True,
        },
    )


def build_controller(device, firmware):
    monitor = FakeDeviceMonitor(device)
    firmware_service = FakeFirmwareService(firmware)
    worker = FakeUploadWorker()

    controller = UpdateController(
        device_monitor=monitor,
        firmware_service=firmware_service,
        upload_worker=worker,
    )

    controller.device = device
    controller.selected_firmware = firmware
    controller.state = UpdateControllerState.READY
    controller.status_message = "Ready to Update"

    return controller, monitor, worker


# =====================================================================
# TEST HEADER
# =====================================================================

print()
print("=" * 70)
print("STEP 4.3 - CONFIRMATION TO FINAL VALIDATION WORKFLOW TEST")
print("=" * 70)


with tempfile.TemporaryDirectory() as temp_dir:

    firmware_path = (
        Path(temp_dir)
        / "UnlockBoxIII_ZNA2US_1.00.bin"
    )

    firmware_path.write_bytes(
        b"UB3 TEST FIRMWARE"
    )

    device = make_device("COM3")
    firmware = make_firmware(firmware_path)

    # ================================================================
    # TEST 1 - CONFIRMED UPDATE REQUIRES SECOND SCAN
    # ================================================================

    print()
    print("TEST 1 - CONFIRMED UPDATE REQUIRES SECOND SCAN")
    print("=" * 70)

    controller, monitor, worker = build_controller(
        device,
        firmware,
    )

    first_validation = controller.validate_before_update(
        expected_device=device,
    )

    assert first_validation.valid is True
    assert monitor.service.scan_count == 1

    started = controller.confirm_update(
        first_validation
    )

    assert started is True
    assert monitor.service.scan_count == 2
    assert worker.start_count == 1
    assert worker.firmware is firmware
    assert controller.state == UpdateControllerState.UPLOADING

    print("[PASS] First validation succeeded")
    print("[PASS] Confirmation accepted")
    print("[PASS] Second fresh device scan performed")
    print("[PASS] UploadWorker started only after second validation")
    print("[PASS] Correct firmware propagated")

    # ================================================================
    # TEST 2 - DEVICE REPLACED WHILE DIALOG WAS OPEN
    # ================================================================

    print()
    print("TEST 2 - DEVICE REPLACED WHILE DIALOG WAS OPEN")
    print("=" * 70)

    controller, monitor, worker = build_controller(
        device,
        firmware,
    )

    first_validation = controller.validate_before_update(
        expected_device=device,
    )

    assert first_validation.valid is True
    assert monitor.service.scan_count == 1

    replacement = make_device("COM7")
    monitor.service.current_device = replacement

    started = controller.confirm_update(
        first_validation
    )

    assert started is False
    assert monitor.service.scan_count == 2
    assert worker.start_count == 0
    assert controller.state != UpdateControllerState.UPLOADING

    print("[PASS] Replacement UB3 detected")
    print("[PASS] Device identity mismatch rejected")
    print("[PASS] UploadWorker was not started")

    # ================================================================
    # TEST 3 - DEVICE DISCONNECTED WHILE DIALOG WAS OPEN
    # ================================================================

    print()
    print("TEST 3 - DEVICE DISCONNECTED WHILE DIALOG WAS OPEN")
    print("=" * 70)

    controller, monitor, worker = build_controller(
        device,
        firmware,
    )

    first_validation = controller.validate_before_update(
        expected_device=device,
    )

    assert first_validation.valid is True

    monitor.service.current_device = None

    started = controller.confirm_update(
        first_validation
    )

    assert started is False
    assert monitor.service.scan_count == 2
    assert worker.start_count == 0
    assert controller.device is None

    print("[PASS] Disconnection detected")
    print("[PASS] Final validation rejected update")
    print("[PASS] UploadWorker was not started")

    # ================================================================
    # TEST 4 - FIRMWARE CHANGED WHILE DIALOG WAS OPEN
    # ================================================================

    print()
    print("TEST 4 - FIRMWARE CHANGED WHILE DIALOG WAS OPEN")
    print("=" * 70)

    controller, monitor, worker = build_controller(
        device,
        firmware,
    )

    first_validation = controller.validate_before_update(
        expected_device=device,
    )

    changed_path = (
        Path(temp_dir)
        / "UnlockBoxIII_ZMJ_1.00.bin"
    )

    changed_path.write_bytes(
        b"DIFFERENT TEST FIRMWARE"
    )

    changed_firmware = make_firmware(
        changed_path,
        name="ZMJ",
        version="1.00",
    )

    controller.selected_firmware = (
        changed_firmware
    )

    started = controller.confirm_update(
        first_validation
    )

    assert started is False
    assert monitor.service.scan_count == 1
    assert worker.start_count == 0

    print("[PASS] Firmware change detected")
    print("[PASS] Confirmed firmware identity protected")
    print("[PASS] UploadWorker was not started")

    # ================================================================
    # TEST 5 - INVALID CONFIRMATION RESULT
    # ================================================================

    print()
    print("TEST 5 - INVALID CONFIRMATION RESULT")
    print("=" * 70)

    controller, monitor, worker = build_controller(
        device,
        firmware,
    )

    invalid = PreUpdateValidationResult(
        valid=False,
        message="Device is no longer available.",
        device=device,
        firmware=firmware,
        checks={
            "device_connected": False,
            "maple_serial": False,
            "same_device": False,
            "firmware_selected": True,
            "firmware_valid": True,
        },
    )

    started = controller.confirm_update(
        invalid
    )

    assert started is False
    assert monitor.service.scan_count == 0
    assert worker.start_count == 0

    print("[PASS] Invalid validation result rejected")
    print("[PASS] No unnecessary device scan performed")
    print("[PASS] UploadWorker was not started")

    # ================================================================
    # TEST 6 - CONFIRMED DEVICE/FIRMWARE PRESERVED
    # ================================================================

    print()
    print("TEST 6 - CONFIRMED DEVICE/FIRMWARE PRESERVED")
    print("=" * 70)

    controller, monitor, worker = build_controller(
        device,
        firmware,
    )

    first_validation = make_validation(
        device,
        firmware,
    )

    assert first_validation.device is device
    assert first_validation.firmware is firmware

    started = controller.confirm_update(
        first_validation
    )

    assert started is True
    assert worker.firmware is firmware
    assert controller.device is device

    print("[PASS] Confirmed device identity preserved")
    print("[PASS] Confirmed firmware identity preserved")
    print("[PASS] Correct firmware passed to UploadWorker")


print()
print("=" * 70)
print("ALL STEP 4.3 CONFIRMATION WORKFLOW TESTS PASSED")
print("=" * 70)
print()
print("No physical UB3 was programmed.")
