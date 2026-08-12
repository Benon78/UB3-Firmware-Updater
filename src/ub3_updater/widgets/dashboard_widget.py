"""
UB3 Firmware Updater - Firmware / Update Dashboard

Step 4.5:
Operator-focused live firmware update progress presentation.

The widget does not invent byte-level upload progress. Maple Loader's
current output does not provide a trustworthy numeric transfer percentage,
so the progress indicator represents verified workflow phases.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QFont
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QProgressBar,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ub3_updater.models.firmware import Firmware
from ub3_updater.models.upload_result import UploadResult
from ub3_updater.themes.design_system import COMBO_BOX_STYLE
from ub3_updater.widgets.components import (
    UB3Button,
    UB3ComboBox,
    UB3Card,
    UB3StatusBadge,
    UB3SectionHeader,
    UB3StatusBanner,
)
from ub3_updater.themes.light_theme import (
    BORDER,
    CARD,
    ERROR,
    INFO_BACKGROUND,
    PRIMARY,
    PRIMARY_DARK,
    SUCCESS,
    SUCCESS_BACKGROUND,
    TEXT,
    TEXT_SECONDARY,
    WARNING,
    WARNING_BACKGROUND,
)


# =========================================================
# Circular Progress
# =========================================================

class CircularProgressWidget(QWidget):
    """
    Compact circular workflow progress indicator.

    The percentage represents the update workflow phase, not bytes
    transferred. This distinction is intentional because Maple Loader
    does not expose reliable byte-level progress.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._value = 0
        self._status = "Ready"

        self.setObjectName("circularProgress")
        self.setMinimumSize(132, 132)
        self.setMaximumSize(150, 150)
        self.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )

    def set_value(
        self,
        value: int,
        status: str | None = None,
    ) -> None:
        self._value = max(0, min(100, int(value)))

        if status is not None:
            self._status = str(status)

        self.update()

    def value(self) -> int:
        return self._value

    def status(self) -> str:
        return self._status

    def paintEvent(self, event):
        del event

        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        rect = QRectF(
            10,
            10,
            self.width() - 20,
            self.height() - 20,
        )

        # Background ring.
        background_pen = QPen(
            QColor("#E5E7EB")
        )
        background_pen.setWidth(9)
        background_pen.setCapStyle(
            Qt.PenCapStyle.RoundCap
        )

        painter.setPen(background_pen)
        painter.drawArc(
            rect,
            90 * 16,
            -360 * 16,
        )

        # Progress ring.
        progress_pen = QPen(
            QColor(PRIMARY)
        )
        progress_pen.setWidth(9)
        progress_pen.setCapStyle(
            Qt.PenCapStyle.RoundCap
        )

        painter.setPen(progress_pen)

        span = int(
            -360
            * 16
            * self._value
            / 100
        )

        if self._value > 0:
            painter.drawArc(
                rect,
                90 * 16,
                span,
            )

        # Percentage.
        painter.setPen(
            QColor(TEXT)
        )

        percentage_font = QFont(
            "Segoe UI",
            18,
            QFont.Weight.Bold,
        )

        painter.setFont(
            percentage_font
        )

        painter.drawText(
            QRectF(
                20,
                37,
                self.width() - 40,
                34,
            ),
            Qt.AlignmentFlag.AlignCenter,
            f"{self._value}%",
        )

        # Phase label.
        painter.setPen(
            QColor(TEXT_SECONDARY)
        )

        phase_font = QFont(
            "Segoe UI",
            8,
            QFont.Weight.DemiBold,
        )

        painter.setFont(
            phase_font
        )

        painter.drawText(
            QRectF(
                16,
                72,
                self.width() - 32,
                24,
            ),
            Qt.AlignmentFlag.AlignCenter,
            self._status,
        )


