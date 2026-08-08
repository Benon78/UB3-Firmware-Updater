"""
=========================================================
UB3 Device Manager

Application Entry Point

Developer:
Benjamin William

Version:
0.2.0
=========================================================
"""

import sys

from PySide6.QtWidgets import QApplication

from ub3_updater.themes.light_theme import STYLE
from ub3_updater.ui.main_window import MainWindow


def main() -> None:
    """Start the application."""

    app = QApplication(sys.argv)

    app.setStyleSheet(STYLE)

    window = MainWindow()

    window.show()

    sys.exit(app.exec())