"""
=========================================================
UB3 Firmware Updater

Entry Point

Developer:
Benjamin William

Version:
0.1.0

=========================================================
"""

import sys

from PySide6.QtWidgets import QApplication

from ub3_updater.app import UB3UpdaterApp


def main():

    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)

    window = UB3UpdaterApp()

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()