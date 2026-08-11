"""
======================================================================
UB3 Firmware Updater
Step 5.4 - Controlled Physical Validation Tool
======================================================================

Purpose
-------
Provide a controlled operator workflow for validating the complete
UB3 firmware update path before and during the first physical-device
programming test.

Architecture
------------
This tool intentionally reuses the existing project architecture:

    ConfigService
        |
        +--> FirmwareService
        |
        +--> DeviceService
        |
        +--> UploadService
                    |
                    +--> ProcessRunner
                    |
                    +--> bundled maple_upload.bat

Safety
------
SAFE MODE is the default.

No physical UB3 is programmed unless BOTH are supplied:

    --program
    --confirm PROGRAM-UB3

The tool never creates its own subprocess/upload/device-detection
architecture.

No C:\\tmp firmware staging is used.

No physical UB3 is programmed by safe mode.
======================================================================
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


# ======================================================================
# PROJECT BOOTSTRAP
# ======================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


# ======================================================================
# PROJECT IMPORTS
# ======================================================================

from ub3_updater.services.config_service import ConfigService

from ub3_updater.services.firmware_service import (
    FirmwareService,
)

from ub3_updater.services.device_service import (
    DeviceService,
)

from ub3_updater.services.upload_service import (
    UploadService,
)
from ub3_updater.services.maple_resource_service import MapleResourceService


# ======================================================================
# CONSTANTS
# ======================================================================

PROGRAM_CONFIRMATION_TOKEN = "PROGRAM-UB3"

EXPECTED_MAPLE_ALT_ID = "2"

EXPECTED_MAPLE_DFU_ID = "1EAF:003"

EXPECTED_FIRMWARE_NAME = "ZNA2US"


# ======================================================================
# OUTPUT HELPERS
# ======================================================================

def print_header(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def print_pass(message: str) -> None:
    print(f"[PASS] {message}")


def print_fail(message: str) -> None:
    print(f"[FAIL] {message}")


def print_warn(message: str) -> None:
    print(f"[WARN] {message}")


def print_info(message: str) -> None:
    print(f"[INFO] {message}")


# ======================================================================
# PROJECT RESOURCE VALIDATION
# ======================================================================

def validate_project_resources() -> bool:
    """
    Validate the resources required for physical programming.
    """

    print_header("PROJECT RESOURCES")

    try:
        firmware_root = Path(
            ConfigService.firmware_root()
        ).resolve()
    except Exception as exc:
        print_fail(
            f"Unable to resolve firmware root: {exc}"
        )
        return False

    try:
        maple_uploader = Path(
            ConfigService.maple_uploader()
        ).resolve()
    except Exception as exc:
        print_fail(
            f"Unable to resolve Maple uploader: {exc}"
        )
        return False

    print(
        f"Firmware root : {firmware_root}"
    )

    print(
        f"Maple uploader: {maple_uploader}"
    )

    resource_service = MapleResourceService(
        resource_root=maple_uploader.parent
    )

    runtime_validation = resource_service.validate()

    if not runtime_validation.valid:
        details = ""
        if runtime_validation.missing_files:
            details = (
                " Missing: "
                + ", ".join(runtime_validation.missing_files)
            )
        print_fail(
            "Bundled Maple runtime is incomplete."
            + details
        )
        return False

    print_pass("Bundled Maple runtime available")

    java = resource_service.resolve_java()

    if java is None:
        print_fail(
            "Java runtime not found. maple_loader.jar requires "
            "Java 7 or newer. Install Java or add a bundled JRE "
            "under resources/tools/maple/java/."
        )
        return False

    print_pass(f"Java runtime available: {java}")

    # --------------------------------------------------------------
    # Firmware repository
    # --------------------------------------------------------------

    if not firmware_root.exists():

        print_fail(
            "Firmware repository does not exist."
        )

        return False

    if not firmware_root.is_dir():

        print_fail(
            "Firmware repository is not a directory."
        )

        return False

    print_pass(
        "Firmware repository available"
    )

    # --------------------------------------------------------------
    # Maple uploader
    # --------------------------------------------------------------

    if not maple_uploader.exists():

        print_fail(
            "Bundled Maple uploader does not exist."
        )

        return False

    if not maple_uploader.is_file():

        print_fail(
            "Configured Maple uploader is not a file."
        )

        return False

    if (
        maple_uploader.name.lower()
        != "maple_upload.bat"
    ):

        print_warn(
            "Configured uploader is not named "
            "maple_upload.bat."
        )

    # --------------------------------------------------------------
    # Ensure bundled resources are used
    # --------------------------------------------------------------

    try:
        maple_uploader.relative_to(
            PROJECT_ROOT
        )
    except ValueError:

        print_fail(
            "Maple uploader is outside the project "
            "resources directory."
        )

        return False

    if (
        "resources" not in
        {
            part.lower()
            for part in maple_uploader.parts
        }
    ):

        print_fail(
            "Maple uploader is not under project "
            "resources."
        )

        return False

    print_pass(
        "Bundled Maple uploader available"
    )

    return True


# ======================================================================
# FIRMWARE DISCOVERY
# ======================================================================

def load_selected_firmware():
    """
    Load firmware using the existing FirmwareService API.

    Current FirmwareService contract:

        get_all()
        get_default()
        find()
        validate()

    No alternative firmware repository API is created here.
    """

    print_header("FIRMWARE PRE-FLIGHT")

    firmware_service = FirmwareService()

    # --------------------------------------------------------------
    # Discover firmware
    # --------------------------------------------------------------

    firmwares = firmware_service.get_all()

    if not firmwares:

        print_fail(
            "No valid firmware packages found."
        )

        errors = firmware_service.get_errors()

        for error in errors:

            print(
                f"  - {error}"
            )

        return None

    print_pass(
        f"Firmware packages detected: "
        f"{len(firmwares)}"
    )

    # --------------------------------------------------------------
    # Display packages
    # --------------------------------------------------------------

    print()

    print("Available firmware:")

    for firmware in firmwares:

        print(
            f"  - {firmware.display_name}"
        )

        print(
            f"    File: {firmware.filename}"
        )

    # --------------------------------------------------------------
    # Default firmware
    # --------------------------------------------------------------

    firmware = firmware_service.get_default()

    if firmware is None:

        print_fail(
            "No default firmware is available."
        )

        return None

    print()

    print(
        f"Selected firmware: "
        f"{firmware.display_name}"
    )

    # --------------------------------------------------------------
    # Confirm expected firmware
    # --------------------------------------------------------------

    if (
        firmware.name.upper()
        != EXPECTED_FIRMWARE_NAME.upper()
    ):

        print_warn(
            "Default firmware is not "
            f"{EXPECTED_FIRMWARE_NAME}."
        )

        print_warn(
            "The actual FirmwareService default "
            "will be used."
        )

    # --------------------------------------------------------------
    # Validate selected firmware
    # --------------------------------------------------------------

    valid, error = (
        firmware_service.validate(
            firmware
        )
    )

    if not valid:

        print_fail(
            "Firmware validation failed."
        )

        print(
            f"  Reason: {error}"
        )

        return None

    print_pass(
        "Selected firmware file validated"
    )

    # --------------------------------------------------------------
    # Verify path
    # --------------------------------------------------------------

    firmware_path = Path(
        firmware.path
    ).resolve()

    print()

    print(
        f"Firmware name : {firmware.name}"
    )

    print(
        f"Firmware ver. : {firmware.version}"
    )

    print(
        f"Firmware file : {firmware.filename}"
    )

    print(
        f"Firmware path : {firmware_path}"
    )

    # --------------------------------------------------------------
    # Firmware must belong to resources/firmware
    # --------------------------------------------------------------

    try:

        firmware_path.relative_to(
            Path(
                ConfigService.firmware_root()
            ).resolve()
        )

    except ValueError:

        print_fail(
            "Selected firmware is outside "
            "resources/firmware."
        )

        return None

    print_pass(
        "Firmware belongs to project "
        "resources/firmware"
    )

    return firmware


# ======================================================================
# DEVICE PRE-FLIGHT
# ======================================================================

def scan_device():
    """
    Perform a fresh device scan through the existing DeviceService.
    """

    print_header("DEVICE PRE-FLIGHT")

    try:

        device_service = DeviceService()

    except Exception as exc:

        print_fail(
            f"Unable to initialize DeviceService: {exc}"
        )

        return None

    # --------------------------------------------------------------
    # Fresh scan
    # --------------------------------------------------------------

    try:

        devices = device_service.scan()

    except Exception as exc:

        print_fail(
            f"Device scan failed: {exc}"
        )

        return None

    # DeviceService.scan() returns the current Device object,
    # not a list of devices. This is the established project API.
    device = devices

    if device is None or not device.connected:

        print_fail(
            "No UB3 device detected."
        )

        print()
        print(
            "Connect the UB3 and ensure it appears "
            "as a Maple Serial device."
        )

        return None

    print_pass(
        "Fresh device scan completed"
    )

    print()

    print(
        f"Device      : "
        f"{getattr(device, 'name', 'Unavailable')}"
    )

    print(
        f"COM port    : "
        f"{getattr(device, 'com_port', 'Unavailable')}"
    )

    print(
        f"VID:PID     : "
        f"{getattr(device, 'vid_pid', 'Unavailable')}"
    )

    print(
        f"Manufacturer: "
        f"{getattr(device, 'manufacturer', 'Unavailable')}"
    )

    # --------------------------------------------------------------
    # Connection check
    # --------------------------------------------------------------

    connected = getattr(
        device,
        "connected",
        None,
    )

    if connected is False:

        print_fail(
            "Detected device is not connected."
        )

        return None

    print_pass(
        "UB3 device detected"
    )

    # --------------------------------------------------------------
    # Maple Serial
    # --------------------------------------------------------------

    if device.is_maple is not True:

        print_fail(
            "Device is not in Maple Serial mode."
        )

        return None

    print_pass(
        "Maple Serial mode detected"
    )

    # --------------------------------------------------------------
    # COM port
    # --------------------------------------------------------------

    com_port = getattr(
        device,
        "com_port",
        None,
    )

    if not com_port:

        print_fail(
            "COM port was not detected."
        )

        return None

    print_pass(
        f"COM port automatically detected: "
        f"{com_port}"
    )

    return device


# ======================================================================
# UPLOAD SERVICE / COMMAND PREVIEW
# ======================================================================

def build_command_preview(
    device,
    firmware,
):
    """
    Use the existing UploadService command-building architecture.

    This function does not execute Maple Loader.
    """

    print_header("MAPLE COMMAND PREVIEW")

    try:

        upload_service = UploadService()

    except Exception as exc:

        print_fail(
            f"Unable to initialize UploadService: {exc}"
        )

        return None

    # --------------------------------------------------------------
    # Verify uploader
    # --------------------------------------------------------------

    uploader = getattr(
        upload_service,
        "uploader_path",
        None,
    )

    if uploader is None:

        uploader = getattr(
            upload_service,
            "maple_uploader",
            None,
        )

    if uploader is not None:

        print(
            f"Uploader: {uploader}"
        )

    # --------------------------------------------------------------
    # Obtain COM port
    # --------------------------------------------------------------

    com_port = getattr(
        device,
        "com_port",
        None,
    )

    if not com_port:

        print_fail(
            "Device does not provide a COM port."
        )

        return None

    # --------------------------------------------------------------
    # Firmware path
    # --------------------------------------------------------------

    firmware_path = Path(
        firmware.path
    ).resolve()

    if not firmware_path.exists():

        print_fail(
            "Selected firmware file does not exist."
        )

        return None

    # --------------------------------------------------------------
    # Try the existing UploadService command API
    # --------------------------------------------------------------

    # Use the established UploadService command builder.
    # Do not duplicate Maple command construction here.
    command = upload_service.build_command(
        device=device,
        firmware=firmware,
    )

    # --------------------------------------------------------------
    # Normalize command
    # --------------------------------------------------------------

    if isinstance(command, tuple):

        command = list(command)

    elif isinstance(command, str):

        command = [
            command
        ]

    else:

        command = list(command)

    print()

    print(
        "Resolved command:"
    )

    for index, argument in enumerate(
        command
    ):

        print(
            f"  [{index}] {argument}"
        )

    # --------------------------------------------------------------
    # Contract validation
    # --------------------------------------------------------------

    command_text = " ".join(
        str(argument)
        for argument in command
    )

    if str(com_port) not in command_text:

        print_fail(
            "Detected COM port was not propagated "
            "into the command."
        )

        return None

    print_pass(
        "Detected COM port propagated"
    )

    if EXPECTED_MAPLE_ALT_ID not in command:

        print_fail(
            "Maple ALT ID is missing."
        )

        return None

    print_pass(
        f"Maple ALT ID = "
        f"{EXPECTED_MAPLE_ALT_ID}"
    )

    if EXPECTED_MAPLE_DFU_ID not in command:

        print_fail(
            "Maple DFU ID is missing."
        )

        return None

    print_pass(
        f"Maple DFU ID = "
        f"{EXPECTED_MAPLE_DFU_ID}"
    )

    if str(firmware_path) not in command:

        print_fail(
            "Selected firmware path was not "
            "propagated into the command."
        )

        return None

    print_pass(
        "Selected firmware path propagated"
    )

    # --------------------------------------------------------------
    # Firmware must be final argument
    # --------------------------------------------------------------

    if (
        str(command[-1])
        != str(firmware_path)
    ):

        print_fail(
            "Firmware path is not the final "
            "Maple argument."
        )

        return None

    print_pass(
        "Firmware path is final Maple argument"
    )

    # --------------------------------------------------------------
    # No development C:\tmp staging
    # --------------------------------------------------------------

    command_lower = command_text.lower()

    if (
        "c:\\tmp" in command_lower
        or "c:/tmp" in command_lower
    ):

        print_fail(
            "C:\\tmp firmware staging detected."
        )

        return None

    print_pass(
        "No C:\\tmp firmware staging used"
    )

    return {
        "upload_service": upload_service,
        "command": command,
        "com_port": com_port,
        "firmware_path": firmware_path,
    }


# ======================================================================
# SAFE PRE-FLIGHT
# ======================================================================

def run_safe_preflight():
    """
    Run the complete software/device pre-flight.

    Never programs the UB3.
    """

    print_header(
        "STEP 5.4 - CONTROLLED PHYSICAL VALIDATION"
    )

    print(
        "[SAFE MODE] No firmware will be programmed."
    )

    print(
        "Use --program --confirm PROGRAM-UB3 "
        "for hardware."
    )

    # --------------------------------------------------------------
    # Resources
    # --------------------------------------------------------------

    if not validate_project_resources():

        return False

    # --------------------------------------------------------------
    # Firmware
    # --------------------------------------------------------------

    firmware = load_selected_firmware()

    if firmware is None:

        return False

    # --------------------------------------------------------------
    # Device
    # --------------------------------------------------------------

    device = scan_device()

    if device is None:

        return False

    # --------------------------------------------------------------
    # Command
    # --------------------------------------------------------------

    command_info = build_command_preview(
        device,
        firmware,
    )

    if command_info is None:

        return False

    # --------------------------------------------------------------
    # Final safe-mode summary
    # --------------------------------------------------------------

    print_header(
        "SAFE PRE-FLIGHT COMPLETE"
    )

    print_pass(
        "Firmware repository validated"
    )

    print_pass(
        "Bundled Maple uploader validated"
    )

    print_pass(
        "Firmware selected and validated"
    )

    print_pass(
        "UB3 detected"
    )

    print_pass(
        "Maple Serial mode verified"
    )

    print_pass(
        "COM port automatically detected"
    )

    print_pass(
        "Maple command contract validated"
    )

    print()

    print(
        "Selected firmware:"
    )

    print(
        f"  {firmware.display_name}"
    )

    print()

    print(
        "Detected device:"
    )

    print(
        f"  COM port: "
        f"{command_info['com_port']}"
    )

    print()

    print(
        "No firmware was programmed."
    )

    return True


# ======================================================================
# PHYSICAL PROGRAMMING CONFIRMATION
# ======================================================================

def require_program_confirmation(
    confirmation: str | None,
) -> bool:
    """
    Require the exact explicit confirmation token.
    """

    if confirmation != PROGRAM_CONFIRMATION_TOKEN:

        print()
        print_fail(
            "Physical programming requires the exact "
            f"confirmation token: "
            f"{PROGRAM_CONFIRMATION_TOKEN}"
        )

        return False

    print_pass(
        "Physical programming confirmation accepted"
    )

    return True


# ======================================================================
# PHYSICAL PROGRAMMING
# ======================================================================

def run_physical_programming(
    confirmation: str | None,
) -> bool:
    """
    Execute the controlled physical programming flow.

    IMPORTANT:
    The actual upload is delegated to UploadService.
    """

    print_header(
        "STEP 5.4 - PHYSICAL UB3 PROGRAMMING"
    )

    print(
        "WARNING:"
    )

    print(
        "This operation will program the connected "
        "physical UB3."
    )

    print(
        "Do not disconnect the USB cable during upload."
    )

    if not require_program_confirmation(
        confirmation
    ):

        return False

    # --------------------------------------------------------------
    # Perform a fresh pre-flight immediately before
    # programming.
    # --------------------------------------------------------------

    if not validate_project_resources():

        return False

    firmware = load_selected_firmware()

    if firmware is None:

        return False

    device = scan_device()

    if device is None:

        return False

    command_info = build_command_preview(
        device,
        firmware,
    )

    if command_info is None:

        return False

    upload_service = command_info[
        "upload_service"
    ]

    # --------------------------------------------------------------
    # Final operator confirmation
    # --------------------------------------------------------------

    print()

    print(
        "FINAL PROGRAMMING TARGET"
    )

    print(
        f"  Device   : "
        f"{getattr(device, 'name', 'UB3')}"
    )

    print(
        f"  COM port : "
        f"{command_info['com_port']}"
    )

    print(
        f"  Firmware : "
        f"{firmware.display_name}"
    )

    print(
        f"  File     : "
        f"{firmware.filename}"
    )

    print()

    final_confirmation = input(
        "Type PROGRAM-UB3 to begin programming: "
    ).strip()

    if (
        final_confirmation
        != PROGRAM_CONFIRMATION_TOKEN
    ):

        print()
        print_warn(
            "Physical programming cancelled."
        )

        return False

    # --------------------------------------------------------------
    # Execute through existing UploadService
    # --------------------------------------------------------------

    print()

    print(
        "Starting physical UB3 programming..."
    )

    start_time = time.monotonic()

    try:

        result = upload_service.upload(
            firmware
        )

    except Exception as exc:

        duration = (
            time.monotonic()
            - start_time
        )

        print()
        print_fail(
            "UploadService raised an exception."
        )

        print(
            f"  Error   : {exc}"
        )

        print(
            f"  Duration: {duration:.2f}s"
        )

        return False

    duration = (
        time.monotonic()
        - start_time
    )

    # --------------------------------------------------------------
    # Upload result
    # --------------------------------------------------------------

    print_header(
        "PHYSICAL PROGRAMMING RESULT"
    )

    print(
        f"Status      : "
        f"{getattr(result, 'status', 'Unknown')}"
    )

    print(
        f"Success     : "
        f"{getattr(result, 'success', False)}"
    )

    print(
        f"Duration    : "
        f"{duration:.2f}s"
    )

    message = getattr(
        result,
        "message",
        "",
    )

    warning = getattr(
        result,
        "warning",
        "",
    )

    error = getattr(
        result,
        "error",
        "",
    )

    if message:

        print(
            f"Message     : {message}"
        )

    if warning:

        print_warn(
            f"Warning: {warning}"
        )

    if error:

        print_fail(
            f"Error: {error}"
        )

    if not getattr(
        result,
        "success",
        False,
    ):

        print()
        print_fail(
            "Physical firmware programming failed."
        )

        return False

    print()
    print_pass(
        "Firmware programming reported success"
    )

    # --------------------------------------------------------------
    # Post-upload device verification
    # --------------------------------------------------------------

    print_header(
        "POST-UPLOAD DEVICE VERIFICATION"
    )

    print(
        "Waiting for UB3 USB re-enumeration..."
    )

    time.sleep(2.0)

    try:

        device_service = DeviceService()

        devices = device_service.scan()

    except Exception as exc:

        print_warn(
            "Post-upload device scan failed: "
            f"{exc}"
        )

        print_warn(
            "The upload result was successful, "
            "but the device could not be verified."
        )

        return True

    # DeviceService.scan() returns a Device object.
    post_device = devices

    if (
        post_device is None
        or not post_device.connected
    ):

        print_warn(
            "UB3 did not immediately re-enumerate."
        )

        print_warn(
            "The Maple Loader may have reset the USB "
            "device. Reconnect the UB3 and verify "
            "the device manually."
        )

        return True

    print_pass(
        "Post-upload device scan detected UB3"
    )

    post_com = getattr(
        post_device,
        "com_port",
        "Unavailable",
    )

    post_maple = post_device.is_maple

    print(
        f"Device  : "
        f"{getattr(post_device, 'name', 'Unavailable')}"
    )

    print(
        f"COM port: "
        f"{post_com}"
    )

    print(
        f"Maple   : "
        f"{post_maple}"
    )

    print()
    print(
        "Post-upload verification completed."
    )

    return True


# ======================================================================
# ARGUMENT PARSER
# ======================================================================

def create_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "UB3 Firmware Updater Step 5.4 "
            "controlled physical validation tool."
        )
    )

    parser.add_argument(
        "--program",
        action="store_true",
        help=(
            "Enable physical UB3 programming. "
            "Safe mode is used by default."
        ),
    )

    parser.add_argument(
        "--confirm",
        type=str,
        default=None,
        help=(
            "Required programming confirmation "
            "token: PROGRAM-UB3"
        ),
    )

    return parser


# ======================================================================
# MAIN
# ======================================================================

def main() -> int:

    parser = create_parser()

    args = parser.parse_args()

    # --------------------------------------------------------------
    # Default = SAFE MODE
    # --------------------------------------------------------------

    if not args.program:

        success = run_safe_preflight()

        print()

        if success:

            print(
                "STEP 5.4 SAFE PRE-FLIGHT PASSED."
            )

            print(
                "No physical UB3 was programmed."
            )

            return 0

        print(
            "STEP 5.4 SAFE PRE-FLIGHT FAILED."
        )

        print(
            "No physical UB3 was programmed."
        )

        return 1

    # --------------------------------------------------------------
    # Programming mode
    # --------------------------------------------------------------

    success = run_physical_programming(
        args.confirm
    )

    print()

    if success:

        print(
            "STEP 5.4 PHYSICAL VALIDATION COMPLETED."
        )

        return 0

    print(
        "STEP 5.4 PHYSICAL VALIDATION FAILED "
        "OR WAS CANCELLED."
    )

    return 1


# ======================================================================
# ENTRY POINT
# ======================================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )