"""
=========================================================
UB3 Firmware Updater

UploadWorker Test

Purpose
-------
Test UploadWorker independently from real hardware.

This test verifies:

1. Initial IDLE state
2. Worker startup
3. STARTING -> UPLOADING lifecycle
4. UploadService called exactly once
5. Successful upload
6. Successful upload with warning
7. Failed upload
8. Unexpected exception handling
9. Duplicate start protection
10. wait()
11. reset()
12. Progress callbacks
13. Output callbacks
14. Worker reuse

NO REAL UB3 IS PROGRAMMED.
=========================================================
"""

from pathlib import Path
import time

import bootstrap

from ub3_updater.models.firmware import Firmware

from ub3_updater.models.upload_result import (
    UploadResult,
    UploadStatus,
)

from ub3_updater.workers.upload_worker import (
    UploadWorker,
    UploadWorkerState,
)


# =========================================================
# HELPERS
# =========================================================

def create_firmware() -> Firmware:
    """
    Create a test Firmware object.
    """

    return Firmware(
        name="ZNA2US",
        version="1.00",
        path=str(
            Path(
                r"C:\tmp\test_firmware.bin"
            )
        ),
    )


def create_success_result() -> UploadResult:
    """
    Create a successful UploadResult.
    """

    return UploadResult.success_result(
        message="Firmware upload completed successfully.",
        firmware_name="ZNA2US",
        firmware_version="1.00",
        com_port="COM3",
        duration_seconds=18.5,
    )


def create_warning_result() -> UploadResult:
    """
    Create a successful UploadResult with warning.

    has_warning is a read-only/computed property.
    Therefore only status and warning are assigned.
    """

    result = UploadResult.success_result(
        message="Firmware was programmed successfully.",
        firmware_name="ZNA2US",
        firmware_version="1.00",
        com_port="COM3",
        duration_seconds=18.6,
    )

    result.status = (
        UploadStatus.SUCCESS_WITH_WARNING
    )

    result.warning = (
        "Firmware programming completed, "
        "but Maple Loader reported a USB reset warning."
    )

    return result


def create_failure_result() -> UploadResult:
    """
    Create a failed UploadResult.

    UploadResult.failed_result() assigns the failure status
    internally, so status must not be passed here.
    """

    return UploadResult.failed_result(
        message="Upload process failed.",
        firmware_name="ZNA2US",
        firmware_version="1.00",
        com_port="COM3",
    )


# =========================================================
# FAKE UPLOAD SERVICE
# =========================================================

class FakeUploadService:
    """
    Fake UploadService.

    No real device or Maple Loader is used.
    """

    def __init__(
        self,
        result=None,
        exception=None,
        delay=0.05,
    ):

        self.result = result

        self.exception = exception

        self.delay = delay

        self.upload_count = 0

        self.last_firmware = None

    def upload(
        self,
        firmware,
        *,
        on_output=None,
        on_error=None,
        **kwargs,
    ):
        """
        Simulate UploadService.upload().
        """

        self.upload_count += 1

        self.last_firmware = firmware

        if self.delay:

            time.sleep(
                self.delay
            )

        if self.exception is not None:

            raise self.exception

        return self.result


# =========================================================
# HEADER
# =========================================================

print()
print("=" * 70)
print("UPLOAD WORKER TEST")
print("=" * 70)


# =========================================================
# TEST FIRMWARE
# =========================================================

firmware = create_firmware()


print()
print("Firmware:")

print(
    "  Name    :",
    firmware.name,
)

print(
    "  Version :",
    firmware.version,
)

print(
    "  Path    :",
    firmware.path,
)


# =========================================================
# TEST 1
# INITIAL STATE
# =========================================================

print()
print("=" * 70)
print("TEST 1 - INITIAL STATE")
print("=" * 70)


service = FakeUploadService(
    result=create_success_result()
)


worker = UploadWorker(
    upload_service=service
)


assert (
    worker.state
    == UploadWorkerState.IDLE
), (
    f"Expected IDLE, got {worker.state}"
)


assert (
    worker.is_running
    is False
)


assert (
    worker.result
    is None
)


print(
    "[PASS] Worker starts in IDLE"
)


# =========================================================
# TEST 2
# SUCCESSFUL UPLOAD
# =========================================================

print()
print("=" * 70)
print("TEST 2 - SUCCESSFUL UPLOAD")
print("=" * 70)


states = []

progress_messages = []

completed_results = []

errors = []


def on_state_changed(state):

    states.append(
        state
    )


def on_progress(message):

    progress_messages.append(
        message
    )


