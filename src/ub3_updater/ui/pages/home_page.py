"""
UB3 Firmware Updater - Home Page

First GUI integration step:
Device detection + firmware selection + update dashboard.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ub3_updater.controllers.update_controller import (
    UpdateController,
    UpdateControllerState,
)
from ub3_updater.models.device import Device
from ub3_updater.models.firmware import Firmware
from ub3_updater.models.upload_result import UploadResult
from ub3_updater.themes.light_theme import (
    TEXT,
    TEXT_SECONDARY,
)
from ub3_updater.ui.base_page import BasePage
from ub3_updater.widgets.connection_status import (
    ConnectionStatusWidget,
)
from ub3_updater.widgets.dashboard_widget import (
    DashboardWidget,
)
from ub3_updater.widgets.instruction_widget import (
    InstructionWidget,
)
from ub3_updater.widgets.logo_widget import LogoWidget


class HomePage(BasePage):
    """
    Operator home screen.

    The page communicates with UpdateController through
    explicit methods. It does not call hardware or upload
    services directly.
    """

    def __init__(
        self,
        controller: UpdateController,
        parent=None,
    ):
        self.controller = controller

        super().__init__(
            title="",
            subtitle="",
        )

        self.build_home()

    def build_home(self):
        # BasePage's title/subtitle are intentionally empty.
        self.main_layout.setContentsMargins(
            18, 16, 18, 12
        )
        self.main_layout.setSpacing(12)

        # ----------------------------------------------
        # Application heading
        # ----------------------------------------------

        self.logo_widget = LogoWidget()
        self.logo_widget.setMinimumHeight(82)
        self.add_widget(
            self.logo_widget
        )

        # ----------------------------------------------
        # Main two-column area
        # ----------------------------------------------

        columns = QHBoxLayout()
        columns.setSpacing(14)

        left = QVBoxLayout()
        left.setSpacing(14)

        right = QVBoxLayout()
        right.setSpacing(14)

        self.connection_widget = (
            ConnectionStatusWidget()
        )

        self.instruction_widget = (
            InstructionWidget()
        )

        self.dashboard_widget = (
            DashboardWidget()
        )

        left.addWidget(
            self.connection_widget
        )

        left.addWidget(
            self.instruction_widget
        )

        left.addStretch()

        right.addWidget(
            self.dashboard_widget
        )

        columns.addLayout(
            left,
            1,
        )

        columns.addLayout(
            right,
            2,
        )

        self.add_layout(
            columns
        )

        # ----------------------------------------------
        # Controller wiring
        # ----------------------------------------------

        self.connection_widget.refresh_requested.connect(
            self._refresh_requested
        )

        self.dashboard_widget.firmware_changed.connect(
            self._firmware_changed
        )

        self.dashboard_widget.update_requested.connect(
            self._update_requested
        )

        self.dashboard_widget.cancel_requested.connect(
            self._cancel_requested
        )

        # ----------------------------------------------
        # Initial firmware list
        # ----------------------------------------------

        self.refresh_firmware()

    # ==================================================
    # Firmware
    # ==================================================

    def refresh_firmware(self):
        firmwares = (
            self.controller
            .get_available_firmware()
        )

        selected = (
            self.controller.selected_firmware
        )

        self.dashboard_widget.set_firmwares(
            firmwares,
            selected=selected,
        )

        # If nothing is selected, choose the controller's
        # configured default firmware.
        if selected is None and firmwares:
            default = (
                self.controller
                .firmware_service
                .get_default()
            )

            if default is not None:
                self.controller.select_firmware(
                    default
                )
                self.dashboard_widget.set_firmwares(
                    firmwares,
                    selected=default,
                )

        self._refresh_button_state()

    # ==================================================
    # Device
    # ==================================================

    def update_device(
        self,
        device: Device | None,
    ):
        self.connection_widget.update_device(
            device
        )

        self._refresh_button_state()

    # ==================================================
    # Controller State
    # ==================================================

    def update_controller_state(
        self,
        state: UpdateControllerState,
        message: str,
    ):
        self.dashboard_widget.set_controller_state(
            state.value,
            message,
            self.controller.can_update,
        )

        self._refresh_button_state()

    def update_status(
        self,
        message: str,
    ):
        self.dashboard_widget.message_label.setText(
            message
        )

    # ==================================================
    # Upload
    # ==================================================

    def append_output(
        self,
        output: str,
    ):
        self.dashboard_widget.append_output(
            output
        )

    def show_result(
        self,
        result: UploadResult,
    ):
        self.dashboard_widget.show_result(
            result,
            self.controller.can_update,
        )

        self._refresh_button_state()

    # ==================================================
    # Actions
    # ==================================================

    def _refresh_requested(self):
        self.controller.refresh_device()

    def _firmware_changed(
        self,
        firmware: Firmware | None,
    ):
        if firmware is None:
            self.controller.select_firmware(
                None
            )
        else:
            self.controller.select_firmware(
                firmware
            )

        self._refresh_button_state()

    def _update_requested(self):
        self.dashboard_widget.clear_output()

        started = (
            self.controller.update()
        )

        if not started:
            self.dashboard_widget.message_label.setText(
                self.controller.status_message
            )

        self._refresh_button_state()

    def _cancel_requested(self):
        self.controller.cancel()

    # ==================================================
    # Button state
    # ==================================================

    def _refresh_button_state(self):
        self.dashboard_widget.update_button.setEnabled(
            self.controller.can_update
            and not self.controller.is_uploading
        )

        if self.controller.is_uploading:
            self.dashboard_widget.cancel_button.setEnabled(
                True
            )
        else:
            self.dashboard_widget.cancel_button.setEnabled(
                False
            )
