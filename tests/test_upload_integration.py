"""
=========================================================
UB3 Firmware Updater

UploadService Integration Test

Purpose
-------
Test the complete UploadService.upload() workflow
without actually flashing a physical UB3.

Flow
----

    Test Firmware
         |
         v
    UploadService.upload()
         |
         v
    Fresh DeviceService.scan()
         |
         v
    Maple Serial validation
         |
         v
    Automatic COM detection
         |
         v
    Firmware preparation
         |
         v
    Maple command generation
         |
         v
    Fake ProcessRunner
         |
         v
    Maple result interpretation
         |
         v
    UploadResult


This test DOES NOT perform a real firmware upload.

The real Maple Loader is not executed.

=========================================================
"""

from pathlib import Path

import bootstrap

from ub3_updater.models.device import (
    Device,
    DeviceState,
)

from ub3_updater.models.firmware import (
    Firmware,
)

from ub3_updater.models.upload_result import (
    UploadStatus,
)

from ub3_updater.services.upload_service import (
    UploadService,
)

from ub3_updater.services.config_service import (
    ConfigService,
)

from ub3_updater.utils.process_runner import (
    ProcessResult,
)


# =========================================================
# Fake DeviceService
# =========================================================

class FakeDeviceService:
    """
    Simulates DeviceService.

    The important part of this fake is that the device is
    returned through scan().

    This allows the test to verify that UploadService
    performs a fresh scan before every upload.
    """

    def __init__(self):

        self.scan_count = 0

        self.device = Device(
            connected=True,
            state=DeviceState.MAPLE_SERIAL,
            com_port="COM3",
            usb_name="Maple Serial (COM3)",
            description="Maple Serial (COM3)",
            manufacturer="LeafLabs, LLC",
            vid="1EAF",
            pid="0004",
            hwid=(
                "USB VID:PID=1EAF:0004 "
                "SER= LOCATION=1-6"
            ),
        )

    def scan(self):

        self.scan_count += 1

        return self.device


# =========================================================
# Fake FirmwareService
# =========================================================

class FakeFirmwareService:
    """
    Simulates successful firmware validation.
    """

    def validate(self, firmware):

        return True, None


# =========================================================
# Fake ProcessRunner
# =========================================================

class FakeProcessRunner:
    """
    Simulates the Maple Loader process.

    The output below is based on the actual successful
    UB3 firmware upload already tested.

    IMPORTANT:
    This class does NOT communicate with the UB3.
    """

    def __init__(self):

        self.run_count = 0

        self.last_command = None

        self.last_cwd = None

        self.last_timeout = None

    def run(
        self,
        command,
        cwd=None,
        timeout=None,
        on_output=None,
        on_error=None,
    ):
        """
        Simulate ProcessRunner.run().
        """

        self.run_count += 1

        self.last_command = command

        self.last_cwd = cwd

        self.last_timeout = timeout

        # -------------------------------------------------
        # Actual Maple Loader output from real test
        # -------------------------------------------------

        stdout = """
maple_loader v0.1
Resetting to bootloader via DTR pulse
Searching for DFU device [1EAF:003]...
Found it!

Opening USB Device 0x1eaf:0x0003...
Found Runtime: [0x1eaf:0x0003] devnum=1, cfg=0, intf=0, alt=2, name="STM32duino bootloader v1.0  Upload to Flash 0x8002000"
Setting Configuration 1...
Claiming USB DFU Interface...
Setting Alternate Setting ...
Determining device status: state = dfuIDLE, status = 0
dfuIDLE, continuing
Transfer Size = 0x0800
bytes_per_hash=6503
Starting download: [##################################################] finished!
state(8) = dfuMANIFEST-WAIT-RESET, status(0) = No error condition is present
Done!
Resetting USB to switch back to runtime mode
error resetting after download: usb_reset: could not reset device, win error: A device which does not exist was specified.
"""

        stderr = """
Reset via USB Serial Failed! Did you select the right serial port?
Assuming the board is in perpetual bootloader mode and continuing...
"""

        # -------------------------------------------------
        # Simulate streaming stdout
        # -------------------------------------------------

        if on_output:

            for line in stdout.splitlines():

                line = line.strip()

                if line:

                    on_output(line)

        # -------------------------------------------------
        # Simulate streaming stderr
        # -------------------------------------------------

        if on_error:

            for line in stderr.splitlines():

                line = line.strip()

                if line:

                    on_error(line)

        # -------------------------------------------------
        # Return ProcessResult
        # -------------------------------------------------

        return ProcessResult(
            command=command,

            return_code=0,

            stdout=stdout,

            stderr=stderr,

            started=True,

            duration_seconds=18.469,
        )


# =========================================================
# Prepare Test Firmware
# =========================================================

