"""
UB3 Firmware Updater - Firmware / Update Dashboard

Step 4.5:
Operator-focused live firmware update progress presentation.

The widget does not invent byte-level upload progress. Maple Loader's
current output does not provide a trustworthy numeric transfer percentage,
so the progress indicator represents verified workflow phases.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QFont
from PySide6.QtWidgets import (
    QFrame,
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
from ub3_updater.widgets.components import UB3Button, UB3ComboBox
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

        firmware_title = QLabel(
            "Selected Firmware"
        )

        firmware_title.setStyleSheet(
            f"""
            font-weight: 600;
            color: {TEXT};
            border: none;
            """
        )

        layout.addWidget(
            firmware_title
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

        self.firmware_info = QLabel(
            "No firmware selected"
        )

        self.firmware_info.setWordWrap(
            True
        )

        self.firmware_info.setStyleSheet(
            f"""
            color: {TEXT_SECONDARY};
            border: none;
            padding: 4px;
            """
        )

        layout.addWidget(
            self.firmware_info
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
        # Output
        # -------------------------------------------------

        output_title = QLabel(
            "Upload Log"
        )

        output_title.setStyleSheet(
            f"""
            font-weight: 600;
            color: {TEXT};
            border: none;
            """
        )

        layout.addWidget(
            output_title
        )

        self.output = QPlainTextEdit()

        self.output.setObjectName(
            "uploadOutput"
        )

        self.output.setReadOnly(
            True
        )

        self.output.setMinimumHeight(
            120
        )

        self.output.setPlaceholderText(
            "Upload messages will appear here."
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

        file_status = (
            "File OK"
            if firmware.is_valid_file()
            else "File validation required"
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

    def _set_progress(
        self,
        value: int,
        phase: str,
        message: str,
    ):

        self._progress_phase = phase

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
        self.output.clear()

    # =====================================================
    # Result
    # =====================================================

    def show_result(
        self,
        result: UploadResult,
        can_update: bool,
    ):

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
