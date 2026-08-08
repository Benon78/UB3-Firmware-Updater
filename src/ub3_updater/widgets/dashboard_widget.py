"""
UB3 Firmware Updater - Firmware / Update Dashboard
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

from ub3_updater.models.firmware import Firmware
from ub3_updater.models.upload_result import UploadResult
from ub3_updater.themes.light_theme import (
    BORDER,
    CARD,
    ERROR,
    INFO_BACKGROUND,
    SUCCESS,
    SUCCESS_BACKGROUND,
    TEXT,
    TEXT_SECONDARY,
    WARNING,
    WARNING_BACKGROUND,
)


class DashboardWidget(QFrame):
    """
    Right-side update dashboard.

    Responsibilities are presentation only:
    - firmware selection
    - firmware information
    - update/cancel actions
    - progress/status display
    - upload output display

    Upload business logic remains in UpdateController.
    """

    firmware_changed = Signal(object)
    update_requested = Signal()
    cancel_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._firmwares: list[Firmware] = []
        self._build_ui()
        self.set_ready_state(False)

    def _build_ui(self):
        self.setObjectName("dashboardCard")
        self.setStyleSheet(
            f"""
            QFrame#dashboardCard {{
                background: {CARD};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        title = QLabel("Firmware Update")
        title.setStyleSheet(
            f"""
            color: {TEXT};
            font-size: 14pt;
            font-weight: 600;
            border: none;
            """
        )
        layout.addWidget(title)

        # Firmware selector
        firmware_title = QLabel("Selected Firmware")
        firmware_title.setStyleSheet(
            f"font-weight: 600; color: {TEXT}; border: none;"
        )
        layout.addWidget(firmware_title)

        self.firmware_combo = QComboBox()
        self.firmware_combo.setMinimumHeight(38)
        self.firmware_combo.currentIndexChanged.connect(
            self._firmware_index_changed
        )
        layout.addWidget(self.firmware_combo)

        self.firmware_info = QLabel("No firmware selected")
        self.firmware_info.setWordWrap(True)
        self.firmware_info.setStyleSheet(
            f"""
            color: {TEXT_SECONDARY};
            border: none;
            padding: 4px;
            """
        )
        layout.addWidget(self.firmware_info)

        # Status
        self.status_label = QLabel("Waiting for UB3")
        self.status_label.setStyleSheet(
            f"""
            color: {TEXT_SECONDARY};
            font-weight: 600;
            border: none;
            """
        )
        layout.addWidget(self.status_label)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setFormat("Working...")
        layout.addWidget(self.progress_bar)

        # Message
        self.message_label = QLabel("")
        self.message_label.setWordWrap(True)
        self.message_label.setMinimumHeight(38)
        self.message_label.setStyleSheet(
            f"""
            color: {TEXT_SECONDARY};
            border: none;
            """
        )
        layout.addWidget(self.message_label)

        # Output
        output_title = QLabel("Upload Log")
        output_title.setStyleSheet(
            f"font-weight: 600; color: {TEXT}; border: none;"
        )
        layout.addWidget(output_title)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(120)
        self.output.setPlaceholderText(
            "Upload messages will appear here."
        )
        layout.addWidget(self.output)

        # Buttons
        buttons = QHBoxLayout()
        buttons.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setProperty("class", "danger")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(
            self.cancel_requested.emit
        )
        buttons.addWidget(self.cancel_button)

        self.update_button = QPushButton("Update")
        self.update_button.setProperty("class", "success")
        self.update_button.setMinimumWidth(130)
        self.update_button.clicked.connect(
            self.update_requested.emit
        )
        buttons.addWidget(self.update_button)

        layout.addLayout(buttons)

    def set_firmwares(
        self,
        firmwares: list[Firmware],
        selected: Firmware | None = None,
    ):
        self._firmwares = list(firmwares)

        previous_path = (
            selected.path
            if selected is not None
            else ""
        )

        self.firmware_combo.blockSignals(True)
        self.firmware_combo.clear()

        for firmware in self._firmwares:
            self.firmware_combo.addItem(
                firmware.display_name,
                firmware,
            )

        if selected is not None:
            for index, firmware in enumerate(self._firmwares):
                if firmware.path == previous_path:
                    self.firmware_combo.setCurrentIndex(index)
                    break

        self.firmware_combo.blockSignals(False)

        self._update_firmware_info()

    def _firmware_index_changed(self, index: int):
        self._update_firmware_info()

        if index < 0 or index >= len(self._firmwares):
            self.firmware_changed.emit(None)
            return

        self.firmware_changed.emit(
            self._firmwares[index]
        )

    def _update_firmware_info(self):
        index = self.firmware_combo.currentIndex()

        if index < 0 or index >= len(self._firmwares):
            self.firmware_info.setText(
                "No firmware selected"
            )
            return

        firmware = self._firmwares[index]

        lines = [
            f"Version: {firmware.version or '--'}",
            f"Target: {firmware.target_device or firmware.hardware or '--'}",
        ]

        if firmware.description:
            lines.append(
                f"Description: {firmware.description}"
            )

        if firmware.filename:
            lines.append(
                f"File: {firmware.filename}"
            )

        self.firmware_info.setText(
            "\n".join(lines)
        )

    def selected_firmware(self) -> Firmware | None:
        index = self.firmware_combo.currentIndex()

        if index < 0 or index >= len(self._firmwares):
            return None

        return self._firmwares[index]

    def set_ready_state(self, can_update: bool):
        self.update_button.setEnabled(
            bool(can_update)
        )
        self.cancel_button.setEnabled(False)
        self.progress_bar.setVisible(False)

        if not can_update:
            self.status_label.setText(
                "Waiting for UB3"
            )

    def set_controller_state(
        self,
        state_value: str,
        message: str,
        can_update: bool,
    ):
        self.status_label.setText(
            state_value
        )

        self.message_label.setText(
            message
        )

        uploading = (
            "Uploading" in state_value
            or state_value == "Uploading Firmware"
        )

        if uploading:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            self.update_button.setEnabled(False)
            self.cancel_button.setEnabled(True)
        else:
            self.progress_bar.setVisible(False)
            self.cancel_button.setEnabled(False)
            self.update_button.setEnabled(
                bool(can_update)
            )

        self._set_status_style(
            state_value
        )

    def append_output(self, text: str):
        if not text:
            return

        self.output.appendPlainText(
            text.rstrip()
        )

    def clear_output(self):
        self.output.clear()

    def show_result(
        self,
        result: UploadResult,
        can_update: bool,
    ):
        self.message_label.setText(
            result.display_message
        )

        if result.success and result.has_warning:
            self.status_label.setText(
                "Success With Warning"
            )
            self._set_status_style(
                "Success With Warning"
            )

        elif result.success:
            self.status_label.setText(
                "Firmware Updated Successfully"
            )
            self._set_status_style(
                "Success"
            )

        elif result.cancelled:
            self.status_label.setText(
                "Update Cancelled"
            )
            self._set_status_style(
                "Cancelled"
            )

        else:
            self.status_label.setText(
                "Update Failed"
            )
            self._set_status_style(
                "Failed"
            )

        self.progress_bar.setVisible(False)
        self.cancel_button.setEnabled(False)
        self.update_button.setEnabled(
            bool(can_update)
        )

        if result.stdout:
            self.append_output(
                result.stdout
            )

        if result.stderr:
            self.append_output(
                "[ERROR]\n" + result.stderr
            )

        if result.warning:
            self.append_output(
                "[WARNING]\n" + result.warning
            )

        if result.error:
            self.append_output(
                "[ERROR]\n" + result.error
            )

    def _set_status_style(
        self,
        state_value: str,
    ):
        value = state_value.lower()

        if "success" in value:
            color = SUCCESS
            background = SUCCESS_BACKGROUND
        elif "warning" in value:
            color = WARNING
            background = WARNING_BACKGROUND
        elif (
            "failed" in value
            or "error" in value
        ):
            color = ERROR
            background = "#FEF2F2"
        elif "uploading" in value:
            color = "#D97706"
            background = WARNING_BACKGROUND
        else:
            color = TEXT_SECONDARY
            background = INFO_BACKGROUND

        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                background: {background};
                border: none;
                border-radius: 6px;
                padding: 7px 10px;
                font-weight: 600;
            }}
            """
        )
