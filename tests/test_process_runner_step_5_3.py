"""
=========================================================
UB3 Firmware Updater

Step 5.3 - ProcessRunner Integration Test

Purpose
-------
Validate the existing ProcessRunner execution boundary
without connecting to or programming a physical UB3.

Tests:
    1. Process startup
    2. stdout streaming
    3. stderr streaming
    4. return-code propagation
    5. working-directory propagation
    6. timeout handling
    7. cancellation
    8. process cleanup
    9. concurrent-run protection

No Maple Loader is executed.
No physical UB3 is programmed.
=========================================================
"""

from pathlib import Path
import os
import sys
import tempfile
import threading
import time

import bootstrap

from ub3_updater.utils.process_runner import (
    ProcessRunner,
)


print("=" * 70)
print("PROCESS RUNNER - STEP 5.3 EXECUTION TEST")
print("=" * 70)


def python_command(*args):
    return [
        sys.executable,
        "-u",
        "-c",
        *args,
    ]


# =========================================================
# TEST 1 - START + STDOUT
# =========================================================

print("\n" + "=" * 70)
print("TEST 1 - PROCESS START AND STDOUT")
print("=" * 70)

runner = ProcessRunner()
stdout_messages = []
stderr_messages = []

result = runner.run(
    python_command(
        "print('UB3 PROCESS STARTED', flush=True); "
        "print('MAPLE COMMAND EXECUTION READY', flush=True)"
    ),
    on_output=stdout_messages.append,
    on_error=stderr_messages.append,
)

assert result.started is True
print("[PASS] Process started")

assert result.return_code == 0
print("[PASS] Return code propagated")

assert "UB3 PROCESS STARTED" in result.stdout
print("[PASS] stdout captured")

assert "UB3 PROCESS STARTED" in stdout_messages
print("[PASS] stdout streamed")

assert result.success is True
print("[PASS] Process success interpreted correctly")


# =========================================================
# TEST 2 - STDERR
# =========================================================

print("\n" + "=" * 70)
print("TEST 2 - STDERR STREAMING")
print("=" * 70)

runner = ProcessRunner()
stderr_messages = []

result = runner.run(
    python_command(
        "import sys; "
        "print('normal output', flush=True); "
        "print('simulated Maple warning', file=sys.stderr, flush=True)"
    ),
    on_error=stderr_messages.append,
)

assert result.return_code == 0
print("[PASS] Process completed")

assert "simulated Maple warning" in result.stderr
print("[PASS] stderr captured")

assert "simulated Maple warning" in stderr_messages
print("[PASS] stderr streamed")


# =========================================================
# TEST 3 - WORKING DIRECTORY
# =========================================================

print("\n" + "=" * 70)
print("TEST 3 - WORKING DIRECTORY")
print("=" * 70)

runner = ProcessRunner()

with tempfile.TemporaryDirectory() as temp_dir:

    expected = str(
        Path(temp_dir).resolve()
    )

    result = runner.run(
        python_command(
            "import os; "
            "print(os.getcwd(), flush=True)"
        ),
        cwd=temp_dir,
    )

    assert result.success is True
    print("[PASS] Process completed in requested directory")

    assert expected.lower() in result.stdout.strip().lower()
    print("[PASS] Working directory propagated")


# =========================================================
# TEST 4 - TIMEOUT
# =========================================================

print("\n" + "=" * 70)
print("TEST 4 - TIMEOUT")
print("=" * 70)

runner = ProcessRunner()

started = time.monotonic()

result = runner.run(
    python_command(
        "import time; "
        "print('long process started', flush=True); "
        "time.sleep(10)"
    ),
    timeout=0.5,
)

elapsed = time.monotonic() - started

assert result.started is True
print("[PASS] Timed process started")

assert result.timed_out is True
print("[PASS] Timeout detected")

assert result.success is False
print("[PASS] Timed-out process is not successful")

assert elapsed < 5
print("[PASS] Timeout terminates process promptly")


# =========================================================
# TEST 5 - CANCELLATION
# =========================================================

