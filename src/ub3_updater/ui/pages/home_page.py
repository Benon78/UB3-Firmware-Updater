"""
UB3 Firmware Updater - Home Page

First GUI integration step:
Device detection + firmware selection + update dashboard.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
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
from ub3_updater.widgets.device_information import (
    DeviceInformationWidget,
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
        #
        # Each column owns its own vertical scroll area.
        # This prevents the device cards and firmware dashboard
        # from compressing into each other when the window height
        # is reduced or the content grows.
        # ----------------------------------------------

        columns = QHBoxLayout()
        columns.setSpacing(16)
        columns.setContentsMargins(0, 0, 0, 0)

        # -----------------------------
        # Left: connection/device info
        # -----------------------------

        left_content = QWidget()
        left_content.setObjectName("homeLeftContent")
        left_content.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Minimum,
        )

        left = QVBoxLayout(left_content)
        left.setContentsMargins(2, 2, 8, 2)
        left.setSpacing(14)

        # -----------------------------
        # Right: firmware/update area
        # -----------------------------

        right_content = QWidget()
        right_content.setObjectName("homeRightContent")
        right_content.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Minimum,
        )

        right = QVBoxLayout(right_content)
        right.setContentsMargins(2, 2, 8, 2)
        right.setSpacing(14)

        self.connection_widget = ConnectionStatusWidget()
        # HomePage-level reference to the operator refresh control.
        # The button remains owned by ConnectionStatusWidget so the
        # connection card keeps the refresh action next to device state.
        self.refresh_button = self.connection_widget.refresh_button
        self.connection_widget.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed,
        )

        self.device_information_widget = DeviceInformationWidget()
        self.device_information_widget.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Preferred,
        )

        self.instruction_widget = InstructionWidget()
        self.instruction_widget.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Preferred,
        )

        self.dashboard_widget = DashboardWidget()
        self.dashboard_widget.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Preferred,
        )

        left.addWidget(self.connection_widget)
        left.addWidget(self.device_information_widget)
        left.addWidget(self.instruction_widget)
        left.addStretch(1)

        right.addWidget(self.dashboard_widget)
        right.addStretch(1)

        # -----------------------------
        # Independent scroll areas
        # -----------------------------

        self.left_scroll_area = QScrollArea()
        self.left_scroll_area.setObjectName("leftHomeScrollArea")
        self.left_scroll_area.setWidgetResizable(True)
        self.left_scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.left_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.left_scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.left_scroll_area.setWidget(left_content)
        self.left_scroll_area.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.right_scroll_area = QScrollArea()
        self.right_scroll_area.setObjectName("rightHomeScrollArea")
        self.right_scroll_area.setWidgetResizable(True)
        self.right_scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.right_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.right_scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.right_scroll_area.setWidget(right_content)
        self.right_scroll_area.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        # Keep the established 1:2 visual balance while allowing
        # both sections to consume the available window height.
        columns.addWidget(self.left_scroll_area, 1)
        columns.addWidget(self.right_scroll_area, 2)

        self.add_layout(columns)

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

        self.device_information_widget.update_device(
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
