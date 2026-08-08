from pathlib import Path

import bootstrap

from ub3_updater.services.upload_service import UploadService
from ub3_updater.utils.process_runner import ProcessRunner


UPLOADER = Path(
    r"C:\Benon\Personal\Set_UP\Arduino\hardware"
    r"\Arduino_STM32\Arduino_STM32-master"
    r"\tools\win\maple_upload.bat"
)


print("=" * 70)
print("MAPLE PROCESS TEST")
print("=" * 70)

service = UploadService(
    uploader_path=UPLOADER
)

runner = ProcessRunner()

# ---------------------------------------------------------
# Use the actual COM port.
# ---------------------------------------------------------

command = [
    "cmd.exe",
    "/d",
    "/c",
    "call",
    str(UPLOADER),
    "COM3",
    "2",
    "1EAF:003",
    r"C:\tmp\UnlockBoxIII_260123_ZNA2US-WWDG2d_1.00.ino.generic_stm32f103r.bin",
]

print()
print("Command:")
for index, argument in enumerate(command):
    print(f"[{index}] {argument}")

print()
print("Working directory:")
print(UPLOADER.parent)

print()
print("=" * 70)
print("STARTING MAPLE UPLOADER")
print("=" * 70)

print()
print("This will communicate with the UB3.")
print("UB3 should currently be:")
print("    Maple Serial (COM3)")
print()
print("Do NOT manually switch to USB Serial Device.")
print()

input(
    "Press ENTER to start, or Ctrl+C to cancel..."
)


def output(line: str):
    print(f"[OUT] {line}")


def error(line: str):
    print(f"[ERR] {line}")


result = runner.run(
    command,
    cwd=UPLOADER.parent,
    timeout=120,
    on_output=output,
    on_error=error,
)


print()
print("=" * 70)
print("PROCESS RESULT")
print("=" * 70)

print()
print("Started :", result.started)
print("Success :", result.success)
print("Failed  :", result.failed)
print("Return  :", result.return_code)
print("Timeout :", result.timed_out)
print("Cancel  :", result.cancelled)
print("Error   :", result.error)
print("Duration:", round(result.duration_seconds, 3), "seconds")

print()
print("STDOUT:")
print(result.stdout)

print()
print("STDERR:")
print(result.stderr)