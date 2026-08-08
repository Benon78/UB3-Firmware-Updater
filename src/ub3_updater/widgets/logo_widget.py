"""
=========================================================
UB3 Firmware Updater

Logo Widget

Developer:
Benjamin William
=========================================================
"""

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
)

from PySide6.QtCore import Qt

from ub3_updater.themes.light_theme import (
    PRIMARY,
    PRIMARY_DARK,
    TEXT,
    TEXT_SECONDARY,
)


class LogoWidget(QWidget):
    """
    Application logo and title widget.
    """

    def __init__(self):
        super().__init__()

        self.build_ui()

    def build_ui(self):

        layout = QHBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        # ----------------------------------------
        # Logo Box
        # ----------------------------------------

        logo = QFrame()

        logo.setFixedSize(90, 90)

        logo.setStyleSheet(f"""
            background:{PRIMARY_DARK};
            border-radius:18px;
        """)

        logo_layout = QVBoxLayout(logo)

        logo_layout.setContentsMargins(0, 0, 0, 0)

        logo_text = QLabel("UB3")

        logo_text.setAlignment(Qt.AlignCenter)

        logo_text.setStyleSheet("""
            color:white;
            font-size:26px;
            font-weight:700;
        """)

        logo_layout.addWidget(logo_text)

        # ----------------------------------------
        # Title Area
        # ----------------------------------------

        title_layout = QVBoxLayout()

        title_layout.setSpacing(4)

        title = QLabel("UB3 Firmware Updater Tool")

        title.setStyleSheet(f"""
            color:{TEXT};
            font-size:26px;
            font-weight:700;
        """)

        subtitle = QLabel("Offline • Simple • Reliable")

        subtitle.setStyleSheet(f"""
            color:{TEXT_SECONDARY};
            font-size:12pt;
        """)

        title_layout.addStretch()
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        title_layout.addStretch()

        layout.addWidget(logo)

        layout.addLayout(title_layout)

        layout.addStretch()