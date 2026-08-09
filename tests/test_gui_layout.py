"""
UB3 Firmware Updater - GUI Step 3 Layout / Scroll Test

Validates the Home page independent scrolling layout.

The Home page should maintain clear separation between:

LEFT COLUMN
    Connection Status
    Device Information
    Instructions

RIGHT COLUMN
    Firmware Selection
    Firmware Information
    Update Controls
    Upload Log

No physical UB3 is required.
No real USB monitoring is started.
No firmware is programmed.
"""

from __future__ import annotations

import os
import sys

os.environ.setdefault(
    "QT_QPA_PLATFORM",
    "offscreen",
)

import bootstrap

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ub3_updater.controllers.update_controller import (
    UpdateControllerState,
)
from ub3_updater.services.firmware_service import (
    FirmwareService,
)
from ub3_updater.ui.main_window import MainWindow


# =====================================================================
# APPLICATION
# =====================================================================

print()
print("=" * 70)
print("GUI STEP 3 - HOME PAGE LAYOUT TEST")
print("=" * 70)

app = QApplication.instance()

if app is None:
    app = QApplication(sys.argv)

from ub3_updater.themes.light_theme import STYLE

app.setStyleSheet(STYLE)


# =====================================================================
# CONTROLLER STUB
# =====================================================================

class ControllerStub:
    """
    Complete controller contract required by MainWindow/HomePage.

    This stub does not start the real DeviceMonitor.
    """

    def __init__(self):

        # -------------------------------------------------------------
        # Real firmware service
        # -------------------------------------------------------------

        self.firmware_service = (
            FirmwareService()
        )

        # -------------------------------------------------------------
        # Runtime values
        # -------------------------------------------------------------

        self.selected_firmware = None

        self.device = None

        self.status_message = (
            "Waiting for UB3"
        )

        # IMPORTANT:
        # Current project uses WAITING_FOR_DEVICE.
        self._state = (
            UpdateControllerState.WAITING_FOR_DEVICE
        )

        self.started = False

        self.stopped = False

        # -------------------------------------------------------------
        # GUI callback storage
        # -------------------------------------------------------------

        self._on_device_changed = None

        self._on_state_changed = None

        self._on_status = None

        self._on_output = None

        self._on_result = None

        self._on_error = None

    # =================================================================
    # STATE
    # =================================================================

    @property
    def state(self):
        return self._state

    # =================================================================
    # UPLOAD STATE
    # =================================================================

    @property
    def is_uploading(self):
        return False

    # =================================================================
    # UPDATE AVAILABILITY
    # =================================================================

    @property
    def can_update(self):
        return (
            self.selected_firmware is not None
            and self.device is not None
            and self.device.connected
        )

    # =================================================================
    # LIFECYCLE
    # =================================================================

    def start(self):
        """
        Simulate controller startup.

        No real hardware access.
        """

        self.started = True

        return True

    def stop(self):
        """
        Simulate controller shutdown.
        """

        self.stopped = True

        return True

    # =================================================================
    # DEVICE
    # =================================================================

    def refresh_device(self):
        """
        Test-only refresh.

        Does not access physical USB hardware.
        """

        return None

    # =================================================================
    # FIRMWARE
    # =================================================================

    def get_available_firmware(self):
        return (
            self.firmware_service.get_all()
        )

    def select_firmware(
        self,
        firmware,
    ):
        self.selected_firmware = firmware

        return firmware

    # =================================================================
    # UPDATE ACTIONS
    # =================================================================

    def update(self):
        """
        No physical update in layout tests.
        """

        return False

    def cancel(self):
        """
        No physical cancellation in layout tests.
        """

        return False

    # =================================================================
    # CALLBACK REGISTRATION
    # =================================================================

    def set_on_device_changed(
        self,
        callback,
    ):
        self._on_device_changed = callback

    def set_on_state_changed(
        self,
        callback,
    ):
        self._on_state_changed = callback

    def set_on_status(
        self,
        callback,
    ):
        self._on_status = callback

    def set_on_output(
        self,
        callback,
    ):
        self._on_output = callback

    def set_on_result(
        self,
        callback,
    ):
        self._on_result = callback

    def set_on_error(
        self,
        callback,
    ):
        self._on_error = callback


# =====================================================================
# CREATE WINDOW
# =====================================================================

controller = ControllerStub()

window = MainWindow(
    controller=controller
)

home = window.home_page


# =====================================================================
# TEST 1 - MAIN WINDOW
# =====================================================================

print()
print("TEST 1 - MAIN WINDOW")
print("=" * 70)

assert window is not None

assert home is not None

assert controller.started is True

print("[PASS] MainWindow created")

print("[PASS] HomePage created")

print("[PASS] Controller.start() called")


