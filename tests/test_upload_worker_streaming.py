"""
======================================================================
UB3 FIRMWARE UPDATER
UPLOAD WORKER - STEP 4.4 STREAMING TEST
======================================================================

Purpose
-------
Verify that UploadWorker correctly propagates:

1. Worker startup
2. Firmware propagation
3. UploadService invocation
4. Worker state changes
5. Textual progress messages
6. UploadService stdout
7. UploadService stderr
8. Completion result
9. Error handling

IMPORTANT
---------
This test does NOT use a physical UB3.

UploadService is replaced by a fake service.
No Maple Loader executable is called.
======================================================================
"""

from __future__ import annotations

import time
from pathlib import Path

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


# =====================================================================
# HEADER
# =====================================================================

print()
print("=" * 70)
print("UPLOAD WORKER - STEP 4.4 STREAMING TEST")
print("=" * 70)


# =====================================================================
# TEST FIRMWARE
# =====================================================================

def create_firmware() -> Firmware:
    """
    Create a test Firmware object.

    The fake service does not require the physical file to exist.
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


firmware = create_firmware()


# =====================================================================
# TEST RESULT
# =====================================================================

def create_success_result() -> UploadResult:
    """
    Create a successful UploadResult using the existing project API.
    """

    return UploadResult.success_result(
        message=(
            "Firmware upload completed successfully."
        ),
        firmware_name="ZNA2US",
        firmware_version="1.00",
        com_port="COM3",
        duration_seconds=1.25,
    )


# =====================================================================
# FAKE UPLOAD SERVICE
# =====================================================================

class FakeUploadService:
    """
    Fake UploadService used by the streaming test.

    No real device is accessed.
    No Maple Loader is executed.

    The current UploadWorker contract calls:

        upload(
            firmware,
            on_output=...,
            on_error=...,
        )
    """

    def __init__(
        self,
        result: UploadResult | None = None,
        exception: Exception | None = None,
        delay: float = 0.05,
    ) -> None:

        self.result = (
            result
            if result is not None
            else create_success_result()
        )

        self.exception = exception

        self.delay = delay

        self.upload_count = 0

        self.last_firmware = None

        self.output_callback = None

        self.error_callback = None

    # -----------------------------------------------------------------
    # Upload
    # -----------------------------------------------------------------

    def upload(
        self,
        firmware,
        on_output=None,
        on_error=None,
        **kwargs,
    ):
        """
        Simulate UploadService.upload().
        """

        self.upload_count += 1

        self.last_firmware = firmware

        self.output_callback = on_output

        self.error_callback = on_error

        # -------------------------------------------------------------
        # Simulate a short-running background operation.
        # -------------------------------------------------------------

        if self.delay:
            time.sleep(
                self.delay
            )

        # -------------------------------------------------------------
        # Simulate an unexpected UploadService exception.
        # -------------------------------------------------------------

        if self.exception is not None:
            raise self.exception

        # -------------------------------------------------------------
        # Simulate Maple Loader stdout.
        # -------------------------------------------------------------

        if on_output is not None:

            on_output(
                "Maple Loader started."
            )

            on_output(
                "Opening COM3..."
            )

            on_output(
                "Downloading firmware..."
            )

            on_output(
                "Firmware transfer completed."
            )

        # -------------------------------------------------------------
        # Simulate Maple Loader stderr.
        #
        # UploadWorker should convert this to:
        #
        #     [ERROR] ...
        #
        # -------------------------------------------------------------

        if on_error is not None:

            on_error(
                "USB reset detected after download."
            )

        return self.result


# =====================================================================
# CALLBACK COLLECTION
# =====================================================================

states = []

progress_messages = []

output_messages = []

completed_results = []

errors = []


# =====================================================================
# CALLBACKS
# =====================================================================

def on_state_changed(
    state: UploadWorkerState,
):
    states.append(
        state
    )


def on_progress(
    message: str,
):
    progress_messages.append(
        str(message)
    )


def on_output(
    message: str,
):
    output_messages.append(
        str(message)
    )


def on_completed(
    result: UploadResult,
):
    completed_results.append(
        result
    )


def on_error(
    error: Exception,
):
    errors.append(
        error
    )


# =====================================================================
# CREATE SERVICE
# =====================================================================

service = FakeUploadService()


# =====================================================================
# CREATE WORKER
# =====================================================================

worker = UploadWorker(
    upload_service=service
)


# =====================================================================
# CONFIGURE CALLBACKS
# =====================================================================

worker.configure_callbacks(
    on_state_changed=on_state_changed,
    on_output=on_output,
    on_progress=on_progress,
    on_completed=on_completed,
    on_error=on_error,
)


# =====================================================================
# TEST 1 - INITIAL STATE
# =====================================================================

print()
print("=" * 70)
print("TEST 1 - INITIAL STATE")
print("=" * 70)


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


# =====================================================================
# TEST 2 - START WORKER
# =====================================================================

print()
print("=" * 70)
print("TEST 2 - START WORKER")
print("=" * 70)


started = worker.start(
    firmware
)


assert started is True, (
    "UploadWorker.start() returned False."
)


print(
    "[PASS] Worker started"
)


# =====================================================================
# TEST 3 - WAIT FOR COMPLETION
# =====================================================================

print()
print("=" * 70)
print("TEST 3 - WAIT FOR COMPLETION")
print("=" * 70)


finished = worker.wait(
    timeout=5.0
)


assert finished is True, (
    "Worker did not finish within 5 seconds."
)


print(
    "[PASS] Worker finished"
)


# =====================================================================
# TEST 4 - UPLOAD SERVICE INVOCATION
# =====================================================================

print()
print("=" * 70)
print("TEST 4 - UPLOAD SERVICE INVOCATION")
print("=" * 70)


assert (
    service.upload_count
    == 1
), (
    "UploadService.upload() was not called "
    "exactly once."
)


print(
    "[PASS] UploadService called exactly once"
)


assert (
    service.last_firmware
    is firmware
), (
    "Firmware object was not propagated correctly."
)


print(
    "[PASS] Firmware propagated correctly"
)


# =====================================================================
# TEST 5 - WORKER LIFECYCLE
# =====================================================================

print()
print("=" * 70)
print("TEST 5 - WORKER LIFECYCLE")
print("=" * 70)


assert (
    UploadWorkerState.STARTING
    in states
), (
    "STARTING state was not emitted."
)


print(
    "[PASS] STARTING state emitted"
)


assert (
    UploadWorkerState.UPLOADING
    in states
), (
    "UPLOADING state was not emitted."
)


print(
    "[PASS] UPLOADING state emitted"
)


assert (
    UploadWorkerState.COMPLETED
    in states
), (
    "COMPLETED state was not emitted."
)


print(
    "[PASS] COMPLETED state emitted"
)


assert (
    worker.state
    == UploadWorkerState.COMPLETED
)


print(
    "[PASS] Final state is COMPLETED"
)


# =====================================================================
# TEST 6 - TEXTUAL PROGRESS
# =====================================================================

print()
print("=" * 70)
print("TEST 6 - TEXTUAL PROGRESS")
print("=" * 70)


print(
    f"Captured progress messages: "
    f"{len(progress_messages)}"
)


for index, message in enumerate(
    progress_messages,
    start=1,
):

    print(
        f"  [{index}] {message}"
    )


assert progress_messages, (
    "No progress messages were emitted."
)


assert any(
    "Preparing firmware upload" in message
    for message in progress_messages
), (
    "Preparation progress message was not emitted."
)


print(
    "[PASS] Preparation progress emitted"
)


assert any(
    "Starting firmware upload" in message
    for message in progress_messages
), (
    "Starting progress message was not emitted."
)


print(
    "[PASS] Upload-start progress emitted"
)


assert any(
    "completed successfully" in message.lower()
    for message in progress_messages
), (
    "Completion progress message was not emitted."
)


print(
    "[PASS] Completion progress emitted"
)


# =====================================================================
# TEST 7 - OUTPUT STREAMING
# =====================================================================

print()
print("=" * 70)
print("TEST 7 - OUTPUT STREAMING")
print("=" * 70)


print(
    f"Captured output messages: "
    f"{len(output_messages)}"
)


for index, message in enumerate(
    output_messages,
    start=1,
):

    print(
        f"  [{index}] {message}"
    )


assert output_messages, (
    "No output messages were received."
)


assert any(
    "Maple Loader started" in message
    for message in output_messages
), (
    "Maple Loader startup output was not propagated."
)


print(
    "[PASS] Maple Loader startup output propagated"
)


assert any(
    "Opening COM3" in message
    for message in output_messages
), (
    "COM port output was not propagated."
)


print(
    "[PASS] COM port output propagated"
)


assert any(
    "Downloading firmware" in message
    for message in output_messages
), (
    "Firmware download output was not propagated."
)


print(
    "[PASS] Firmware download output propagated"
)


assert any(
    "Firmware transfer completed" in message
    for message in output_messages
), (
    "Firmware completion output was not propagated."
)


print(
    "[PASS] Firmware completion output propagated"
)


# =====================================================================
# TEST 8 - STDERR STREAMING
# =====================================================================

print()
print("=" * 70)
print("TEST 8 - STDERR STREAMING")
print("=" * 70)


assert any(
    "[ERROR]" in message
    for message in output_messages
), (
    "UploadWorker did not prefix stderr "
    "with [ERROR]."
)


print(
    "[PASS] stderr converted to [ERROR] output"
)


assert any(
    "USB reset detected" in message
    for message in output_messages
), (
    "stderr message was not propagated."
)


print(
    "[PASS] stderr message propagated"
)


# =====================================================================
# TEST 9 - RESULT
# =====================================================================

print()
print("=" * 70)
print("TEST 9 - UPLOAD RESULT")
print("=" * 70)


assert (
    worker.result
    is not None
), (
    "Worker did not store UploadResult."
)


assert isinstance(
    worker.result,
    UploadResult,
)


print(
    "[PASS] UploadResult returned"
)


assert (
    worker.result.status
    == UploadStatus.SUCCESS
)


print(
    "[PASS] UploadResult status is SUCCESS"
)


assert (
    worker.result.success
    is True
)


print(
    "[PASS] UploadResult success=True"
)


# =====================================================================
# TEST 10 - COMPLETION CALLBACK
# =====================================================================

print()
print("=" * 70)
print("TEST 10 - COMPLETION CALLBACK")
print("=" * 70)


assert (
    len(completed_results)
    == 1
), (
    "Completion callback was not executed "
    "exactly once."
)


print(
    "[PASS] Completion callback executed"
)


assert (
    completed_results[0]
    is worker.result
)


print(
    "[PASS] Completion callback received "
    "worker result"
)


# =====================================================================
# TEST 11 - ERROR CALLBACK
# =====================================================================

print()
print("=" * 70)
print("TEST 11 - ERROR CALLBACK")
print("=" * 70)


assert not errors, (
    f"Unexpected worker errors: {errors}"
)


print(
    "[PASS] No unexpected worker error"
)


# =====================================================================
# TEST 12 - WORKER FIRMWARE
# =====================================================================

print()
print("=" * 70)
print("TEST 12 - WORKER FIRMWARE")
print("=" * 70)


assert (
    worker.firmware
    is firmware
)


print(
    "[PASS] Worker retains selected firmware"
)


# =====================================================================
# TEST 13 - RESET
# =====================================================================

print()
print("=" * 70)
print("TEST 13 - RESET")
print("=" * 70)


reset = worker.reset()


assert reset is True, (
    "Worker reset failed."
)


assert (
    worker.state
    == UploadWorkerState.IDLE
)


assert (
    worker.firmware
    is None
)


assert (
    worker.result
    is None
)


print(
    "[PASS] Worker reset to IDLE"
)


# =====================================================================
# FINAL VALIDATION
# =====================================================================

print()
print("=" * 70)
print("FINAL VALIDATION")
print("=" * 70)


print(
    "[PASS] Worker startup"
)

print(
    "[PASS] UploadService invocation"
)

print(
    "[PASS] Firmware propagation"
)

print(
    "[PASS] Worker lifecycle"
)

print(
    "[PASS] Textual progress streaming"
)

print(
    "[PASS] stdout streaming"
)

print(
    "[PASS] stderr streaming"
)

print(
    "[PASS] UploadResult propagation"
)

print(
    "[PASS] Completion callback"
)

print(
    "[PASS] Worker reset"
)


print()
print("=" * 70)
print(
    "ALL UPLOAD WORKER STEP 4.4 "
    "STREAMING TESTS PASSED"
)
print("=" * 70)

print()
print(
    "No physical UB3 was programmed."
)