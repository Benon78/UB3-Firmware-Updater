"""
=========================================================
UB3 Firmware Updater

UpdateController Test

No physical UB3 is programmed.

Tests:
    1. Initial state
    2. Controller start
    3. Device connection
    4. Firmware selection
    5. Ready state
    6. Update start
    7. Uploading state
    8. Successful upload
    9. Success with warning
    10. Failed upload
    11. Device disconnect
    12. Next UB3 connection
    13. Duplicate update protection
    14. Cancellation
=========================================================
"""

from enum import Enum
from pathlib import Path
import time

import bootstrap

from ub3_updater.models.device import (
    Device,
)

from ub3_updater.models.firmware import (
    Firmware,
)

from ub3_updater.models.upload_result import (
    UploadResult,
    UploadStatus,
)

from ub3_updater.workers.upload_worker import (
    UploadWorkerState,
)

from ub3_updater.controllers.update_controller import (
    UpdateController,
    UpdateControllerState,
)


# =========================================================
# SIGNAL MOCK
# =========================================================

class FakeSignal:

    def __init__(self):

        self.callbacks = []

    def connect(
        self,
        callback,
    ):

        self.callbacks.append(
            callback
        )

    def emit(
        self,
        *args,
    ):

        for callback in list(
            self.callbacks
        ):

            callback(
                *args
            )


# =========================================================
# FAKE DEVICE MONITOR
# =========================================================

class FakeDeviceMonitor:

    def __init__(self):

        self.device_changed = FakeSignal()

        self.device_connected = FakeSignal()

        self.device_disconnected = FakeSignal()

        self.started = False

        self.stopped = False

        self.service = FakeDeviceService()

    def start(self):

        self.started = True

    def stop(self):

        self.stopped = True

    def connect_device(
        self,
        device,
    ):

        self.service.current_device = (
            device
        )

        self.device_connected.emit(
            device
        )

        self.device_changed.emit(
            device
        )

    def disconnect_device(self):

        self.service.current_device = (
            Device()
        )

        self.device_disconnected.emit()

        self.device_changed.emit(
            self.service.current_device
        )


class FakeDeviceService:

    def __init__(self):

        self.current_device = Device()

    def scan(self):

        return self.current_device


# =========================================================
# FAKE FIRMWARE SERVICE
# =========================================================

class FakeFirmwareService:

    def __init__(self):

        self.firmware = (
            Firmware(
                name="ZNA2US",
                version="1.00",
                path=str(
                    Path(
                        r"C:\tmp\test_firmware.bin"
                    )
                ),
            )
        )

    def get_available(self):

        return [
            self.firmware
        ]


# =========================================================
# FAKE UPLOAD WORKER
# =========================================================

class FakeUploadWorker:

    def __init__(self):

        self.state = (
            UploadWorkerState.IDLE
        )

        self.result = None

        self.exception = None

        self.firmware = None

        self.is_running = False

        self.start_count = 0

        self.cancel_count = 0

        self.reset_count = 0

        self._on_state_changed = None

        self._on_progress = None

        self._on_completed = None

        self._on_error = None

        self._on_output = None

    # -----------------------------------------------------
    # Callbacks
    # -----------------------------------------------------

    def configure_callbacks(
        self,
        on_state_changed=None,
        on_progress=None,
        on_completed=None,
        on_error=None,
    ):

        self._on_state_changed = (
            on_state_changed
        )

        self._on_progress = (
            on_progress
        )

        self._on_completed = (
            on_completed
        )

        self._on_error = (
            on_error
        )

    def set_on_output(
        self,
        callback,
    ):

        self._on_output = callback

    # -----------------------------------------------------
    # Start
    # -----------------------------------------------------

    def start(
        self,
        firmware,
    ):

        if self.is_running:

            return False

        self.firmware = firmware

        self.start_count += 1

        self.is_running = True

        self.state = (
            UploadWorkerState.STARTING
        )

        if self._on_state_changed:

            self._on_state_changed(
                self.state
            )

        self.state = (
            UploadWorkerState.UPLOADING
        )

        if self._on_state_changed:

            self._on_state_changed(
                self.state
            )

        return True

    # -----------------------------------------------------
    # Complete
    # -----------------------------------------------------

    def complete(
        self,
        result,
    ):

        self.result = result

        self.is_running = False

        if result.cancelled:

            # Use FAILED if the installed worker enum
            # does not expose CANCELLED.
            if hasattr(
                UploadWorkerState,
                "CANCELLED",
            ):

                self.state = (
                    UploadWorkerState.CANCELLED
                )

            else:

                self.state = (
                    UploadWorkerState.FAILED
                )

        elif result.success:

            self.state = (
                UploadWorkerState.COMPLETED
            )

        else:

            self.state = (
                UploadWorkerState.FAILED
            )

        if self._on_state_changed:

            self._on_state_changed(
                self.state
            )

        if self._on_completed:

            self._on_completed(
                result
            )

    # -----------------------------------------------------
    # Cancel
    # -----------------------------------------------------

    def cancel(self):

        if not self.is_running:

            return False

        self.cancel_count += 1

        self.is_running = False

        return True

    # -----------------------------------------------------
    # Reset
    # -----------------------------------------------------

    def reset(self):

        if self.is_running:

            return False

        self.reset_count += 1

        self.state = (
            UploadWorkerState.IDLE
        )

        self.result = None

        self.exception = None

        self.firmware = None

        return True


