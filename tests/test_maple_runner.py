import bootstrap

from pathlib import Path

from ub3_updater.utils.process_runner import ProcessRunner


MAPLE_UPLOAD = Path(
    r"C:\Benon\Personal\Set_UP\Arduino\hardware"
    r"\Arduino_STM32\Arduino_STM32-master"
    r"\tools\win\maple_upload.bat"
)


print("=" * 70)
print("MAPLE UPLOADER PROCESS TEST")
print("=" * 70)

print()
print("Uploader:")
print(MAPLE_UPLOAD)

print()
print("Exists:", MAPLE_UPLOAD.exists())

if not MAPLE_UPLOAD.exists():
    raise FileNotFoundError(
        f"maple_upload.bat not found: {MAPLE_UPLOAD}"
    )


runner = ProcessRunner()


def on_output(line):
    print(f"[OUT] {line}")


def on_error(line):
    print(f"[ERR] {line}")


print()
print("Starting maple_upload.bat...")
print("No COM port or firmware arguments are being supplied.")
print()


result = runner.run(
    [
        "cmd.exe",
        "/d",
        "/c",
        "call",
        str(MAPLE_UPLOAD),
    ],
    cwd=MAPLE_UPLOAD.parent,
    timeout=15,
    on_output=on_output,
    on_error=on_error,
)


print()
print("=" * 70)
print("RESULT")
print("=" * 70)

print("Started :", result.started)
print("Success :", result.success)
print("Failed  :", result.failed)
print("Return  :", result.return_code)
print("Timeout :", result.timed_out)
print("Cancel  :", result.cancelled)
print("Error   :", result.error)

print()
print("STDOUT:")
print(result.stdout)

print()
print("STDERR:")
print(result.stderr)

print()
print(
    "Duration:",
    round(result.duration_seconds, 3),
    "seconds",
)