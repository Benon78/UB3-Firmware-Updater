"""
=========================================================
UB3 Firmware Updater

Instruction Widget

Developer:
Benjamin William
=========================================================
"""

from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
)

from ub3_updater.themes.light_theme import (
    CARD,
    BORDER,
)


class InstructionWidget(QFrame):

    def __init__(self):

        super().__init__()

        self.build_ui()

    def build_ui(self):

        self.setStyleSheet(f"""
            QFrame{{
                background:{CARD};
                border:1px solid {BORDER};
                border-radius:8px;
            }}
        """)

        layout = QVBoxLayout(self)

        title = QLabel("Before connecting UB3")

        title.setStyleSheet("""
            font-size:13pt;
            font-weight:600;
        """)

        layout.addWidget(title)

        items = [

            "1. Connect the UB3 using a USB cable.",

            "2. Wait until Windows detects the Serial Port.",

            "3. Ensure the device battery is above 20%.",

            "4. Do not disconnect the cable during firmware update.",

            "5. Click Refresh if the device is not detected."

        ]

        for item in items:

            lbl = QLabel(item)

            lbl.setWordWrap(True)

            layout.addWidget(lbl)