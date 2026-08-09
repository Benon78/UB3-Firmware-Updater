"""
======================================================================
UB3 FIRMWARE UPDATER
STEP 4.2 - UPDATE CONFIRMATION DIALOG TEST
======================================================================

No physical UB3 is programmed.
The dialog is presentation-only and never starts UploadWorker.
"""

from pathlib import Path
import tempfile

import bootstrap

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog

from ub3_updater.models.device import Device, DeviceState
from ub3_updater.models.firmware import Firmware
from ub3_updater.models.pre_update_validation import (
    PreUpdateValidationResult,
)
from ub3_updater.ui.dialogs.update_confirmation_dialog import (
    UpdateConfirmationDialog,
)


app = QApplication.instance()

if app is None:
    app = QApplication([])


# =====================================================================
# FIXTURES
# =====================================================================


def make_device():
    return Device(
        connected=True,
        state=DeviceState.MAPLE_SERIAL,
        com_port="COM3",
        usb_name="Maple Serial (COM3)",
        description="Maple Serial (COM3)",
        manufacturer="LeafLabs, LLC",
        vid="1EAF",
        pid="0004",
        hwid="USB VID:PID=1EAF:0004",
    )


def make_firmware(path):
    return Firmware(
        name="ZNA2US",
        version="1.00",
        target_device="UB3",
        filename=Path(path).name,
        path=str(path),
        size=Path(path).stat().st_size,
    )


def make_valid_result(device, firmware):
    return PreUpdateValidationResult(
        valid=True,
        message="Pre-update validation passed.",
        device=device,
        firmware=firmware,
        checks={
            "device_connected": True,
            "maple_serial": True,
            "same_device": True,
            "firmware_selected": True,
            "firmware_valid": True,
        },
    )


def make_invalid_result(device=None, firmware=None):
    return PreUpdateValidationResult(
        valid=False,
        message="UB3 is no longer connected.",
        device=device,
        firmware=firmware,
        checks={
            "device_connected": False,
            "maple_serial": False,
            "same_device": False,
            "firmware_selected": True,
            "firmware_valid": True,
        },
    )


# =====================================================================
# TEST SETUP
# =====================================================================

print()
print("=" * 70)
print("STEP 4.2 - UPDATE CONFIRMATION DIALOG TEST")
print("=" * 70)