# =========================================================
# Dashboard Widget
# =========================================================

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

        self._progress_phase = "Ready"

        self._build_ui()

        self.set_ready_state(False)

    # =====================================================
    # UI
    # =====================================================

    def _build_ui(self):
        self.setObjectName(
            "dashboardCard"
        )

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

        layout.setContentsMargins(
            18,
            16,
            18,
            16,
        )

        layout.setSpacing(10)

        # -------------------------------------------------
        # Title
        # -------------------------------------------------

        title = QLabel(
            "Firmware Update"
        )

        title.setStyleSheet(
            f"""
            color: {TEXT};
            font-size: 14pt;
            font-weight: 600;
            border: none;
            """
        )

        layout.addWidget(title)

        # -------------------------------------------------
        # Firmware selector
        # -------------------------------------------------

        firmware_header = UB3SectionHeader(
            "Firmware Selection",
            "Select the firmware package to program onto the connected UB3.",
        )

        layout.addWidget(
            firmware_header
        )

        self.firmware_combo = UB3ComboBox()

        self.firmware_combo.setObjectName(
            "firmwareCombo"
        )
        self.firmware_combo.setMinimumHeight(
            42
        )

        self.firmware_combo.currentIndexChanged.connect(
            self._firmware_index_changed
        )

        layout.addWidget(
            self.firmware_combo
        )

        self.firmware_details_card = UB3Card(
            object_name="firmwareDetailsCard"
        )

        details_layout = QVBoxLayout(
            self.firmware_details_card
        )

        details_layout.setContentsMargins(
            12,
            10,
            12,
            10,
        )

        details_layout.setSpacing(6)

        details_header = QHBoxLayout()
        details_header.setSpacing(8)

        details_title = QLabel(
            "Firmware Details"
        )

        details_title.setStyleSheet(
            f"""
            color: {TEXT};
            font-weight: 700;
            border: none;
            """
        )

        details_header.addWidget(
            details_title
        )

        details_header.addStretch()

        self.firmware_validation_badge = UB3StatusBadge(
            "Not selected",
            "neutral",
        )

        self.firmware_validation_badge.setObjectName(
            "firmwareValidationBadge"
        )

        details_header.addWidget(
            self.firmware_validation_badge
        )

        details_layout.addLayout(
            details_header
        )

        self.firmware_info = QLabel(
            "No firmware selected"
        )

        self.firmware_info.setWordWrap(
            True
        )

        self.firmware_info.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        self.firmware_info.setStyleSheet(
            f"""
            color: {TEXT_SECONDARY};
            border: none;
            padding: 4px;
            """
        )

        details_layout.addWidget(
            self.firmware_info
        )

        layout.addWidget(
            self.firmware_details_card
        )

        # -------------------------------------------------
        # Progress card
        # -------------------------------------------------

        self.progress_card = QFrame()

        self.progress_card.setObjectName(
            "progressCard"
        )

        self.progress_card.setVisible(
            False
        )

        self.progress_card.setStyleSheet(
            f"""
            QFrame#progressCard {{
                background: {INFO_BACKGROUND};
                border: 1px solid #BFDBFE;
                border-radius: 8px;
            }}
            """
        )

        progress_layout = QVBoxLayout(
            self.progress_card
        )

        progress_layout.setContentsMargins(
            14,
            12,
            14,
            12,
        )

        progress_layout.setSpacing(8)

        progress_header = QHBoxLayout()
        progress_header.setSpacing(8)

        self.progress_title = QLabel(
            "Update Progress"
        )

        self.progress_title.setStyleSheet(
            f"""
            color: {TEXT};
            font-size: 11pt;
            font-weight: 700;
            border: none;
            """
        )

        progress_header.addWidget(
            self.progress_title
        )

        progress_header.addStretch()

        self.progress_phase_label = QLabel(
            "Ready"
        )

        self.progress_phase_label.setStyleSheet(
            f"""
            color: {PRIMARY_DARK};
            font-weight: 600;
            border: none;
            """
        )

        progress_header.addWidget(
            self.progress_phase_label
        )

        progress_layout.addLayout(
            progress_header
        )

        # -------------------------------------------------
        # Upload workflow phases
        #
        # These are workflow states, not byte-level progress.
        # The Maple runtime does not expose trustworthy byte
        # percentages, so the UI deliberately presents the
        # operator with verified process phases.
        # -------------------------------------------------

        self.progress_steps = {}

        phases_layout = QHBoxLayout()
        phases_layout.setContentsMargins(2, 0, 2, 0)
        phases_layout.setSpacing(4)

        for phase_name in (
            "Prepare",
            "Start",
            "Upload",
            "Reconnect",
            "Complete",
        ):
            phase_label = QLabel(phase_name)
            phase_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            phase_label.setMinimumHeight(26)
            phase_label.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed,
            )
            self.progress_steps[phase_name] = phase_label
            phases_layout.addWidget(phase_label)

        progress_layout.addLayout(phases_layout)

        progress_center = QHBoxLayout()
        progress_center.addStretch()

        self.circular_progress = (
            CircularProgressWidget()
        )

        progress_center.addWidget(
            self.circular_progress
        )

        progress_center.addStretch()

        progress_layout.addLayout(
            progress_center
        )

        self.progress_bar = QProgressBar()

        self.progress_bar.setObjectName(
            "firmwareProgressBar"
        )

        self.progress_bar.setRange(
            0,
            100,
        )

        self.progress_bar.setValue(
            0
        )

        self.progress_bar.setTextVisible(
            False
        )

        self.progress_bar.setMinimumHeight(
            12
        )

        progress_layout.addWidget(
            self.progress_bar
        )

        self.progress_message = QLabel(
            "Waiting to start..."
        )

        self.progress_message.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.progress_message.setWordWrap(
            True
        )

        self.progress_message.setStyleSheet(
            f"""
            color: {TEXT_SECONDARY};
            border: none;
            font-weight: 600;
            """
        )

        progress_layout.addWidget(
            self.progress_message
        )

        self.progress_hint = QLabel(
            "Progress represents update workflow phases, "
            "not transferred bytes."
        )

        self.progress_hint.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.progress_hint.setWordWrap(
            True
        )

        self.progress_hint.setStyleSheet(
            f"""
            color: {TEXT_SECONDARY};
            border: none;
            font-size: 8pt;
            """
        )

        progress_layout.addWidget(
            self.progress_hint
        )

        self._update_progress_steps(
            "Ready"
        )

        layout.addWidget(
            self.progress_card
        )

        # -------------------------------------------------
        # Status
        # -------------------------------------------------

        self.status_label = QLabel(
            "Waiting for UB3"
        )

        self.status_label.setStyleSheet(
            f"""
            color: {TEXT_SECONDARY};
            font-weight: 600;
            border: none;
            """
        )

        layout.addWidget(
            self.status_label
        )

        # -------------------------------------------------
        # Result Banner
        # -------------------------------------------------

        self.result_banner = UB3StatusBanner(
            "",
            "info",
        )

        self.result_banner.setObjectName(
            "updateResultBanner"
        )

        self.result_banner.setVisible(
            False
        )

        layout.addWidget(
            self.result_banner
        )

        # -------------------------------------------------
        # Message
        # -------------------------------------------------

        self.message_label = QLabel(
            ""
        )

        self.message_label.setWordWrap(
            True
        )

        self.message_label.setMinimumHeight(
            38
        )

        self.message_label.setStyleSheet(
            f"""
            color: {TEXT_SECONDARY};
            border: none;
            """
        )

        layout.addWidget(
            self.message_label
        )

        # -------------------------------------------------
        # Diagnostics summary
        # -------------------------------------------------

        self.diagnostics_card = UB3Card(
            object_name="uploadDiagnosticsCard"
        )

        diagnostics_layout = QVBoxLayout(
            self.diagnostics_card
        )
        diagnostics_layout.setContentsMargins(
            12, 10, 12, 10
        )
        diagnostics_layout.setSpacing(8)

        diagnostics_header = QHBoxLayout()
        diagnostics_title = QLabel("Upload Diagnostics")
        diagnostics_title.setStyleSheet(
            f"font-weight: 700; color: {TEXT}; border: none;"
        )
        diagnostics_header.addWidget(diagnostics_title)
        diagnostics_header.addStretch()

        self.diagnostics_badge = UB3StatusBadge(
            "No completed upload",
            "neutral",
        )
        self.diagnostics_badge.setObjectName(
            "uploadDiagnosticsBadge"
        )
        diagnostics_header.addWidget(self.diagnostics_badge)
        diagnostics_layout.addLayout(diagnostics_header)

        diagnostics_grid = QGridLayout()
        diagnostics_grid.setHorizontalSpacing(18)
        diagnostics_grid.setVerticalSpacing(6)

        self.diagnostic_values = {}
        diagnostic_fields = (
            ("Firmware", "firmware"),
            ("Version", "version"),
            ("COM Port", "com_port"),
            ("Device State", "device_state"),
            ("Duration", "duration"),
            ("Return Code", "return_code"),
        )

        for index, (caption, key) in enumerate(diagnostic_fields):
            row = index // 3
            column = (index % 3) * 2

            caption_label = QLabel(caption)
            caption_label.setStyleSheet(
                f"color: {TEXT_SECONDARY}; font-size: 8pt; border: none;"
            )

            value_label = QLabel("Not available")
            value_label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            value_label.setStyleSheet(
                f"color: {TEXT}; font-weight: 600; border: none;"
            )

            diagnostics_grid.addWidget(caption_label, row, column)
            diagnostics_grid.addWidget(value_label, row, column + 1)
            self.diagnostic_values[key] = value_label

        diagnostics_layout.addLayout(diagnostics_grid)
        layout.addWidget(self.diagnostics_card)

        # -------------------------------------------------
        # Technical log
        # -------------------------------------------------

        log_header = QHBoxLayout()
        log_title = QLabel("Technical Upload Log")
        log_title.setStyleSheet(
            f"font-weight: 600; color: {TEXT}; border: none;"
        )
        log_header.addWidget(log_title)
        log_header.addStretch()

        self.copy_log_button = UB3Button(
            "Copy", variant="secondary"
        )
        self.copy_log_button.setObjectName("copyLogButton")
        self.copy_log_button.setMinimumHeight(32)
        self.copy_log_button.clicked.connect(self.copy_log)
        log_header.addWidget(self.copy_log_button)

        self.clear_log_button = UB3Button(
            "Clear", variant="secondary"
        )
        self.clear_log_button.setObjectName("clearLogButton")
        self.clear_log_button.setMinimumHeight(32)
        self.clear_log_button.clicked.connect(self.clear_output)
        log_header.addWidget(self.clear_log_button)

        self.save_log_button = UB3Button(
            "Save", variant="secondary"
        )
        self.save_log_button.setObjectName("saveLogButton")
        self.save_log_button.setMinimumHeight(32)
        self.save_log_button.clicked.connect(self.save_log)
        log_header.addWidget(self.save_log_button)

        layout.addLayout(log_header)

        self.output = QPlainTextEdit()

        self.output.setObjectName(
            "uploadOutput"
        )

        self.output.setReadOnly(
            True
        )

        self.output.setMinimumHeight(140)

        self.output.setPlaceholderText(
            "Technical upload messages will appear here."
        )

        layout.addWidget(
            self.output
        )

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        buttons = QHBoxLayout()

        buttons.addStretch()

        self.cancel_button = UB3Button(
            "Cancel",
            variant="secondary",
        )

        self.cancel_button.setObjectName(
            "cancelButton"
        )

        self.cancel_button.setEnabled(
            False
        )

        self.cancel_button.clicked.connect(
            self.cancel_requested.emit
        )

        buttons.addWidget(
            self.cancel_button
        )

        self.update_button = UB3Button(
            "UPDATE",
            variant="primary",
        )

        self.update_button.setObjectName(
            "updateButton"
        )

        self.update_button.setMinimumWidth(
            130
        )

        self.update_button.clicked.connect(
            self.update_requested.emit
        )

        buttons.addWidget(
            self.update_button
        )

        layout.addLayout(
            buttons
        )

    # =====================================================
    # Firmware
    # =====================================================

    def set_firmwares(
        self,
        firmwares: list[Firmware],
        selected: Firmware | None = None,
    ):
        self._firmwares = list(
            firmwares
        )

        previous_path = (
            selected.path
            if selected is not None
            else ""
        )

        self.firmware_combo.blockSignals(
            True
        )

        self.firmware_combo.clear()

        for firmware in self._firmwares:

            label = (
                f"{firmware.name} — "
                f"Version {firmware.version}"
                if firmware.name
                and firmware.version
                else firmware.display_name
            )

            self.firmware_combo.addItem(
                label,
                firmware,
            )

        if selected is not None:

            for index, firmware in enumerate(
                self._firmwares
            ):

                if firmware.path == previous_path:

                    self.firmware_combo.setCurrentIndex(
                        index
                    )

                    break

        self.firmware_combo.blockSignals(
            False
        )

        self._update_firmware_info()

    def _firmware_index_changed(
        self,
        index: int,
    ):

        self._update_firmware_info()

        if (
            index < 0
            or index >= len(self._firmwares)
        ):

            self.firmware_changed.emit(
                None
            )

            return

        self.firmware_changed.emit(
            self._firmwares[index]
        )

    def _update_firmware_info(self):
        """
        Display complete operator-facing firmware information.
        """

        index = (
            self.firmware_combo.currentIndex()
        )

        if (
            index < 0
            or index >= len(self._firmwares)
        ):

            self.firmware_info.setText(
                "No firmware selected"
            )

            self.firmware_validation_badge.setText(
                "Not selected"
            )
            self.firmware_validation_badge.set_status(
                "neutral"
            )

            return

        firmware = (
            self._firmwares[index]
        )

        name = (
            firmware.name
            or "Unknown"
        )

        version = (
            firmware.version
            or "Unknown"
        )

        target = (
            firmware.target_device
            or firmware.hardware
            or "UB3"
        )

        file_name = (
            firmware.filename
            or "--"
        )

        size = (
            f"{firmware.size_mb:.2f} MB"
            if firmware.size > 0
            else "--"
        )

        release_date = (
            firmware.release_date
            or "--"
        )

        file_valid = firmware.is_valid_file()

        file_status = (
            "File OK"
            if file_valid
            else "File validation required"
        )

        if file_valid:
            self.firmware_validation_badge.setText(
                "Validated"
            )
            self.firmware_validation_badge.set_status(
                "success"
            )
        else:
            self.firmware_validation_badge.setText(
                "Validation required"
            )
            self.firmware_validation_badge.set_status(
                "warning"
            )

        checksum_status = (
            f"{firmware.checksum_algorithm}: configured"
            if firmware.checksum
            else "Checksum: not configured"
        )

        lines = [
            f"<b>{name}</b>",
            f"Version: <b>{version}</b>",
            f"Target Device: {target}",
            f"Release Date: {release_date}",
            f"File: {file_name}",
            f"Size: {size}",
            f"Status: {file_status}",
            checksum_status,
        ]

        if firmware.description:

            lines.append(
                f"Description: "
                f"{firmware.description}"
            )

        self.firmware_info.setText(
            "<br>".join(lines)
        )

    def selected_firmware(
        self,
    ) -> Firmware | None:

        index = (
            self.firmware_combo.currentIndex()
        )

        if (
            index < 0
            or index >= len(self._firmwares)
        ):

            return None

        return self._firmwares[index]

    # =====================================================
    # Ready State
    # =====================================================

    def set_ready_state(
        self,
        can_update: bool,
    ):

        self.update_button.setEnabled(
            bool(can_update)
        )

        self.cancel_button.setEnabled(
            False
        )

        self.progress_card.setVisible(
            False
        )

        self._set_progress(
            0,
            "Ready",
            "Waiting to start...",
        )

        if not can_update:

            self.status_label.setText(
                "Waiting for UB3"
            )

    # =====================================================
    # Controller State
    # =====================================================

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
            or state_value
            == "Uploading Firmware"
        )

        if uploading:

            # A new upload supersedes the previous terminal result.
            self.result_banner.setVisible(False)

            self._show_progress()

            # STARTING/initial controller state.
            self._set_progress(
                10,
                "Preparing",
                message or "Preparing firmware update...",
            )

            self.update_button.setEnabled(
                False
            )

            self.cancel_button.setEnabled(
                True
            )

        else:

            self.cancel_button.setEnabled(
                False
            )

            self.update_button.setEnabled(
                bool(can_update)
            )

        self._set_status_style(
            state_value
        )

    # =====================================================
    # Live Progress
    # =====================================================

    def update_progress(
        self,
        message: str,
    ) -> None:
        """
        Update the visual progress indicator from a controller
        progress/status message.

        The percentage is a workflow-phase indicator, never a
        fabricated byte-transfer percentage.
        """

        text = str(
            message
            or ""
        ).strip()

        if not text:
            return

        self._show_progress()

        lower = text.lower()

        if (
            "preparing" in lower
            or "validation" in lower
        ):

            value = 10
            phase = "Preparing"

        elif (
            "starting firmware" in lower
            or "maple loader started" in lower
            or "starting upload" in lower
        ):

            value = 25
            phase = "Starting"

        elif (
            "uploading" in lower
            or "downloading" in lower
            or "opening com" in lower
            or "transferring" in lower
        ):

            value = 60
            phase = "Uploading"

        elif (
            "re-enumerat" in lower
            or "reconnected" in lower
            or "maple serial" in lower
            or "resetting usb" in lower
            or "usb reset" in lower
            or "returned to" in lower
        ):

            value = 92
            phase = "Reconnecting"

        elif (
            "completed successfully" in lower
            or "transfer completed" in lower
        ):

            value = 85
            phase = "Finalizing"

        else:

            # A live diagnostic line does not prove a new
            # percentage. Keep the current phase.
            value = self.circular_progress.value()
            phase = self._progress_phase

        self._set_progress(
            value,
            phase,
            text,
        )

    def _show_progress(self):
        self.progress_card.setVisible(
            True
        )

        self.progress_bar.setRange(
            0,
            100,
        )

    def _update_progress_steps(
        self,
        phase: str,
    ) -> None:
        """
        Update the visual upload workflow phases.

        This is deliberately presentation-only. A phase becomes
        active only when an existing controller/Maple message
        indicates that phase has been reached.
        """

        phase_order = {
            "Ready": 0,
            "Preparing": 1,
            "Starting": 2,
            "Uploading": 3,
            "Reconnecting": 4,
            "Finalizing": 4,
            "Complete": 5,
            "Failed": -1,
            "Warning": 5,
        }

        current = phase_order.get(
            phase,
            0,
        )

        for name, label in self.progress_steps.items():
            index = {
                "Prepare": 1,
                "Start": 2,
                "Upload": 3,
                "Reconnect": 4,
                "Complete": 5,
            }[name]

            if current == -1:
                active = False
                completed = False
            else:
                completed = index < current
                active = index == current

            if completed:
                label.setText(f"✓ {name}")
                label.setStyleSheet(
                    f"""
                    QLabel {{
                        color: {SUCCESS};
                        background: {SUCCESS_BACKGROUND};
                        border: none;
                        border-radius: 5px;
                        padding: 5px 4px;
                        font-size: 8pt;
                        font-weight: 700;
                    }}
                    """
                )
            elif active:
                label.setText(name)
                label.setStyleSheet(
                    f"""
                    QLabel {{
                        color: {PRIMARY_DARK};
                        background: #DBEAFE;
                        border: 1px solid #93C5FD;
                        border-radius: 5px;
                        padding: 5px 4px;
                        font-size: 8pt;
                        font-weight: 700;
                    }}
                    """
                )
            else:
                label.setText(name)
                label.setStyleSheet(
                    f"""
                    QLabel {{
                        color: {TEXT_SECONDARY};
                        background: #F3F4F6;
                        border: none;
                        border-radius: 5px;
                        padding: 5px 4px;
                        font-size: 8pt;
                        font-weight: 600;
                    }}
                    """
                )

    # =====================================================
    # Set Progress
    # =====================================================

    def _set_progress(
        self,
        value: int,
        phase: str,
        message: str,
    ):

        self._progress_phase = phase

        self._update_progress_steps(
            phase
        )

        self.progress_bar.setValue(
            max(0, min(100, int(value)))
        )

        self.circular_progress.set_value(
            value,
            phase,
        )

        self.progress_phase_label.setText(
            phase
        )

        self.progress_message.setText(
            message
        )

    def _complete_progress(
        self,
        *,
        success: bool,
        warning: bool = False,
        message: str = "",
    ):

        if success:

            self._show_progress()

            self._set_progress(
                100,
                "Complete",
                message
                or "Firmware update completed.",
            )

            self.progress_card.setStyleSheet(
                f"""
                QFrame#progressCard {{
                    background: {SUCCESS_BACKGROUND};
                    border: 1px solid #A7F3D0;
                    border-radius: 8px;
                }}
                """
            )

            self.progress_bar.setStyleSheet(
                f"""
                QProgressBar {{
                    background: #D1FAE5;
                    border: none;
                    border-radius: 6px;
                    height: 12px;
                }}

                QProgressBar::chunk {{
                    background: {WARNING if warning else SUCCESS};
                    border-radius: 6px;
                }}
                """
            )

        else:

            # Keep the progress card visible after a failed/cancelled
            # update so the operator can immediately see the final
            # workflow state and review the associated log output.
            # Hiding the card would remove the most important diagnostic
            # context at the exact point an operator needs it.
            self._show_progress()

            current_value = self.circular_progress.value()

            if current_value >= 100:
                current_value = 85

            self._set_progress(
                current_value,
                "Failed" if not warning else "Warning",
                message
                or (
                    "Firmware update failed."
                    if not warning
                    else "Firmware update completed with a warning."
                ),
            )

            if warning:
                card_background = WARNING_BACKGROUND
                border_color = "#FCD34D"
                progress_background = "#FEF3C7"
                progress_color = WARNING
            else:
                card_background = "#FEF2F2"
                border_color = "#FECACA"
                progress_background = "#FEE2E2"
                progress_color = ERROR

            self.progress_card.setStyleSheet(
                f"""
                QFrame#progressCard {{
                    background: {card_background};
                    border: 1px solid {border_color};
                    border-radius: 8px;
                }}
                """
            )

            self.progress_bar.setStyleSheet(
                f"""
                QProgressBar {{
                    background: {progress_background};
                    border: none;
                    border-radius: 6px;
                    height: 12px;
                }}

                QProgressBar::chunk {{
                    background: {progress_color};
                    border-radius: 6px;
                }}
                """
            )

    # =====================================================
    # Output
    # =====================================================

    def append_output(
        self,
        text: str,
    ):

        if not text:
            return

        self.output.appendPlainText(
            text.rstrip()
        )

        scrollbar = (
            self.output.verticalScrollBar()
        )

        scrollbar.setValue(
            scrollbar.maximum()
        )

    def clear_output(self):
        """Clear only the visible technical log; application file logs are preserved."""
        self.output.clear()

    def copy_log(self):
        """Copy the visible technical upload log to the system clipboard."""
        QApplication.clipboard().setText(
            self.output.toPlainText()
        )

    def save_log(self):
        """Save the visible technical upload log without altering the application log."""
        text = self.output.toPlainText()
        if not text:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Upload Log",
            "ub3_upload.log",
            "Log files (*.log);;Text files (*.txt);;All files (*)",
        )

        if not file_path:
            return

        Path(file_path).write_text(
            text,
            encoding="utf-8",
        )

    def _set_diagnostic_value(self, key: str, value: str) -> None:
        label = self.diagnostic_values.get(key)
        if label is not None:
            label.setText(value or "Not available")

    def _update_diagnostics(self, result: UploadResult) -> None:
        self.diagnostics_badge.setText(result.display_status)

        if result.success and result.has_warning:
            badge_status = "warning"
        elif result.success:
            badge_status = "success"
        elif result.cancelled:
            badge_status = "neutral"
        else:
            badge_status = "error"

        self.diagnostics_badge.set_status(badge_status)

        self._set_diagnostic_value("firmware", result.firmware_name)
        self._set_diagnostic_value("version", result.firmware_version)
        self._set_diagnostic_value("com_port", result.com_port)
        self._set_diagnostic_value("device_state", result.device_state)

        duration = (
            f"{result.duration_seconds:.2f} s"
            if result.duration_seconds
            else "Not available"
        )
        self._set_diagnostic_value("duration", duration)

        return_code = (
            str(result.return_code)
            if result.return_code is not None
            else "Not available"
        )
        self._set_diagnostic_value("return_code", return_code)

    # =====================================================
    # Result Presentation
    # =====================================================

    def _show_result_banner(
        self,
        status: str,
        message: str,
    ) -> None:
        """Present the terminal upload outcome without changing upload logic."""
        self.result_banner.set_status(status)
        self.result_banner.set_message(message)
        self.result_banner.setVisible(True)

    # =====================================================
    # Result
    # =====================================================

    def show_result(
        self,
        result: UploadResult,
        can_update: bool,
    ):

        self._update_diagnostics(result)

        self.message_label.setText(
            result.display_message
        )

        if (
            result.success
            and result.has_warning
        ):

            self.status_label.setText(
                "Success With Warning"
            )

            self._set_status_style(
                "Success With Warning"
            )

            self._complete_progress(
                success=True,
                warning=True,
                message=(
                    "Firmware programming completed "
                    "with a warning."
                ),
            )

            self._show_result_banner(
                "warning",
                "Firmware updated, but a post-upload warning requires attention.",
            )

        elif result.success:

            self.status_label.setText(
                "Firmware Updated Successfully"
            )

            self._set_status_style(
                "Success"
            )

            self._complete_progress(
                success=True,
                message=(
                    "Firmware programming completed "
                    "successfully."
                ),
            )

            self._show_result_banner(
                "success",
                "Firmware updated successfully. UB3 completed the update workflow.",
            )

        elif result.cancelled:

            self.status_label.setText(
                "Update Cancelled"
            )

            self._set_status_style(
                "Cancelled"
            )

            self._complete_progress(
                success=False
            )

            self._show_result_banner(
                "info",
                "Firmware update was cancelled. No further action was taken.",
            )

        else:

            self.status_label.setText(
                "Update Failed"
            )

            self._set_status_style(
                "Failed"
            )

            self._complete_progress(
                success=False
            )

            self._show_result_banner(
                "error",
                "Firmware update failed. Review the upload log for details.",
            )

        self.cancel_button.setEnabled(
            False
        )

        self.update_button.setEnabled(
            bool(can_update)
        )

        if result.stdout:

            self.append_output(
                result.stdout
            )

        if result.stderr:

            self.append_output(
                "[ERROR]\n"
                + result.stderr
            )

        if result.warning:

            self.append_output(
                "[WARNING]\n"
                + result.warning
            )

        if result.error:

            self.append_output(
                "[ERROR]\n"
                + result.error
            )

    # =====================================================
    # Status Style
    # =====================================================

    def _set_status_style(
        self,
        state_value: str,
    ):

        value = (
            state_value.lower()
        )

        if "warning" in value:

            color = WARNING
            background = WARNING_BACKGROUND

        elif "success" in value:

            color = SUCCESS
            background = SUCCESS_BACKGROUND

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
