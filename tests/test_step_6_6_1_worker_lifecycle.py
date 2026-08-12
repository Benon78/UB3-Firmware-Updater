"""
STEP 6.6.1 - UPLOAD WORKER REUSABILITY

Regression for the physical GUI finding:
- first update succeeds;
- UploadWorker remains terminal;
- second update fails until application restart.

No physical UB3 is programmed.
"""

from __future__ import annotations

import os
import sys
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import bootstrap  # noqa: F401

from PySide6.QtWidgets import QApplication

from ub3_updater.models.firmware import Firmware
from ub3_updater.models.upload_result import UploadResult
from ub3_updater.workers.upload_worker import UploadWorker, UploadWorkerState


class FakeUploadService:
    def __init__(self):
        self.calls = []

    def upload(self, firmware, *, on_output=None, on_error=None, **kwargs):
        self.calls.append(firmware)
        if on_output:
            on_output(f"Uploading {firmware.name}...")
        time.sleep(0.05)
        return UploadResult.success_result(
            message="Firmware upload completed successfully.",
            firmware_name=firmware.name,
            firmware_version=firmware.version,
            com_port="COM3",
            duration_seconds=0.05,
        )


def firmware(name):
    return Firmware(
        name=name,
        version="1.00",
        path=fr"C:\project\resources\firmware\{name}\firmware.bin",
    )


app = QApplication.instance() or QApplication(sys.argv)
service = FakeUploadService()
worker = UploadWorker(upload_service=service)

f1 = firmware("ZNA2US")
f2 = firmware("ZMJ")

print()
print("# STEP 6.6.1 - UPLOAD WORKER LIFECYCLE")

assert worker.state == UploadWorkerState.IDLE
print("[PASS] Worker starts in IDLE")

assert worker.start(f1) is True
assert worker.wait(timeout=5) is True
assert worker.state == UploadWorkerState.COMPLETED
assert len(service.calls) == 1
print("[PASS] First firmware upload completes")

assert worker.start(f2) is False
print("[PASS] Terminal worker rejects direct duplicate start")

assert worker.reset() is True
assert worker.state == UploadWorkerState.IDLE
assert worker.result is None
assert worker.firmware is None
print("[PASS] Existing reset API returns worker to IDLE")

assert worker.start(f2) is True
assert worker.wait(timeout=5) is True
assert worker.state == UploadWorkerState.COMPLETED
assert len(service.calls) == 2
assert service.calls[0] is f1
assert service.calls[1] is f2
print("[PASS] Worker can execute a second update with different firmware")

# Verify the existing HomePage upload-completion path contains the
# lifecycle reset. The upload/result UI is owned by HomePage in the
# current architecture; do not move this responsibility into MainWindow.
from pathlib import Path

source = Path("src/ub3_updater/ui/pages/home_page.py").read_text(encoding="utf-8")
assert "_schedule_worker_reset" in source
assert "_reset_worker_when_finished" in source
assert "QTimer.singleShot" in source
assert "controller.reset_worker" in source
print("[PASS] GUI completion path schedules safe worker reset")

print()
print("# ALL STEP 6.6.1 WORKER LIFECYCLE TESTS PASSED")
print("No physical UB3 was programmed.")
