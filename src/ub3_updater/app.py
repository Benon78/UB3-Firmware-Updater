"""
=========================================================
UB3 Firmware Updater

Application Bootstrap

Developer:
Benjamin William

Version:
0.1.0
=========================================================
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
)
from PySide6.QtCore import Qt


APP_NAME = "UB3 Firmware Updater"
APP_VERSION = "0.1.0"


class UB3UpdaterApp(QMainWindow):
    """
    Main application window.
    This class will later host the entire GUI.
    """

    def __init__(self):
        super().__init__()

        self.initialize_window()

    def initialize_window(self):

        self.setWindowTitle(f"{APP_NAME}   v{APP_VERSION}")

        self.resize(1280, 800)

        self.setMinimumSize(1100, 700)

        label = QLabel("UB3 Firmware Updater\n\nStage 1 Completed")

        label.setAlignment(Qt.AlignCenter)

        label.setStyleSheet("""
            font-size:28px;
            font-weight:bold;
        """)

        self.setCentralWidget(label)