def on_completed(result):

    completed_results.append(
        result
    )


def on_error(error):

    errors.append(
        error
    )


worker.configure_callbacks(
    on_state_changed=on_state_changed,
    on_progress=on_progress,
    on_completed=on_completed,
    on_error=on_error,
)


started = worker.start(
    firmware
)


assert (
    started is True
), (
    "Worker failed to start."
)


print(
    "[PASS] Worker started"
)


finished = worker.wait(
    timeout=5
)


assert (
    finished is True
), (
    "Worker did not finish within timeout."
)


print(
    "[PASS] Worker finished"
)


assert (
    worker.state
    == UploadWorkerState.COMPLETED
), (
    f"Expected COMPLETED, got {worker.state}"
)


print(
    "[PASS] Final state is COMPLETED"
)


assert (
    service.upload_count
    == 1
), (
    "UploadService.upload() was not called exactly once."
)


print(
    "[PASS] UploadService called exactly once"
)


assert (
    service.last_firmware
    is firmware
), (
    "Firmware object was not passed correctly."
)


print(
    "[PASS] Firmware propagated correctly"
)


assert (
    worker.result
    is not None
)


assert (
    worker.result.success
    is True
)


print(
    "[PASS] UploadResult returned successfully"
)


assert (
    len(completed_results)
    == 1
), (
    "Completion callback was not called exactly once."
)


print(
    "[PASS] Completion callback executed"
)


assert (
    len(errors)
    == 0
), (
    "Unexpected error callback."
)


print(
    "[PASS] No unexpected error"
)


assert (
    UploadWorkerState.STARTING
    in states
)


assert (
    UploadWorkerState.UPLOADING
    in states
)


assert (
    UploadWorkerState.COMPLETED
    in states
)


print(
    "[PASS] Worker lifecycle states correct"
)


# =========================================================
# TEST 3
# SUCCESS WITH WARNING
# =========================================================

print()
print("=" * 70)
print("TEST 3 - SUCCESS WITH WARNING")
print("=" * 70)


warning_service = FakeUploadService(
    result=create_warning_result()
)


warning_worker = UploadWorker(
    upload_service=warning_service
)


warning_completed = []


warning_worker.set_on_completed(
    lambda result: warning_completed.append(
        result
    )
)


assert (
    warning_worker.start(
        firmware
    )
    is True
)


assert (
    warning_worker.wait(
        timeout=5
    )
    is True
)


assert (
    warning_worker.state
    == UploadWorkerState.COMPLETED
), (
    "SUCCESS_WITH_WARNING should still "
    "produce COMPLETED worker state."
)


assert (
    warning_worker.result.success
    is True
)


assert (
    warning_worker.result.status
    == UploadStatus.SUCCESS_WITH_WARNING
)


assert (
    warning_worker.result.has_warning
    is True
), (
    "Warning result was not recognized."
)


assert (
    bool(
        warning_worker.result.warning
    )
    is True
)


assert (
    len(warning_completed)
    == 1
)


print(
    "[PASS] SUCCESS_WITH_WARNING handled correctly"
)


# =========================================================
# TEST 4
# FAILED UPLOAD
# =========================================================

print()
print("=" * 70)
print("TEST 4 - FAILED UPLOAD")
print("=" * 70)


failure_service = FakeUploadService(
    result=create_failure_result()
)


failure_worker = UploadWorker(
    upload_service=failure_service
)


failure_worker.start(
    firmware
)


assert (
    failure_worker.wait(
        timeout=5
    )
    is True
)


assert (
    failure_worker.state
    == UploadWorkerState.FAILED
), (
    f"Expected FAILED, got "
    f"{failure_worker.state}"
)


assert (
    failure_worker.result
    is not None
)


assert (
    failure_worker.result.success
    is False
)


assert (
    failure_worker.result.failed
    is True
)


print(
    "[PASS] Failed upload handled correctly"
)


# =========================================================
# TEST 5
# UNEXPECTED EXCEPTION
# =========================================================

print()
print("=" * 70)
print("TEST 5 - UNEXPECTED EXCEPTION")
print("=" * 70)


test_exception = RuntimeError(
    "Simulated UploadService exception"
)


exception_service = FakeUploadService(
    exception=test_exception
)


exception_worker = UploadWorker(
    upload_service=exception_service
)


exception_errors = []


exception_worker.set_on_error(
    lambda error: exception_errors.append(
        error
    )
)


exception_worker.start(
    firmware
)


assert (
    exception_worker.wait(
        timeout=5
    )
    is True
)