print("\n" + "=" * 70)
print("TEST 5 - CANCELLATION")
print("=" * 70)

runner = ProcessRunner()
holder = {}

def run_long_process():
    holder["result"] = runner.run(
        python_command(
            "import time; "
            "print('cancellation test started', flush=True); "
            "time.sleep(10)"
        ),
        timeout=30,
    )

thread = threading.Thread(
    target=run_long_process,
    daemon=True,
)

thread.start()

deadline = time.time() + 3

while (
    not runner.is_running
    and time.time() < deadline
):
    time.sleep(0.02)

assert runner.is_running is True
print("[PASS] Long-running process detected")

cancelled = runner.cancel()

assert cancelled is True
print("[PASS] Cancellation request accepted")

thread.join(timeout=5)

assert not thread.is_alive()
print("[PASS] Process runner thread finished")

cancel_result = holder["result"]

assert cancel_result.cancelled is True
print("[PASS] Cancellation propagated to ProcessResult")

assert cancel_result.success is False
print("[PASS] Cancelled process is not successful")


# =========================================================
# TEST 6 - CANCEL WHEN IDLE
# =========================================================

print("\n" + "=" * 70)
print("TEST 6 - IDLE CANCELLATION")
print("=" * 70)

runner = ProcessRunner()

assert runner.cancel() is False
print("[PASS] Idle cancellation rejected safely")


# =========================================================
# TEST 7 - CONCURRENT EXECUTION PROTECTION
# =========================================================

print("\n" + "=" * 70)
print("TEST 7 - CONCURRENT PROCESS PROTECTION")
print("=" * 70)

runner = ProcessRunner()
holder = {}

def run_first():
    holder["first"] = runner.run(
        python_command(
            "import time; time.sleep(1)"
        ),
        timeout=5,
    )

thread = threading.Thread(
    target=run_first,
    daemon=True,
)

thread.start()

deadline = time.time() + 3

while (
    not runner.is_running
    and time.time() < deadline
):
    time.sleep(0.02)

assert runner.is_running is True
print("[PASS] First process running")

second = runner.run(
    python_command(
        "print('second process')"
    )
)

assert second.started is False
print("[PASS] Second process rejected while runner busy")

assert "already running" in second.error.lower()
print("[PASS] Concurrent-run error reported")

runner.cancel()
thread.join(timeout=5)

assert not thread.is_alive()
print("[PASS] First process cleaned up")


# =========================================================
# TEST 8 - CLEANUP
# =========================================================

print("\n" + "=" * 70)
print("TEST 8 - CLEANUP")
print("=" * 70)

runner = ProcessRunner()

holder = {}

def run_cleanup_process():
    holder["result"] = runner.run(
        python_command(
            "import time; time.sleep(10)"
        ),
        timeout=30,
    )

thread = threading.Thread(
    target=run_cleanup_process,
    daemon=True,
)

thread.start()

deadline = time.time() + 3

while (
    not runner.is_running
    and time.time() < deadline
):
    time.sleep(0.02)

assert runner.is_running is True
print("[PASS] Cleanup test process running")

runner.cleanup()

thread.join(timeout=5)

assert not thread.is_alive()
print("[PASS] cleanup() terminated active process")

assert runner.is_running is False
print("[PASS] Runner returned to idle state")


# =========================================================
# FINAL VALIDATION
# =========================================================

print("\n" + "=" * 70)
print("FINAL VALIDATION")
print("=" * 70)

print("[PASS] Process startup")
print("[PASS] stdout streaming")
print("[PASS] stderr streaming")
print("[PASS] return-code handling")
print("[PASS] working-directory handling")
print("[PASS] timeout handling")
print("[PASS] cancellation")
print("[PASS] concurrent-run protection")
print("[PASS] process cleanup")

print("\n" + "=" * 70)
print("ALL STEP 5.3 PROCESS RUNNER TESTS PASSED")
print("=" * 70)

print("\nNo Maple Loader executed.")
print("No physical UB3 was programmed.")
