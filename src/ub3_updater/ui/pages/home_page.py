"""
UB3 Firmware Updater - Home Page

First GUI integration step:
Device detection + firmware selection + update dashboard.
"""

from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QDialog
)

from ub3_updater.controllers.update_controller import (
    UpdateController,
    UpdateControllerState,
)
from ub3_updater.models.device import Device
from ub3_updater.models.firmware import Firmware
from ub3_updater.models.upload_result import UploadResult
from ub3_updater.models.pre_update_validation import PreUpdateValidationResult
from ub3_updater.ui.dialogs.update_confirmation_dialog import UpdateConfirmationDialog
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
from ub3_updater.widgets.components import (
    UB3Card,
    UB3SectionHeader,
    UB3StatusBadge,
)
from ub3_updater.themes.design_system import (
    BACKGROUND,
    SURFACE,
    BORDER,
    TEXT,
    TEXT_SECONDARY,
    PRIMARY,
    SPACE_2,
    SPACE_3,
    SPACE_4,
    SPACE_5,
    CARD_RADIUS,
)


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
        # Application heading / operator status
        # ----------------------------------------------

        self.logo_widget = LogoWidget()
        self.logo_widget.setObjectName("homeBrandHeader")
        self.logo_widget.setMinimumHeight(82)
        self.add_widget(self.logo_widget)

        # Compact workflow status directly under the application
        # heading. This is presentation-only; controller state remains
        # the single source of truth.
        self.home_status_row = QWidget()
        self.home_status_row.setObjectName("homeStatusRow")
        status_layout = QHBoxLayout(self.home_status_row)
        status_layout.setContentsMargins(2, 0, 2, 0)
        status_layout.setSpacing(SPACE_3)

        self.home_status_title = QLabel("Device Connection")
        self.home_status_title.setStyleSheet(
            f"color: {TEXT}; font-size: 11pt; font-weight: 700; border: none;"
        )
        status_layout.addWidget(self.home_status_title)

        self.home_status_badge = UB3StatusBadge(
            "Waiting for UB3",
            status="neutral",
        )
        self.home_status_badge.setMinimumWidth(120)
        status_layout.addWidget(self.home_status_badge)

        self.home_status_hint = QLabel(
            "Connect a UB3 device by USB to begin."
        )
        self.home_status_hint.setStyleSheet(
            f"color: {TEXT_SECONDARY}; border: none;"
        )
        status_layout.addWidget(self.home_status_hint)
        status_layout.addStretch()

        self.add_widget(self.home_status_row)

        # ----------------------------------------------
        # Unified workflow summary
        #
        # This is a presentation-only summary of the same
        # controller/device state already used by the page.
        # It does not introduce a second workflow state machine.
        # ----------------------------------------------

        self.workflow_summary_card = UB3Card(
            object_name="workflowSummaryCard"
        )

        workflow_layout = QVBoxLayout(
            self.workflow_summary_card
        )
        workflow_layout.setContentsMargins(
            SPACE_3, SPACE_2, SPACE_3, SPACE_2
        )
        workflow_layout.setSpacing(SPACE_2)

        workflow_header = UB3SectionHeader(
            "Update Workflow",
            "Follow the four operator stages from connection to final result.",
        )
        workflow_layout.addWidget(workflow_header)

        workflow_steps_layout = QHBoxLayout()
        workflow_steps_layout.setContentsMargins(0, 0, 0, 0)
        workflow_steps_layout.setSpacing(SPACE_2)

        self.workflow_step_widgets = {}
        workflow_definitions = (
            ("connect", "1", "Connect", "Waiting"),
            ("select", "2", "Select", "Select firmware"),
            ("update", "3", "Update", "Unavailable"),
            ("result", "4", "Result", "Awaiting result"),
        )

        for key, number, title, initial in workflow_definitions:
            step = QWidget()
            step.setObjectName(f"workflowStep_{key}")
            step_layout = QVBoxLayout(step)
            step_layout.setContentsMargins(0, 0, 0, 0)
            step_layout.setSpacing(3)

            number_label = QLabel(number)
            number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            number_label.setStyleSheet(
                f"color: {TEXT_SECONDARY}; font-size: 8pt; "
                "font-weight: 700; border: none;"
            )

            title_label = QLabel(title)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet(
                f"color: {TEXT}; font-weight: 700; border: none;"
            )

            badge = UB3StatusBadge(initial, "neutral")
            badge.setObjectName(f"workflow{key.title()}Badge")
            badge.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed,
            )

            step_layout.addWidget(number_label)
            step_layout.addWidget(title_label)
            step_layout.addWidget(badge)

            workflow_steps_layout.addWidget(step, 1)

            self.workflow_step_widgets[key] = {
                "number": number_label,
                "title": title_label,
                "badge": badge,
            }

        workflow_layout.addLayout(workflow_steps_layout)
        self.add_widget(self.workflow_summary_card)

        # Synchronize the workflow summary once during construction.
        # This establishes the initial presentation from the controller
        # state before the firmware refresh/default-selection logic runs.
        self._update_workflow_summary()

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
        self.left_scroll_area.setStyleSheet(
            f"QScrollArea#leftHomeScrollArea {{ background: {BACKGROUND}; border: none; }}"
        )
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
        self.right_scroll_area.setStyleSheet(
            f"QScrollArea#rightHomeScrollArea {{ background: {BACKGROUND}; border: none; }}"
        )
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
    # Unified Workflow Summary
    # ==================================================

    def _set_workflow_step(
        self,
        key: str,
        text: str,
        status: str,
    ) -> None:
        step = self.workflow_step_widgets.get(key)
        if not step:
            return
        badge = step["badge"]
        badge.setText(text)
        badge.set_status(status)

    def _update_workflow_summary(self) -> None:
        device = self.controller.device
        connected = bool(device and device.connected)
        firmware_selected = self.controller.selected_firmware is not None
        uploading = self.controller.is_uploading
        state = self.controller.state

        self._set_workflow_step(
            "connect",
            "Connected" if connected else "Waiting",
            "success" if connected else "neutral",
        )

        self._set_workflow_step(
            "select",
            "Selected" if firmware_selected else "Select firmware",
            "success" if firmware_selected else "neutral",
        )

        if uploading or state == UpdateControllerState.UPLOADING:
            update_text, update_status = "In progress", "warning"
        elif connected and firmware_selected and self.controller.can_update:
            update_text, update_status = "Ready", "success"
        elif connected:
            update_text, update_status = "Waiting", "neutral"
        else:
            update_text, update_status = "Unavailable", "neutral"

        self._set_workflow_step(
            "update",
            update_text,
            update_status,
        )

        if state == UpdateControllerState.SUCCESS:
            result_text, result_status = "Success", "success"
        elif state == UpdateControllerState.SUCCESS_WITH_WARNING:
            result_text, result_status = "Warning", "warning"
        elif state in (
            UpdateControllerState.FAILED,
            UpdateControllerState.ERROR,
        ):
            result_text, result_status = "Failed", "error"
        elif state == UpdateControllerState.CANCELLED:
            result_text, result_status = "Cancelled", "neutral"
        else:
            result_text, result_status = "Awaiting result", "neutral"

        self._set_workflow_step(
            "result",
            result_text,
            result_status,
        )

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

        if device is None or not device.connected:
            self.home_status_badge.setText("Waiting for UB3")
            self.home_status_badge.set_status("neutral")
            self.home_status_hint.setText(
                "Connect a UB3 device by USB to begin."
            )
        else:
            self.home_status_badge.setText("UB3 Connected")
            self.home_status_badge.set_status("success")
            com = device.com_port or "USB"
            self.home_status_hint.setText(
                f"Device detected on {com}. Ready for firmware selection."
            )

        self._refresh_button_state()
        self._update_workflow_summary()

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

        state_name = state.value
        if state in (
            UpdateControllerState.SUCCESS,
            UpdateControllerState.SUCCESS_WITH_WARNING,
        ):
            self.home_status_badge.setText(state_name)
            self.home_status_badge.set_status(
                "success" if state == UpdateControllerState.SUCCESS else "warning"
            )
        elif state in (
            UpdateControllerState.FAILED,
            UpdateControllerState.ERROR,
        ):
            self.home_status_badge.setText(state_name)
            self.home_status_badge.set_status("error")
        elif state == UpdateControllerState.UPLOADING:
            self.home_status_badge.setText("Uploading")
            self.home_status_badge.set_status("warning")
        elif state == UpdateControllerState.READY:
            self.home_status_badge.setText("Ready")
            self.home_status_badge.set_status("success")
        else:
            self.home_status_badge.setText("Waiting for UB3")
            self.home_status_badge.set_status("neutral")

        self._refresh_button_state()
        self._update_workflow_summary()

    def update_status(
        self,
        message: str,
    ):
        self.dashboard_widget.message_label.setText(
            message
        )

        # During an active upload, controller status messages are
        # translated into the operator-facing workflow progress
        # indicator. The dashboard owns the presentation mapping.
        if self.controller.is_uploading:
            self.dashboard_widget.update_progress(
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

        # Maple Loader output is also useful as a live phase signal.
        # This does not fabricate byte-level progress; the dashboard
        # only maps recognized workflow phases.
        if self.controller.is_uploading:
            self.dashboard_widget.update_progress(
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
        self._update_workflow_summary()
        self._schedule_worker_reset()

    # ==================================================
    # Upload Worker Lifecycle
    # ==================================================

    def _schedule_worker_reset(self) -> None:
        """
        Schedule a safe worker reset after a terminal upload result.

        UploadWorker emits its completion callback before its thread has
        necessarily finished. The controller deliberately refuses to
        reset a running worker, so the reset is polled from the GUI event
        loop until the worker is no longer active.
        """
        QTimer.singleShot(
            50,
            self._reset_worker_when_finished,
        )

    def _reset_worker_when_finished(self) -> None:
        """
        Return UploadWorker to IDLE once its thread has exited.
        """
        if self.controller.is_uploading:
            QTimer.singleShot(
                50,
                self._reset_worker_when_finished,
            )
            return

        self.controller.reset_worker()
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
        self._update_workflow_summary()

    def _update_requested(self):
        """
        Run the complete operator confirmation boundary.

        Stage 1:
            Fresh pre-update validation.

        Stage 2:
            Operator reviews the validated device/firmware.

        Stage 3:
            After confirmation, the controller performs a second
            fresh validation and only then starts UploadWorker.
        """

        self.dashboard_widget.clear_output()

        validate = getattr(
            self.controller,
            "validate_before_update",
            None,
        )

        confirm_update = getattr(
            self.controller,
            "confirm_update",
            None,
        )

        # --------------------------------------------------
        # Compatibility guard for lightweight GUI test
        # controllers. The real UpdateController always provides
        # these methods.
        # --------------------------------------------------

        if not callable(validate) or not callable(confirm_update):
            self.dashboard_widget.message_label.setText(
                "Update safety validation is unavailable."
            )
            self._refresh_button_state()
            return

        # --------------------------------------------------
        # First validation: capture the device/firmware that
        # will be shown in the confirmation dialog.
        # --------------------------------------------------

        validation = validate(
            expected_device=self.controller.device,
        )

        if not validation.valid:
            self.dashboard_widget.message_label.setText(
                validation.message
            )
            self._refresh_button_state()
            return

        # --------------------------------------------------
        # Operator confirmation.
        # --------------------------------------------------

        dialog = UpdateConfirmationDialog(
            validation,
            parent=self.window(),
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            self.dashboard_widget.message_label.setText(
                "Firmware update cancelled."
            )
            self._refresh_button_state()
            return

        # --------------------------------------------------
        # Second validation + UploadWorker start.
        # --------------------------------------------------

        started = confirm_update(
            validation
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