# =====================================================================
# TEST 2 - INDEPENDENT SCROLL AREAS
# =====================================================================

print()
print("TEST 2 - INDEPENDENT SCROLL AREAS")
print("=" * 70)

assert (
    home.left_scroll_area
    is not None
)

assert (
    home.right_scroll_area
    is not None
)

# -------------------------------------------------------------
# Vertical scrolling
# -------------------------------------------------------------

assert (
    home.left_scroll_area
    .verticalScrollBarPolicy()
    == Qt.ScrollBarPolicy.ScrollBarAsNeeded
)

assert (
    home.right_scroll_area
    .verticalScrollBarPolicy()
    == Qt.ScrollBarPolicy.ScrollBarAsNeeded
)

# -------------------------------------------------------------
# Horizontal scrolling
# -------------------------------------------------------------

assert (
    home.left_scroll_area
    .horizontalScrollBarPolicy()
    == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
)

assert (
    home.right_scroll_area
    .horizontalScrollBarPolicy()
    == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
)

# -------------------------------------------------------------
# Widget resizing
# -------------------------------------------------------------

assert (
    home.left_scroll_area.widgetResizable()
    is True
)

assert (
    home.right_scroll_area.widgetResizable()
    is True
)

print(
    "[PASS] Left section has independent "
    "vertical scrollbar"
)

print(
    "[PASS] Right section has independent "
    "vertical scrollbar"
)

print(
    "[PASS] Horizontal overflow disabled"
)

print(
    "[PASS] Left content is independently resizable"
)

print(
    "[PASS] Right content is independently resizable"
)


# =====================================================================
# TEST 3 - SECTION CONTENT
# =====================================================================

print()
print("TEST 3 - SECTION CONTENT")
print("=" * 70)

left_content = (
    home.left_scroll_area.widget()
)

right_content = (
    home.right_scroll_area.widget()
)

assert left_content is not None

assert right_content is not None

# -------------------------------------------------------------
# Left column
# -------------------------------------------------------------

assert (
    home.connection_widget.parent()
    is left_content
)

assert (
    home.device_information_widget.parent()
    is left_content
)

assert (
    home.instruction_widget.parent()
    is left_content
)

# -------------------------------------------------------------
# Right column
# -------------------------------------------------------------

assert (
    home.dashboard_widget.parent()
    is right_content
)

print(
    "[PASS] Connection section is in "
    "left scroll area"
)

print(
    "[PASS] Device information is in "
    "left scroll area"
)

print(
    "[PASS] Instructions are in "
    "left scroll area"
)

print(
    "[PASS] Firmware dashboard is in "
    "right scroll area"
)


# =====================================================================
# TEST 4 - FIRMWARE MODEL INTEGRITY
# =====================================================================

print()
print("TEST 4 - FIRMWARE MODEL INTEGRITY")
print("=" * 70)

firmwares = (
    controller
    .get_available_firmware()
)

assert firmwares, (
    "FirmwareService returned no firmware."
)

assert all(
    hasattr(
        firmware,
        "is_valid_file",
    )
    for firmware in firmwares
)

print(
    "[PASS] FirmwareService returns real "
    "Firmware objects"
)

print(
    "[PASS] Firmware validation API available"
)


# =====================================================================
# TEST 5 - RESIZE
# =====================================================================

print()
print("TEST 5 - WINDOW RESIZE")
print("=" * 70)

window.resize(
    1200,
    760,
)

app.processEvents()

assert window.width() == 1200

assert window.height() == 760

print(
    "[PASS] Large window layout accepted"
)

window.resize(
    1100,
    700,
)

app.processEvents()

assert window.width() == 1100

assert window.height() == 700

print(
    "[PASS] Reduced window layout accepted"
)

# The important point is that both scroll areas remain
# present after resizing.

assert (
    home.left_scroll_area
    is not None
)

assert (
    home.right_scroll_area
    is not None
)

print(
    "[PASS] Two-column structure remains intact"
)


# =====================================================================
# TEST 6 - BUTTON IDENTITY
# =====================================================================

print()
print("TEST 6 - BUTTON IDENTITY")
print("=" * 70)

dashboard = (
    home.dashboard_widget
)

assert (
    dashboard.update_button.objectName()
    == "updateButton"
)

assert (
    dashboard.cancel_button.objectName()
    == "cancelButton"
)

print(
    "[PASS] Update button object name preserved"
)

print(
    "[PASS] Cancel button object name preserved"
)


# =====================================================================
# CLEANUP
# =====================================================================

window.close()

print()
print("=" * 70)
print("ALL GUI STEP 3 LAYOUT TESTS PASSED")
print("=" * 70)

print(
    "Independent left/right scrolling validated."
)

print(
    "No physical UB3 was programmed."
)