# =========================================================
# RESULT HELPERS
# =========================================================

def success_result():

    return UploadResult.success_result(
        message=(
            "Firmware upload completed successfully."
        ),
        firmware_name="ZNA2US",
        firmware_version="1.00",
        com_port="COM3",
        duration_seconds=12.4,
    )


def warning_result():

    result = (
        UploadResult.success_result(
            message=(
                "Firmware was programmed successfully."
            ),
            firmware_name="ZNA2US",
            firmware_version="1.00",
            com_port="COM3",
            duration_seconds=18.6,
        )
    )

    result.status = (
        UploadStatus.SUCCESS_WITH_WARNING
    )

    result.warning = (
        "Firmware programming completed, "
        "but Maple Loader reported a USB reset warning."
    )

    return result


def failed_result():

    return UploadResult.failed_result(
        message="Upload process failed.",
        firmware_name="ZNA2US",
        firmware_version="1.00",
        com_port="COM3",
    )


# =========================================================
# DEVICE HELPER
# =========================================================

def maple_device(
    com_port="COM3",
):

    # -----------------------------------------------------
    # Use a lightweight test object because different
    # project revisions have used different DeviceState
    # enumerations during development.
    # -----------------------------------------------------

    class MapleState:

        name = "MAPLE_SERIAL"

        value = "Maple Serial"

    return Device(
        connected=True,
        state=MapleState(),
        com_port=com_port,
        vid="1EAF",
        pid="0004",
        manufacturer="LeafLabs, LLC",
        description=f"Maple Serial ({com_port})",
        usb_name=f"Maple Serial ({com_port})",
    )


# =========================================================
# HEADER
# =========================================================

print()
print("=" * 70)
print("UPDATE CONTROLLER TEST")
print("=" * 70)


# =========================================================
# CREATE DEPENDENCIES
# =========================================================

monitor = FakeDeviceMonitor()

firmware_service = (
    FakeFirmwareService()
)

worker = (
    FakeUploadWorker()
)


controller = UpdateController(
    device_monitor=monitor,
    firmware_service=firmware_service,
    upload_worker=worker,
)


# =========================================================
# CALLBACK COLLECTION
# =========================================================

states = []

statuses = []

devices = []

results = []

errors = []


controller.set_on_state_changed(
    lambda state: states.append(
        state
    )
)

controller.set_on_status(
    lambda message: statuses.append(
        message
    )
)

controller.set_on_device_changed(
    lambda device: devices.append(
        device
    )
)

controller.set_on_result(
    lambda result: results.append(
        result
    )
)

controller.set_on_error(
    lambda error: errors.append(
        error
    )
)


# =========================================================
# TEST 1
# INITIAL STATE
# =========================================================

print()
print("=" * 70)
print("TEST 1 - INITIAL STATE")
print("=" * 70)


assert (
    controller.state
    == UpdateControllerState.WAITING_FOR_DEVICE
)


assert (
    controller.device
    is None
)


assert (
    controller.selected_firmware
    is None
)


assert (
    controller.can_update
    is False
)


print(
    "[PASS] Controller starts waiting for UB3"
)


# =========================================================
# TEST 2
# START
# =========================================================