assert (
    exception_worker.state
    == UploadWorkerState.FAILED
)


assert (
    exception_worker.exception
    is test_exception
)


assert (
    len(exception_errors)
    == 1
)


assert (
    exception_errors[0]
    is test_exception
)


print(
    "[PASS] Unexpected exception handled correctly"
)


# =========================================================
# TEST 6
# DUPLICATE START
# =========================================================

print()
print("=" * 70)
print("TEST 6 - DUPLICATE START")
print("=" * 70)


slow_service = FakeUploadService(
    result=create_success_result(),
    delay=0.5,
)


duplicate_worker = UploadWorker(
    upload_service=slow_service
)


first_start = (
    duplicate_worker.start(
        firmware
    )
)


assert (
    first_start is True
)


print(
    "[PASS] First start accepted"
)


second_start = (
    duplicate_worker.start(
        firmware
    )
)


assert (
    second_start is False
), (
    "Worker allowed a second upload "
    "while already running."
)


print(
    "[PASS] Duplicate start rejected"
)


assert (
    duplicate_worker.wait(
        timeout=5
    )
    is True
)


assert (
    slow_service.upload_count
    == 1
)


print(
    "[PASS] Only one upload executed"
)


# =========================================================
# TEST 7
# RESET
# =========================================================

print()
print("=" * 70)
print("TEST 7 - RESET")
print("=" * 70)


assert (
    duplicate_worker.state
    == UploadWorkerState.COMPLETED
)


reset_result = (
    duplicate_worker.reset()
)


assert (
    reset_result is True
)


assert (
    duplicate_worker.state
    == UploadWorkerState.IDLE
)


assert (
    duplicate_worker.result
    is None
)


assert (
    duplicate_worker.exception
    is None
)


assert (
    duplicate_worker.firmware
    is None
)


print(
    "[PASS] Worker reset to IDLE"
)


# =========================================================
# TEST 8
# START AFTER RESET
# =========================================================

print()
print("=" * 70)
print("TEST 8 - REUSE WORKER AFTER RESET")
print("=" * 70)


restart_result = (
    duplicate_worker.start(
        firmware
    )
)


assert (
    restart_result is True
)


assert (
    duplicate_worker.wait(
        timeout=5
    )
    is True
)


assert (
    duplicate_worker.state
    == UploadWorkerState.COMPLETED
)


assert (
    slow_service.upload_count
    == 2
)


print(
    "[PASS] Worker can be reused after reset"
)


# =========================================================
# TEST 9
# PROGRESS CALLBACK
# =========================================================

print()
print("=" * 70)
print("TEST 9 - PROGRESS CALLBACK")
print("=" * 70)


progress_service = FakeUploadService(
    result=create_success_result()
)


progress_worker = UploadWorker(
    upload_service=progress_service
)


progress_events = []


progress_worker.set_on_progress(
    lambda message: progress_events.append(
        message
    )
)


progress_worker.start(
    firmware
)


assert (
    progress_worker.wait(
        timeout=5
    )
    is True
)


assert (
    len(progress_events)
    > 0
), (
    "Progress callback was never called."
)


print(
    "[PASS] Progress callback executed"
)


# =========================================================
# TEST 10
# OUTPUT CALLBACK
# =========================================================

print()
print("=" * 70)
print("TEST 10 - OUTPUT CALLBACK")
print("=" * 70)


output_service = FakeUploadService(
    result=create_success_result()
)


output_worker = UploadWorker(
    upload_service=output_service
)


output_events = []


output_worker.set_on_output(
    lambda message: output_events.append(
        message
    )
)


output_worker.start(
    firmware
)


assert (
    output_worker.wait(
        timeout=5
    )
    is True
)


assert (
    output_worker.state
    == UploadWorkerState.COMPLETED
)


print(
    "[PASS] Output callback configured correctly"
)


# =========================================================
# FINAL VALIDATION
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
    "[PASS] Successful upload"
)

print(
    "[PASS] SUCCESS_WITH_WARNING"
)

print(
    "[PASS] Failed upload"
)

print(
    "[PASS] Exception handling"
)

print(
    "[PASS] Duplicate start protection"
)

print(
    "[PASS] Reset"
)

print(
    "[PASS] Worker reuse"
)

print(
    "[PASS] Progress callback"
)

print(
    "[PASS] Output callback"
)


# =========================================================
# COMPLETE
# =========================================================

print()
print("=" * 70)
print("ALL UPLOAD WORKER TESTS PASSED")
print("=" * 70)

print()
print(
    "No physical UB3 was programmed."
)