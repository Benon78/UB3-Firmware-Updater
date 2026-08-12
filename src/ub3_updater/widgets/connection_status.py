"""
UB3 Firmware Updater - Connection Status Widget
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from ub3_updater.models.device import Device
from ub3_updater.widgets.action_button_style import REFRESH_BUTTON_STYLE
from ub3_updater.themes.light_theme import (
    CARD,
    BORDER,
    ERROR,
    SUCCESS,
    TEXT,
    TEXT_SECONDARY,
)


class ConnectionStatusWidget(QFrame):
    """
    Displays the currently detected UB3.

    This widget does not scan hardware itself. MainWindow/
    UpdateController owns device detection and calls
    update_device().
    """

    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("connectionStatusCard")

        self._build_ui()
        self.set_disconnected()

    def _build_ui(self):
        self.setStyleSheet(
            f"""
            QFrame#connectionStatusCard {{
                background: {CARD};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        title = QLabel("Connection Status")
        title.setStyleSheet(
            f"""
            color: {TEXT};
            font-size: 14pt;
            font-weight: 600;
            border: none;
            """
        )
        layout.addWidget(title)

        row = QHBoxLayout()
        row.setSpacing(8)

        self.status_dot = QLabel("●")
        self.status_dot.setFixedWidth(20)
        self.status_dot.setStyleSheet(
            f"color: {ERROR}; font-size: 16pt; border: none;"
        )
        row.addWidget(self.status_dot)

        self.status_label = QLabel()
        self.status_label.setStyleSheet(
            f"""
            color: {TEXT};
            font-size: 11pt;
            font-weight: 600;
            border: none;
            """
        )
        row.addWidget(self.status_label)
        row.addStretch()

        self.com_badge = QLabel("--")
        self.com_badge.setAlignment(Qt.AlignCenter)
        self.com_badge.setMinimumWidth(90)
        self.com_badge.setStyleSheet(
            f"""
            QLabel {{
                background: #F9FAFB;
                color: {TEXT};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 10px;
                font-weight: 600;
            }}
            """
        )
        row.addWidget(self.com_badge)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setToolTip("Refresh device detection")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.setStyleSheet(REFRESH_BUTTON_STYLE)
        self.refresh_button.setMinimumHeight(38)
        self.refresh_button.setMinimumWidth(90)
        self.refresh_button.clicked.connect(
            self.refresh_requested.emit
        )
        row.addWidget(self.refresh_button)

        layout.addLayout(row)

        self.device_label = QLabel()
        self.vid_pid_label = QLabel()
        self.mode_label = QLabel()

        for label in (
            self.device_label,
            self.vid_pid_label,
            self.mode_label,
        ):
            label.setStyleSheet(
                f"""
                color: {TEXT_SECONDARY};
                border: none;
                """
            )
            layout.addWidget(label)

    def set_disconnected(self):
        self.status_dot.setStyleSheet(
            f"color: {ERROR}; font-size: 16pt; border: none;"
        )
        self.status_label.setText("No Device Detected")
        self.com_badge.setText("--")
        self.device_label.setText("Device: --")
        self.vid_pid_label.setText("VID:PID: --")
        self.mode_label.setText("USB Mode: --")

    def update_device(self, device: Device | None):
        """
        Render the current Device model.
        """

        if device is None or not device.connected:
            self.set_disconnected()
            return

        self.status_dot.setStyleSheet(
            f"color: {SUCCESS}; font-size: 16pt; border: none;"
        )
        self.status_label.setText("UB3 Connected")

        self.com_badge.setText(
            device.com_port or "--"
        )

        self.device_label.setText(
            f"Device: {device.display_name}"
        )

        vid = device.vid or "--"
        pid = device.pid or "--"

        self.vid_pid_label.setText(
            f"VID:PID: {vid}:{pid}"
        )

        self.mode_label.setText(
            f"USB Mode: {device.state.value}"
        )

    # Backward-compatible API for existing callers.
    def set_status(
        self,
        connected,
        com_port="--",
        board="--",
        dfu_status="--",
        firmware="--",
    ):
        if not connected:
            self.set_disconnected()
            return

        self.status_dot.setStyleSheet(
            f"color: {SUCCESS}; font-size: 16pt; border: none;"
        )
        self.status_label.setText("UB3 Connected")
        self.com_badge.setText(com_port or "--")
        self.device_label.setText(
            f"Device: {board or '--'}"
        )
        self.vid_pid_label.setText(
            f"DFU: {dfu_status or '--'}"
        )
        self.mode_label.setText(
            f"Firmware: {firmware or '--'}"
        )