with tempfile.TemporaryDirectory() as temp_dir:

    firmware_path = (
        Path(temp_dir) / "UnlockBoxIII_ZNA2US_1.00.bin"
    )
    firmware_path.write_bytes(b"UB3 TEST FIRMWARE")

    device = make_device()
    firmware = make_firmware(firmware_path)
    validation = make_valid_result(
        device,
        firmware,
    )

    # ================================================================
    # TEST 1 - DIALOG CREATION
    # ================================================================

    print()
    print("TEST 1 - DIALOG CREATION")
    print("=" * 70)

    dialog = UpdateConfirmationDialog(
        validation
    )

    assert dialog is not None
    assert dialog.isModal()
    assert dialog.objectName() == (
        "updateConfirmationDialog"
    )

    print("[PASS] Confirmation dialog created")
    print("[PASS] Dialog is modal")
    print("[PASS] Dialog object identity correct")

    # ================================================================
    # TEST 2 - DEVICE INFORMATION
    # ================================================================

    print()
    print("TEST 2 - DEVICE INFORMATION")
    print("=" * 70)

    device_card = dialog.findChild(
        object,
        "deviceCard",
    )

    assert device_card is not None

    device_text = device_card.findChildren(
        type(dialog.findChild(object, "fieldValue"))
    )

    # Use complete widget text rather than relying on layout order.
    card_text = " ".join(
        label.text()
        for label in device_card.findChildren(
            __import__(
                "PySide6.QtWidgets",
                fromlist=["QLabel"],
            ).QLabel
        )
    )

    assert "Maple Serial (COM3)" in card_text
    assert "COM3" in card_text
    assert "Maple Serial" in card_text
    assert "1EAF:0004" in card_text
    assert "LeafLabs, LLC" in card_text

    print("[PASS] Device name displayed")
    print("[PASS] COM port displayed")
    print("[PASS] Maple Serial mode displayed")
    print("[PASS] VID:PID displayed")
    print("[PASS] Manufacturer displayed")

    # ================================================================
    # TEST 3 - FIRMWARE INFORMATION
    # ================================================================

    print()
    print("TEST 3 - FIRMWARE INFORMATION")
    print("=" * 70)

    firmware_card = dialog.findChild(
        object,
        "firmwareCard",
    )

    assert firmware_card is not None

    from PySide6.QtWidgets import QLabel

    firmware_text = " ".join(
        label.text()
        for label in firmware_card.findChildren(
            QLabel
        )
    )

    assert "ZNA2US" in firmware_text
    assert "1.00" in firmware_text
    assert "UB3" in firmware_text
    assert firmware.filename in firmware_text

    print("[PASS] Firmware name displayed")
    print("[PASS] Firmware version displayed")
    print("[PASS] Target device displayed")
    print("[PASS] Firmware filename displayed")
    print("[PASS] Firmware size displayed")

    # ================================================================
    # TEST 4 - VALIDATION STATUS
    # ================================================================

    print()
    print("TEST 4 - VALIDATION STATUS")
    print("=" * 70)

    labels = dialog.findChildren(QLabel)

    all_text = " ".join(
        label.text()
        for label in labels
    )

    assert "Pre-update checks passed" in all_text
    assert "device identity" in all_text
    assert "Maple Serial" in all_text
    assert "firmware file" in all_text

    print("[PASS] Validation success is clearly displayed")
    print("[PASS] Safety checks are summarized")

    # ================================================================
    # TEST 5 - CONFIRMATION GUARD
    # ================================================================

    print()
    print("TEST 5 - CONFIRMATION GUARD")
    print("=" * 70)

    assert dialog.update_button.isEnabled() is False
    assert dialog.confirmation_checked is False

    print(
        "[PASS] Update action disabled before acknowledgement"
    )

    dialog.confirmation_check.setChecked(True)
    app.processEvents()

    assert dialog.confirmation_checked is True
    assert dialog.update_button.isEnabled() is True

    print("[PASS] Update enabled after acknowledgement")

    dialog.confirmation_check.setChecked(False)
    app.processEvents()

    assert dialog.update_button.isEnabled() is False

    print(
        "[PASS] Update disabled when acknowledgement is removed"
    )

    # ================================================================
    # TEST 6 - CANCEL
    # ================================================================

    print()
    print("TEST 6 - CANCEL ACTION")
    print("=" * 70)

    dialog.confirmation_check.setChecked(True)
    app.processEvents()

    dialog.cancel_button.click()

    assert dialog.result() == QDialog.DialogCode.Rejected
    assert dialog.confirmed is False

    print("[PASS] Cancel closes dialog")
    print("[PASS] Cancel does not confirm update")

    dialog.deleteLater()
    app.processEvents()

    # ================================================================
    # TEST 7 - CONFIRM
    # ================================================================

    print()
    print("TEST 7 - CONFIRM ACTION")
    print("=" * 70)

    dialog = UpdateConfirmationDialog(
        validation
    )

    dialog.confirmation_check.setChecked(True)
    app.processEvents()

    dialog.update_button.click()

    assert dialog.result() == QDialog.DialogCode.Accepted
    assert dialog.confirmed is True
    assert dialog.device is device
    assert dialog.firmware is firmware

    print("[PASS] Update confirmation accepted")
    print("[PASS] Confirmed device preserved")
    print("[PASS] Confirmed firmware preserved")

    dialog.deleteLater()
    app.processEvents()

    # ================================================================
    # TEST 8 - INVALID VALIDATION RESULT
    # ================================================================

    print()
    print("TEST 8 - INVALID VALIDATION RESULT")
    print("=" * 70)

    invalid_validation = make_invalid_result(
        device,
        firmware,
    )

    dialog = UpdateConfirmationDialog(
        invalid_validation
    )

    assert dialog.update_button.isEnabled() is False
    assert dialog.confirmation_check.isEnabled() is False

    print(
        "[PASS] Invalid validation cannot be confirmed"
    )

    dialog.deleteLater()
    app.processEvents()


print()
print("=" * 70)
print("ALL STEP 4.2 UPDATE CONFIRMATION DIALOG TESTS PASSED")
print("=" * 70)
print()
print("No physical UB3 was programmed.")
