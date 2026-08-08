"""
=========================================================
UB3 Firmware Updater

Footer Widget

Developer:
Benjamin William
=========================================================
"""

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
)

from PySide6.QtCore import Qt

from ub3_updater.themes.light_theme import (
    BORDER,
    TEXT_SECONDARY,
)


class FooterWidget(QWidget):
    """
    Application footer displayed on every page.
    """

    def __init__(self):
        super().__init__()

        self.build_ui()

    def build_ui(self):

        self.setFixedHeight(35)

        self.setStyleSheet(f"""
            QWidget {{
                border-top:1px solid {BORDER};
                background:white;
            }}
        """)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(10,5,10,5)

        # -------------------------------------

        self.version_label = QLabel("Version 0.1.0-dev")

        self.version_label.setStyleSheet(f"""
            color:{TEXT_SECONDARY};
        """)

        layout.addWidget(self.version_label)

        # -------------------------------------

        layout.addStretch()

        # -------------------------------------

        self.status_label = QLabel("Ready")

        self.status_label.setAlignment(Qt.AlignCenter)

        self.status_label.setStyleSheet(f"""
            color:{TEXT_SECONDARY};
        """)

        layout.addWidget(self.status_label)

        # -------------------------------------

        layout.addStretch()

        # -------------------------------------

        self.mode_label = QLabel("Offline Mode")

        self.mode_label.setStyleSheet(f"""
            color:{TEXT_SECONDARY};
        """)

        layout.addWidget(self.mode_label)

    # =====================================================

    def update_status(
        self,
        version=None,
        mode=None,
        status=None,
    ):

        if version is not None:
            self.version_label.setText(version)

        if mode is not None:
            self.mode_label.setText(mode)

        if status is not None:
            self.status_label.setText(status)