print("=" * 70)
print("UPLOAD SERVICE INTEGRATION TEST")
print("=" * 70)


# ---------------------------------------------------------
# Project root
# ---------------------------------------------------------

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


# ---------------------------------------------------------
# Test fixture directory
# ---------------------------------------------------------

TEST_FIXTURE_DIR = (
    PROJECT_ROOT
    / "tests"
    / "fixtures"
)


TEST_FIXTURE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ---------------------------------------------------------
# Source test firmware
# ---------------------------------------------------------

SOURCE_FIRMWARE = (
    TEST_FIXTURE_DIR
    / (
        "UnlockBoxIII_260123_"
        "ZNA2US-WWDG2d_1.00"
        ".ino.generic_stm32f103r.bin"
    )
)


# ---------------------------------------------------------
# Create dummy firmware if necessary
# ---------------------------------------------------------

if not SOURCE_FIRMWARE.exists():

    SOURCE_FIRMWARE.write_bytes(
        b"UB3 TEST FIRMWARE"
    )


print()
print("Test firmware:")
print(SOURCE_FIRMWARE)

print(
    "Exists       :",
    SOURCE_FIRMWARE.exists(),
)


# =========================================================
# Firmware Model
# =========================================================

firmware = Firmware(
    name="ZNA2US",
    version="1.00",
    path=str(SOURCE_FIRMWARE),
)


# =========================================================
# Create Test Services
# =========================================================

device_service = (
    FakeDeviceService()
)

firmware_service = (
    FakeFirmwareService()
)

process_runner = (
    FakeProcessRunner()
)


# =========================================================
# Bundled Maple Uploader
# =========================================================

# The integration test must use the same Maple runtime that
# the production application uses. It must not depend on an
# Arduino installation outside the project tree.

BUNDLED_UPLOADER = (
    ConfigService.maple_uploader()
    .resolve()
)


print()
print("Bundled Maple uploader:")
print(BUNDLED_UPLOADER)

print(
    "Exists       :",
    BUNDLED_UPLOADER.exists(),
)

assert BUNDLED_UPLOADER.exists(), (
    "Bundled Maple uploader is missing: "
    f"{BUNDLED_UPLOADER}"
)


# =========================================================
# Create UploadService
# =========================================================

service = UploadService(
    device_service=device_service,

    firmware_service=firmware_service,

    process_runner=process_runner,

    uploader_path=BUNDLED_UPLOADER,
)


# =========================================================
# Execute UploadService.upload()
# =========================================================

print()
print("=" * 70)
print("STARTING COMPLETE UPLOAD WORKFLOW")
print("=" * 70)

print()

result = service.upload(
    firmware
)


# =========================================================
# Display Upload Result
# =========================================================

print()
print("=" * 70)
print("UPLOAD RESULT")
print("=" * 70)

print()

print(
    "Status       :",
    result.status,
)

print(
    "Success      :",
    result.success,
)

print(
    "Failed       :",
    result.failed,
)

print(
    "Has Warning  :",
    result.has_warning,
)

print(
    "Message      :",
    result.message,
)

print(
    "Warning      :",
    result.warning,
)

print(
    "Error        :",
    result.error,
)

print(
    "COM Port     :",
    result.com_port,
)

print(
    "Firmware     :",
    result.firmware_name,
)

print(
    "Version      :",
    result.firmware_version,
)

print(
    "Return Code  :",
    result.return_code,
)

print(
    "Duration     :",
    result.duration_seconds,
)

print(
    "Device State :",
    result.device_state,
)


# =========================================================
# Display Generated Command
# =========================================================

print()
print("=" * 70)
print("GENERATED COMMAND")
print("=" * 70)

print()

if result.command:

    for index, argument in enumerate(
        result.command
    ):

        print(
            f"[{index}] {argument}"
        )

else:

    print(
        "No command generated."
    )


# =========================================================
# Validation
# =========================================================

print()
print("=" * 70)
print("VALIDATION")
print("=" * 70)


# =========================================================
# 1. Fresh Device Scan
# =========================================================

assert (
    device_service.scan_count >= 2
), (
    "UploadService did not perform both the initial "
    "device scan and the post-upload Maple Serial "
    "re-enumeration scan."
)

print(
    "[PASS] Fresh pre-upload scan and post-upload "
    "re-enumeration scan performed"
)


# =========================================================
# 2. Device Connected
# =========================================================

assert (
    result.device_state
    == DeviceState.MAPLE_SERIAL.value
), (
    "Unexpected device state: "
    f"{result.device_state}"
)

print(
    "[PASS] Device detected in Maple Serial mode"
)


# =========================================================
# 3. Automatic COM Detection
# =========================================================

assert (
    result.com_port == "COM3"
), (
    "Incorrect COM port: "
    f"{result.com_port}"
)

print(
    "[PASS] COM port automatically detected"
)


