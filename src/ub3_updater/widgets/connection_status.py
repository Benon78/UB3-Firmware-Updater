"""
=========================================================
UB3 Firmware Updater

Connection Status Widget

Developer:
Benjamin William
=========================================================
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)

from PySide6.QtCore import Qt

from ub3_updater.themes.light_theme import (
    SUCCESS,
    ERROR,
    CARD,
    BORDER,
    TEXT,
    TEXT_SECONDARY,
)


class ConnectionStatusWidget(QFrame):

    def __init__(self):
        super().__init__()

        self.build_ui()

        self.set_disconnected()

    def build_ui(self):

        self.setStyleSheet(f"""
            QFrame {{
                background:{CARD};
                border:1px solid {BORDER};
                border-radius:8px;
            }}
        """)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(20,20,20,20)

        layout.setSpacing(15)

        # -----------------------------

        title = QLabel("Connection Status")

        title.setStyleSheet("""
            font-size:14pt;
            font-weight:600;
        """)

        layout.addWidget(title)

        # -----------------------------

        row = QHBoxLayout()

        self.status_dot = QLabel("●")

        self.status_dot.setStyleSheet(f"""
            color:{ERROR};
            font-size:18pt;
        """)

        row.addWidget(self.status_dot)

        self.status_label = QLabel()

        self.status_label.setStyleSheet("""
            font-size:12pt;
            font-weight:600;
        """)

        row.addWidget(self.status_label)

        row.addStretch()

        self.refresh_button = QPushButton("Refresh")

        self.refresh_button.setFixedWidth(120)

        row.addWidget(self.refresh_button)

        layout.addLayout(row)

        # -----------------------------

        self.com_label = QLabel()

        self.board_label = QLabel()

        self.dfu_label = QLabel()

        self.firmware_label = QLabel()

        for label in [
            self.com_label,
            self.board_label,
            self.dfu_label,
            self.firmware_label,
        ]:

            label.setStyleSheet(f"""
                color:{TEXT_SECONDARY};
                font-size:10pt;
            """)

            layout.addWidget(label)

    # ==========================================

    def set_disconnected(self):

        self.status_dot.setStyleSheet(f"""
            color:{ERROR};
            font-size:18pt;
        """)

        self.status_label.setText("No Device Connected")

        self.com_label.setText("COM Port : --")

        self.board_label.setText("Board : --")

        self.dfu_label.setText("DFU : Not Available")

        self.firmware_label.setText("Firmware : --")

    # ==========================================

    def set_status(
        self,
        connected,
        com_port="--",
        board="--",
        dfu_status="--",
        firmware="--",
    ):

        if connected:

            self.status_dot.setStyleSheet(f"""
                color:{SUCCESS};
                font-size:18pt;
            """)

            self.status_label.setText("UB3 Connected")

        else:

            self.set_disconnected()

            return

        self.com_label.setText(f"COM Port : {com_port}")

        self.board_label.setText(f"Board : {board}")

        self.dfu_label.setText(f"DFU : {dfu_status}")

        self.firmware_label.setText(f"Firmware : {firmware}")