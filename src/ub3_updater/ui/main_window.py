"""
=========================================================
UB3 Firmware Updater

Main Window

Developer:
Benjamin William
=========================================================
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QSizePolicy,
)
from PySide6.QtCore import Qt

from ub3_updater.ui.home_page import HomePage


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("UB3 Firmware Updater Tool")

        self.resize(1100, 700)

        self.setMinimumSize(1000, 650)

        self.build_ui()

    def build_ui(self):

        central = QWidget()

        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.setSpacing(0)

        # =========================
        # Header
        # =========================

        header = QWidget()

        header.setFixedHeight(60)

        header_layout = QHBoxLayout(header)

        header_layout.setContentsMargins(20, 10, 20, 10)

        title = QLabel("UB3 Firmware Updater Tool")

        title.setStyleSheet("""
            font-size:22px;
            font-weight:600;
        """)

        header_layout.addWidget(title)

        header_layout.addStretch()

        status = QLabel("Offline Mode")

        status.setStyleSheet("""
            color:#6B7280;
            font-size:10pt;
        """)

        header_layout.addWidget(status)

        main_layout.addWidget(header)

        # =========================
        # Navigation
        # =========================

        navigation = QWidget()

        navigation.setFixedHeight(55)

        nav_layout = QHBoxLayout(navigation)

        nav_layout.setContentsMargins(15, 5, 15, 5)

        self.btn_home = QPushButton("Home")
        self.btn_device = QPushButton("Device")
        self.btn_firmware = QPushButton("Firmware")
        self.btn_upload = QPushButton("Upload")
        self.btn_logs = QPushButton("Logs")
        self.btn_settings = QPushButton("Settings")

        for btn in [
            self.btn_home,
            self.btn_device,
            self.btn_firmware,
            self.btn_upload,
            self.btn_logs,
            self.btn_settings,
        ]:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            nav_layout.addWidget(btn)

        main_layout.addWidget(navigation)

        # =========================
        # Pages
        # =========================

        self.pages = QStackedWidget()

        self.home_page = HomePage()

        self.pages.addWidget(self.home_page)

        main_layout.addWidget(self.pages)

        # =========================
        # Footer
        # =========================

        footer = QWidget()

        footer.setFixedHeight(30)

        footer_layout = QHBoxLayout(footer)

        footer_layout.setContentsMargins(10, 5, 10, 5)

        version = QLabel("v0.1.0-dev")

        footer_layout.addWidget(version)

        footer_layout.addStretch()

        mode = QLabel("Offline Firmware Tool")

        footer_layout.addWidget(mode)

        main_layout.addWidget(footer)