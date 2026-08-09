"""
======================================================================
UB3 FIRMWARE UPDATER
STEP 4.1 - PRE-UPDATE VALIDATION TEST
======================================================================

No physical UB3 is programmed.
"""

from pathlib import Path
import tempfile

import bootstrap

from ub3_updater.controllers.update_controller import (
    UpdateController,
)
from ub3_updater.models.device import (
    Device,
    DeviceState,
)
from ub3_updater.models.firmware import (
    Firmware,
)


class FakeSignal:
    def connect(self, callback):
        self.callback = callback


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

    def start(self):
        pass

    def stop(self):
        pass


class FakeFirmwareService:
    def __init__(self, valid=True):
        self.valid = valid
        self.validate_count = 0

    def get_available(self):
        return []

    def validate(self, firmware):
        self.validate_count += 1

        # Mirror the production contract: a firmware package is not
        # valid when its actual file is missing. The fake service must
        # not return True for an intentionally invalid fixture.
        path = getattr(firmware, "path", None)

        if not path or not Path(path).is_file():
            return False, "Firmware file does not exist."

        if self.valid:
            return True, ""

        return False, "Firmware validation failed."


class FakeWorker:
    is_running = False

    def configure_callbacks(self, **kwargs):
        pass

    def start(self, firmware):
        return False

    def cancel(self):
        return False


def make_device(
    com_port="COM3",
    vid="1EAF",
    pid="0004",
):
    return Device(
        connected=True,
        state=DeviceState.MAPLE_SERIAL,
        com_port=com_port,
        usb_name=f"Maple Serial ({com_port})",
        description=f"Maple Serial ({com_port})",
        manufacturer="LeafLabs, LLC",
        vid=vid,
        pid=pid,
        hwid=f"USB VID:PID={vid}:{pid}",
    )


def make_firmware(path):
    return Firmware(
        name="ZNA2US",
        version="1.00",
        target_device="UB3",
        filename=Path(path).name,
        path=str(path),
        size=Path(path).stat().st_size,
    )


print()
print("=" * 70)
print("STEP 4.1 - PRE-UPDATE VALIDATION TEST")
print("=" * 70)