print()
print("=" * 70)
print("TEST 2 - START CONTROLLER")
print("=" * 70)


controller.start()


assert (
    monitor.started
    is True
)


assert (
    controller.is_waiting
    is True
)


print(
    "[PASS] Controller started"
)

print(
    "[PASS] Device monitor started"
)


# =========================================================
# TEST 3
# DEVICE CONNECTION
# =========================================================

print()
print("=" * 70)
print("TEST 3 - DEVICE CONNECTION")
print("=" * 70)


device = maple_device(
    "COM3"
)


monitor.connect_device(
    device
)


assert (
    controller.device
    is device
)


assert (
    controller.com_port
    == "COM3"
)


assert (
    controller.state
    == UpdateControllerState.DEVICE_CONNECTED
)


print(
    "[PASS] UB3 detected"
)

print(
    "[PASS] COM port propagated"
)


# =========================================================
# TEST 4
# FIRMWARE SELECTION
# =========================================================

print()
print("=" * 70)
print("TEST 4 - FIRMWARE SELECTION")
print("=" * 70)


firmware = (
    firmware_service.firmware
)


selected = (
    controller.select_firmware(
        firmware
    )
)


assert (
    selected is True
)


assert (
    controller.selected_firmware
    is firmware
)


assert (
    controller.firmware_name
    == "ZNA2US"
)


assert (
    controller.firmware_version
    == "1.00"
)


print(
    "[PASS] Firmware selected"
)


# =========================================================
# TEST 5
# READY
# =========================================================

print()
print("=" * 70)
print("TEST 5 - READY STATE")
print("=" * 70)


assert (
    controller.is_ready
    is True
)


assert (
    controller.can_update
    is True
)


assert (
    controller.state
    == UpdateControllerState.READY
)


assert (
    controller.status_message
    == "Ready to Update"
)


print(
    "[PASS] Controller ready for update"
)


# =========================================================
# TEST 6
# START UPDATE
# =========================================================

print()
print("=" * 70)
print("TEST 6 - START UPDATE")
print("=" * 70)


started = (
    controller.update()
)


assert (
    started is True
)


assert (
    worker.start_count
    == 1
)


assert (
    worker.firmware
    is firmware
)


assert (
    controller.is_uploading
    is True
)


assert (
    controller.state
    == UpdateControllerState.UPLOADING
)


print(
    "[PASS] UploadWorker started"
)

print(
    "[PASS] Firmware propagated"
)

print(
    "[PASS] Controller entered UPLOADING"
)


# =========================================================
# TEST 7
# SUCCESS
# =========================================================

print()
print("=" * 70)
print("TEST 7 - SUCCESSFUL UPDATE")
print("=" * 70)


worker.complete(
    success_result()
)


assert (
    controller.is_uploading
    is False
)


assert (
    controller.last_result
    is not None
)


assert (
    controller.last_result.success
    is True
)


assert (
    controller.state
    == UpdateControllerState.SUCCESS
)


assert (
    controller.status_message
    == "Firmware upload completed successfully."
)


assert (
    len(results)
    == 1
)


print(
    "[PASS] Upload completed"
)

print(
    "[PASS] SUCCESS state"
)

print(
    "[PASS] Result propagated"
)


# =========================================================
# TEST 8
# SUCCESS WITH WARNING
# =========================================================

print()
print("=" * 70)
print("TEST 8 - SUCCESS WITH WARNING")
print("=" * 70)


controller.reset_worker()


assert (
    controller.state
    == UpdateControllerState.READY
)


controller.update()


worker.complete(
    warning_result()
)


assert (
    controller.state
    == UpdateControllerState.SUCCESS_WITH_WARNING
)


assert (
    controller.last_result.has_warning
    is True
)


assert (
    controller.last_result.success
    is True
)


print(
    "[PASS] SUCCESS_WITH_WARNING propagated"
)


# =========================================================
# TEST 9
# FAILED UPDATE
# =========================================================

print()
print("=" * 70)
print("TEST 9 - FAILED UPDATE")
print("=" * 70)


controller.reset_worker()


assert (
    controller.is_ready
)


controller.update()


worker.complete(
    failed_result()
)


assert (
    controller.state
    == UpdateControllerState.FAILED
)


assert (
    controller.last_result.failed
    is True
)


assert (
    controller.last_result.success
    is False
)


print(
    "[PASS] FAILED state"
)

