"""
=========================================================
UB3 Firmware Updater

Step 5.3 - Windows Maple Process Boundary Test

Purpose
-------
Validate the existing Windows process boundary used by
Maple Loader without executing the real Maple uploader
or programming a physical UB3.

A temporary .bat file receives the exact Maple argument
contract:

    COM3 2 1EAF:003 <firmware>

The test verifies:
    • cmd.exe wrapper
    • call semantics
    • argument order
    • stdout streaming
    • stderr streaming
    • exit code propagation

No real maple_upload.bat is executed.
No physical UB3 is programmed.
=========================================================
"""

from pathlib import Path
import os
import tempfile

import bootstrap

from ub3_updater.utils.process_runner import ProcessRunner


print("=" * 70)
print("WINDOWS MAPLE PROCESS BOUNDARY - STEP 5.3")
print("=" * 70)

if os.name != "nt":
    print("[SKIP] Windows process-boundary test requires Windows.")
    raise SystemExit(0)


with tempfile.TemporaryDirectory() as temp_dir:

    temp = Path(temp_dir)

    batch = temp / "fake_maple_upload.bat"

    firmware = (
        temp
        / "UnlockBoxIII_260123_ZNA2US-WWDG2d_1.00."
        "ino.generic_stm32f103r.bin"
    )

    firmware.write_bytes(b"STEP 5.3 TEST FIRMWARE")

    batch.write_text(
        "@echo off\r\n"
        "echo Maple Loader process boundary started\r\n"
        "echo COM=%1\r\n"
        "echo ALT=%2\r\n"
        "echo DFU=%3\r\n"
        "echo FIRMWARE=%4\r\n"
        "echo simulated stderr>&2\r\n"
        "exit /b 0\r\n",
        encoding="utf-8",
    )

    command = [
        "cmd.exe",
        "/d",
        "/c",
        "call",
        str(batch),
        "COM3",
        "2",
        "1EAF:003",
        str(firmware),
    ]

    stdout = []
    stderr = []

    runner = ProcessRunner()

    result = runner.run(
        command,
        cwd=batch.parent,
        timeout=10,
        on_output=stdout.append,
        on_error=stderr.append,
    )

    assert result.started is True
    print("[PASS] Windows process started")

    assert result.return_code == 0
    print("[PASS] Batch exit code propagated")

    assert result.success is True
    print("[PASS] Batch process succeeded")

    assert "Maple Loader process boundary started" in result.stdout
    print("[PASS] Maple process stdout captured")

    assert "Maple Loader process boundary started" in stdout
    print("[PASS] Maple process stdout streamed")

    assert "simulated stderr" in result.stderr
    print("[PASS] Maple process stderr captured")

    assert "simulated stderr" in stderr
    print("[PASS] Maple process stderr streamed")

    assert "COM=COM3" in result.stdout
    print("[PASS] COM3 propagated")

    assert "ALT=2" in result.stdout
    print("[PASS] Maple ALT ID propagated")

    assert "DFU=1EAF:003" in result.stdout
    print("[PASS] Maple DFU ID propagated")

    assert str(firmware) in result.stdout
    print("[PASS] Firmware path propagated")

print("\n" + "=" * 70)
print("ALL STEP 5.3 WINDOWS PROCESS BOUNDARY TESTS PASSED")
print("=" * 70)

print("\nReal maple_upload.bat was not executed.")
print("No physical UB3 was programmed.")