# =========================================================
# 4. ProcessRunner Executed
# =========================================================

assert (
    process_runner.run_count == 1
), (
    "ProcessRunner was not executed exactly once."
)

print(
    "[PASS] ProcessRunner executed"
)


# =========================================================
# 5. ProcessRunner Configuration
# =========================================================

assert (
    process_runner.last_timeout
    == service.timeout
), (
    "Incorrect ProcessRunner timeout."
)

print(
    "[PASS] Upload timeout passed correctly"
)


# =========================================================
# 6. Command Exists
# =========================================================

command = (
    process_runner.last_command
)

assert command is not None, (
    "No command was passed to ProcessRunner."
)

print(
    "[PASS] Upload command generated"
)


# =========================================================
# 7. Windows Command
# =========================================================

assert (
    command[0]
    == "cmd.exe"
), (
    "Incorrect command executable."
)

assert (
    command[1]
    == "/d"
), (
    "Missing /d argument."
)

assert (
    command[2]
    == "/c"
), (
    "Missing /c argument."
)

assert (
    command[3]
    == "call"
), (
    "Missing call argument."
)

print(
    "[PASS] Windows command structure correct"
)


# =========================================================
# 8. Maple Uploader
# =========================================================

assert (
    command[4]
    == str(BUNDLED_UPLOADER)
), (
    "Incorrect bundled Maple uploader path."
)

print(
    "[PASS] Bundled Maple uploader path correct"
)


# =========================================================
# 9. Automatic COM Port
# =========================================================

assert (
    command[5]
    == "COM3"
), (
    "COM port was not propagated "
    "from detected Device."
)

print(
    "[PASS] Detected COM port passed to Maple Loader"
)


# =========================================================
# 10. ALT ID
# =========================================================

assert (
    command[6]
    == "2"
), (
    "Incorrect Maple ALT ID."
)

print(
    "[PASS] Maple ALT ID correct"
)


# =========================================================
# 11. DFU ID
# =========================================================

assert (
    command[7]
    == "1EAF:003"
), (
    "Incorrect Maple DFU ID."
)

print(
    "[PASS] Maple DFU ID correct"
)


# =========================================================
# 12. Firmware Argument
# =========================================================

upload_firmware = Path(
    command[8]
).resolve()


assert (
    upload_firmware
    == SOURCE_FIRMWARE.resolve()
), (
    "Firmware command argument does not match the "
    "selected firmware source path."
)

print(
    "[PASS] Selected firmware path passed directly to Maple Loader"
)


# =========================================================
# 13. Firmware Exists
# =========================================================

assert (
    upload_firmware.exists()
), (
    "Prepared firmware file does not exist."
)

print(
    "[PASS] Prepared firmware exists"
)


# =========================================================
# 14. Firmware Information
# =========================================================

assert (
    result.firmware_name
    == "ZNA2US"
)

assert (
    result.firmware_version
    == "1.00"
)

print(
    "[PASS] Firmware information propagated"
)


# =========================================================
# 15. Maple Result
# =========================================================

assert (
    result.status
    == UploadStatus.SUCCESS
), (
    "Expected SUCCESS after confirmed Maple Serial "
    f"re-enumeration, got {result.status}"
)

print(
    "[PASS] Maple result and post-upload re-enumeration "
    "interpreted correctly"
)


# =========================================================
# 16. Overall Success
# =========================================================

assert (
    result.success
    is True
), (
    "Upload should be considered successful."
)

assert (
    result.failed
    is False
), (
    "Successful upload must not be marked failed."
)

print(
    "[PASS] Upload considered successful"
)


# =========================================================
# 17. Warning Captured
# =========================================================

assert (
    result.has_warning
    is False
), (
    "No warning should remain when the UB3 returns "
    "to Maple Serial mode."
)

print(
    "[PASS] Post-upload Maple Serial recovery confirmed"
)


# =========================================================
# 18. Return Code
# =========================================================

assert (
    result.return_code
    == 0
), (
    "Expected Maple Loader return code 0."
)

print(
    "[PASS] Process return code correct"
)


# =========================================================
# 19. Standard Output
# =========================================================

assert (
    "Done!"
    in result.stdout
), (
    "Maple Loader success output was not captured."
)

print(
    "[PASS] Maple stdout captured"
)


# =========================================================
# 20. Standard Error
# =========================================================

assert (
    "Reset via USB Serial Failed!"
    in result.stderr
), (
    "Expected Maple reset warning was not captured."
)

print(
    "[PASS] Maple stderr captured"
)


# =========================================================
# Final
# =========================================================

print()
print("=" * 70)
print("ALL TESTS PASSED")
print("=" * 70)

print()
print(
    "UploadService integration is working correctly."
)

print()
print(
    "No physical UB3 was programmed by this test."
)