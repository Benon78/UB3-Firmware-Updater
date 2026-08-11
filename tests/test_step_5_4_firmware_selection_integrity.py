"""
======================================================================
STEP 5.4 - FIRMWARE SELECTION / UPLOAD INTEGRITY TEST
======================================================================

Strengthens the controlled physical-validation milestone by verifying
that every firmware exposed by the real firmware repository can be:

    GUI dropdown selection
        -> real Firmware model
        -> controller-equivalent selected firmware
        -> exact firmware path
        -> UploadService command

No physical UB3 is programmed.
No real USB scan is performed.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import bootstrap

from PySide6.QtWidgets import QApplication

from ub3_updater.models.device import Device, DeviceState
from ub3_updater.services.config_service import ConfigService
from ub3_updater.services.device_service import DeviceService
from ub3_updater.services.firmware_service import FirmwareService
from ub3_updater.services.upload_service import UploadService
from ub3_updater.widgets.dashboard_widget import DashboardWidget


print()
print("=" * 70)
print("STEP 5.4 - FIRMWARE SELECTION / UPLOAD INTEGRITY TEST")
print("=" * 70)


# =====================================================================
# APPLICATION
# =====================================================================

app = QApplication.instance()

if app is None:
    app = QApplication(sys.argv)


# =====================================================================
# SERVICES
# =====================================================================

firmware_service = FirmwareService()
device_service = DeviceService()

upload_service = UploadService(
    device_service=device_service,
    firmware_service=firmware_service,
)

firmwares = firmware_service.get_all()

assert firmwares, (
    "Firmware repository returned no firmware packages."
)

firmware_root = ConfigService.firmware_root().resolve()

assert firmware_root.is_dir(), (
    f"Firmware repository does not exist: {firmware_root}"
)


# =====================================================================
# TEST 1 - REAL FIRMWARE MODELS
# =====================================================================

print()
print("TEST 1 - FIRMWARE REPOSITORY")
print("=" * 70)

assert all(
    hasattr(firmware, "is_valid_file")
    for firmware in firmwares
)

print(
    f"[PASS] {len(firmwares)} real Firmware model(s) loaded"
)


# =====================================================================
# TEST 2 - GUI DROPDOWN
# =====================================================================

print()
print("TEST 2 - GUI FIRMWARE DROPDOWN")
print("=" * 70)

dashboard = DashboardWidget()

dashboard.set_firmwares(firmwares)

combo = dashboard.firmware_combo

assert combo.count() == len(firmwares)

print(
    f"[PASS] Dropdown contains all {combo.count()} firmware package(s)"
)


# =====================================================================
# TEST 3 - EACH FIRMWARE SELECTION
# =====================================================================

print()
print("TEST 3 - SELECT EACH FIRMWARE")
print("=" * 70)

device = Device(
    connected=True,
    state=DeviceState.MAPLE_SERIAL,
    com_port="COM3",
    usb_name="Maple Serial (COM3)",
    description="Maple Serial (COM3)",
    manufacturer="LeafLabs, LLC",
    vid="1EAF",
    pid="0004",
)

for index, expected_firmware in enumerate(firmwares):

    combo.setCurrentIndex(index)
    app.processEvents()

    selected = dashboard.selected_firmware()

    assert selected is not None

    assert selected is expected_firmware, (
        "Dropdown did not return the same Firmware model object."
    )

    assert selected.name == expected_firmware.name
    assert selected.version == expected_firmware.version

    selected_path = Path(
        selected.path
    ).resolve()

    assert selected_path.is_file(), (
        f"Selected firmware file does not exist: {selected_path}"
    )

    # The GUI must never redirect a repository firmware to C:\tmp
    # or another unrelated location.
    assert firmware_root in selected_path.parents, (
        f"Selected firmware is outside resources/firmware: "
        f"{selected_path}"
    )

    # The selected firmware must pass the normal repository validation.
    valid, error = firmware_service.validate(
        selected
    )

    assert valid, (
        f"Firmware validation failed for "
        f"{selected.name}: {error}"
    )

    print(
        f"[PASS] {selected.name} "
        f"Version {selected.version} selected"
    )

    print(
        f"       File: {selected.filename}"
    )


# =====================================================================
# TEST 4 - COMMAND USES THE SELECTED FIRMWARE
# =====================================================================

print()
print("TEST 4 - COMMAND / SELECTED FIRMWARE INTEGRITY")
print("=" * 70)

for index, expected_firmware in enumerate(firmwares):

    combo.setCurrentIndex(index)
    app.processEvents()

    selected = dashboard.selected_firmware()

    command = upload_service.build_command(
        device=device,
        firmware=selected,
    )

    selected_path = str(
        Path(selected.path).resolve()
    )

    assert command[-1] == selected_path, (
        f"Maple command does not use the selected firmware: "
        f"{selected.name}"
    )

    assert command[-4] == "COM3"
    assert command[-3] == upload_service.MAPLE_ALT_ID
    assert command[-2] == upload_service.MAPLE_DFU_ID

    print(
        f"[PASS] {selected.name} command uses selected binary"
    )

    print(
        f"       {selected_path}"
    )


# =====================================================================
# TEST 5 - ZNA2US SPECIFIC SAFETY CHECK
# =====================================================================

print()
print("TEST 5 - ZNA2US SELECTION")
print("=" * 70)

zna2us_index = next(
    (
        index
        for index, firmware in enumerate(firmwares)
        if firmware.name.upper() == "ZNA2US"
    ),
    None,
)

assert zna2us_index is not None

combo.setCurrentIndex(zna2us_index)
app.processEvents()

selected = dashboard.selected_firmware()

assert selected.name == "ZNA2US"
assert selected.version == "1.00"

command = upload_service.build_command(
    device=device,
    firmware=selected,
)

assert command[-1] == str(
    Path(selected.path).resolve()
)

print("[PASS] ZNA2US selected from GUI")
print("[PASS] ZNA2US Version 1.00 retained")
print("[PASS] ZNA2US binary passed to Maple command")


# =====================================================================
# TEST 6 - FIRMWARE CHANGE DOES NOT LEAK PREVIOUS PATH
# =====================================================================

print()
print("TEST 6 - FIRMWARE CHANGE / PATH ISOLATION")
print("=" * 70)

if len(firmwares) >= 2:

    first = firmwares[0]
    second = firmwares[1]

    combo.setCurrentIndex(0)
    app.processEvents()

    first_selected = dashboard.selected_firmware()

    first_command = upload_service.build_command(
        device=device,
        firmware=first_selected,
    )

    combo.setCurrentIndex(1)
    app.processEvents()

    second_selected = dashboard.selected_firmware()

    second_command = upload_service.build_command(
        device=device,
        firmware=second_selected,
    )

    assert first_selected.name == first.name
    assert second_selected.name == second.name

    assert first_command[-1] == str(
        Path(first.path).resolve()
    )

    assert second_command[-1] == str(
        Path(second.path).resolve()
    )

    assert first_command[-1] != second_command[-1], (
        "Firmware selection changed, but Maple command "
        "retained the previous firmware path."
    )

    print(
        f"[PASS] {first.name} -> {second.name} "
        "selection changes command firmware"
    )

else:

    print(
        "[PASS] Firmware path isolation not required "
        "(only one firmware package installed)"
    )


# =====================================================================
# TEST 7 - MAPLE COMMAND CONTRACT
# =====================================================================

print()
print("TEST 7 - MAPLE COMMAND CONTRACT")
print("=" * 70)

assert command[-4] == "COM3"
assert command[-3] == "2"
assert command[-2] == "1EAF:003"

print("[PASS] COM port = COM3")
print("[PASS] Maple ALT ID = 2")
print("[PASS] Maple DFU ID = 1EAF:003")
print("[PASS] Firmware path is final Maple argument")


# =====================================================================
# CLEANUP
# =====================================================================

dashboard.close()

print()
print("=" * 70)
print("ALL STEP 5.4 FIRMWARE SELECTION INTEGRITY TESTS PASSED")
print("=" * 70)
print()
print("No physical UB3 was programmed.")