with tempfile.TemporaryDirectory() as temp_dir:

    firmware_path = Path(temp_dir) / "test_firmware.bin"
    firmware_path.write_bytes(b"UB3 TEST FIRMWARE")

    # ================================================================
    # TEST 1 - ALL VALID
    # ================================================================

    print()
    print("TEST 1 - VALID DEVICE + VALID FIRMWARE")
    print("=" * 70)

    device = make_device()
    monitor = FakeDeviceMonitor(device)
    firmware_service = FakeFirmwareService(valid=True)

    controller = UpdateController(
        device_monitor=monitor,
        firmware_service=firmware_service,
        upload_worker=FakeWorker(),
    )

    firmware = make_firmware(firmware_path)

    controller.device = device
    controller.selected_firmware = firmware

    result = controller.validate_before_update(
        expected_device=device
    )

    assert result.valid is True
    assert result.failed is False
    assert result.check_passed("device_connected")
    assert result.check_passed("maple_serial")
    assert result.check_passed("same_device")
    assert result.check_passed("firmware_selected")
    assert result.check_passed("firmware_valid")

    assert monitor.service.scan_count == 1
    assert firmware_service.validate_count == 1

    print("[PASS] Fresh device scan performed")
    print("[PASS] Device connected")
    print("[PASS] Maple Serial verified")
    print("[PASS] Same device verified")
    print("[PASS] Firmware selected")
    print("[PASS] Firmware file validated")
    print("[PASS] Validation succeeds")


    # ================================================================
    # TEST 2 - DEVICE DISCONNECTED
    # ================================================================

    print()
    print("TEST 2 - DEVICE DISCONNECTED")
    print("=" * 70)

    monitor.service.current_device = None

    result = controller.validate_before_update(
        expected_device=device
    )

    assert result.valid is False
    assert result.failed is True
    assert result.check_passed(
        "device_connected"
    ) is False

    print("[PASS] Disconnected device rejected")
    print("[PASS] Update cannot continue")


    # ================================================================
    # TEST 3 - USB MODE CHANGED
    # ================================================================

    print()
    print("TEST 3 - USB MODE CHANGED")
    print("=" * 70)

    usb_serial_device = make_device()

    usb_serial_device.state = (
        DeviceState.USB_SERIAL
    )

    monitor.service.current_device = (
        usb_serial_device
    )

    controller.device = usb_serial_device

    result = controller.validate_before_update(
        expected_device=None
    )

    assert result.valid is False
    assert result.check_passed(
        "device_connected"
    )
    assert result.check_passed(
        "maple_serial"
    ) is False

    print("[PASS] USB Serial mode rejected")
    print("[PASS] Maple Serial requirement enforced")


    # ================================================================
    # TEST 4 - DIFFERENT UB3 CONNECTED
    # ================================================================

    print()
    print("TEST 4 - DIFFERENT UB3 CONNECTED")
    print("=" * 70)

    original_device = make_device(
        com_port="COM3"
    )

    replacement_device = make_device(
        com_port="COM4"
    )

    monitor.service.current_device = (
        replacement_device
    )

    controller.device = original_device
    controller.selected_firmware = firmware

    result = controller.validate_before_update(
        expected_device=original_device
    )

    assert result.valid is False
    assert result.check_passed(
        "device_connected"
    )
    assert result.check_passed(
        "maple_serial"
    )
    assert result.check_passed(
        "same_device"
    ) is False

    assert "different" in (
        result.message.lower()
    )

    print("[PASS] Replacement UB3 detected")
    print("[PASS] Device identity mismatch rejected")
    print("[PASS] Update prevented for different device")


    # ================================================================
    # TEST 5 - FIRMWARE MISSING
    # ================================================================

    print()
    print("TEST 5 - INVALID FIRMWARE")
    print("=" * 70)

    monitor.service.current_device = (
        original_device
    )

    invalid_firmware = Firmware(
        name="ZNA2US",
        version="1.00",
        target_device="UB3",
        filename="missing.bin",
        path=str(
            Path(temp_dir) / "missing.bin"
        ),
        size=0,
    )

    controller.device = original_device
    controller.selected_firmware = (
        invalid_firmware
    )

    result = controller.validate_before_update(
        expected_device=original_device
    )

    assert result.valid is False
    assert result.check_passed(
        "device_connected"
    )
    assert result.check_passed(
        "same_device"
    )
    assert result.check_passed(
        "firmware_selected"
    )
    assert result.check_passed(
        "firmware_valid"
    ) is False

    print("[PASS] Missing firmware rejected")
    print("[PASS] Firmware validation failure blocks update")


    # ================================================================
    # TEST 6 - NO FIRMWARE SELECTED
    # ================================================================

    print()
    print("TEST 6 - NO FIRMWARE SELECTED")
    print("=" * 70)

    controller.selected_firmware = None

    result = controller.validate_before_update(
        expected_device=original_device
    )

    assert result.valid is False
    assert result.check_passed(
        "firmware_selected"
    ) is False

    print("[PASS] Missing firmware selection rejected")


    # ================================================================
    # TEST 7 - RESULT SERIALIZATION
    # ================================================================

    print()
    print("TEST 7 - VALIDATION RESULT")
    print("=" * 70)

    controller.selected_firmware = firmware

    monitor.service.current_device = (
        original_device
    )

    result = controller.validate_before_update(
        expected_device=original_device
    )

    data = result.to_dict()

    assert data["valid"] is True
    assert data["device"] is not None
    assert data["firmware"] is not None
    assert data["checks"]["same_device"] is True

    print("[PASS] Validation result serializes")
    print("[PASS] Device information preserved")
    print("[PASS] Firmware information preserved")
    print("[PASS] Individual checks preserved")


print()
print("=" * 70)
print("ALL STEP 4.1 PRE-UPDATE VALIDATION TESTS PASSED")
print("=" * 70)
print()
print("No physical UB3 was programmed.")