print(
    "[PASS] Failure result propagated"
)


# =========================================================
# TEST 10
# DISCONNECT
# =========================================================

print()
print("=" * 70)
print("TEST 10 - DEVICE DISCONNECT")
print("=" * 70)


controller.reset_worker()


monitor.disconnect_device()


assert (
    controller.device
    is None
)


assert (
    controller.state
    == UpdateControllerState.WAITING_FOR_DEVICE
)


assert (
    controller.is_waiting
    is True
)


assert (
    controller.can_update
    is False
)


print(
    "[PASS] Device removal detected"
)

print(
    "[PASS] Controller returned to waiting state"
)


# =========================================================
# TEST 11
# NEXT UB3
# =========================================================

print()
print("=" * 70)
print("TEST 11 - NEXT UB3")
print("=" * 70)


next_device = maple_device(
    "COM7"
)


monitor.connect_device(
    next_device
)


assert (
    controller.device
    is next_device
)


assert (
    controller.com_port
    == "COM7"
)


assert (
    controller.selected_firmware
    is firmware
)


assert (
    controller.can_update
    is True
)


assert (
    controller.state
    == UpdateControllerState.READY
)


print(
    "[PASS] Next UB3 detected"
)

print(
    "[PASS] New COM port detected: COM7"
)

print(
    "[PASS] Firmware selection retained"
)

print(
    "[PASS] Ready for next update"
)


# =========================================================
# TEST 12
# DUPLICATE UPDATE
# =========================================================

print()
print("=" * 70)
print("TEST 12 - DUPLICATE UPDATE PROTECTION")
print("=" * 70)


controller.update()


second_start = (
    controller.update()
)


assert (
    second_start is False
)


assert (
    worker.start_count
    >= 4
)


print(
    "[PASS] Duplicate update rejected"
)


# Complete current fake upload
worker.complete(
    success_result()
)


# =========================================================
# TEST 13
# CANCELLATION
# =========================================================

print()
print("=" * 70)
print("TEST 13 - CANCELLATION")
print("=" * 70)


controller.reset_worker()


controller.update()


assert (
    controller.is_uploading
)


cancelled = (
    controller.cancel()
)


assert (
    cancelled is True
)


assert (
    worker.cancel_count
    == 1
)


print(
    "[PASS] Upload cancellation requested"
)


# =========================================================
# TEST 14
# STATUS SNAPSHOT
# =========================================================

print()
print("=" * 70)
print("TEST 14 - STATUS SNAPSHOT")
print("=" * 70)


snapshot = (
    controller.status_snapshot()
)


assert (
    snapshot["com_port"]
    == "COM7"
)


assert (
    snapshot["firmware_name"]
    == "ZNA2US"
)


assert (
    snapshot["firmware_version"]
    == "1.00"
)


assert (
    snapshot["device_connected"]
    is True
)


assert (
    snapshot["is_uploading"]
    is False
)


print(
    "[PASS] Status snapshot"
)


# =========================================================
# TEST 15
# STOP
# =========================================================

print()
print("=" * 70)
print("TEST 15 - STOP CONTROLLER")
print("=" * 70)


controller.stop()


assert (
    monitor.stopped
    is True
)


assert (
    controller._started
    is False
)


print(
    "[PASS] Controller stopped"
)


# =========================================================
# FINAL
# =========================================================

print()
print("=" * 70)
print("FINAL VALIDATION")
print("=" * 70)

print()
print(
    "[PASS] Initial state"
)

print(
    "[PASS] Controller lifecycle"
)

print(
    "[PASS] Device connection"
)

print(
    "[PASS] Firmware selection"
)

print(
    "[PASS] Ready state"
)

print(
    "[PASS] Upload start"
)

print(
    "[PASS] Successful upload"
)

print(
    "[PASS] Success with warning"
)

print(
    "[PASS] Failed upload"
)

print(
    "[PASS] Device disconnect"
)

print(
    "[PASS] Next UB3"
)

print(
    "[PASS] Duplicate update protection"
)

print(
    "[PASS] Cancellation"
)

print(
    "[PASS] Status snapshot"
)

print(
    "[PASS] Controller shutdown"
)

print()
print("=" * 70)
print("ALL UPDATE CONTROLLER TESTS PASSED")
print("=" * 70)

print()
print(
    "No physical UB3 was programmed."
)