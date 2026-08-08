"""
=========================================================
UB3 Firmware Updater

Base Page

Developer:
Benjamin William
=========================================================
"""

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
)

from PySide6.QtCore import Qt

from ub3_updater.themes.light_theme import (
    BACKGROUND,
    TEXT,
    TEXT_SECONDARY,
)


class BasePage(QWidget):
    """
    Base class for all application pages.

    Every page should inherit from this class.
    """

    def __init__(
        self,
        title: str = "",
        subtitle: str = ""
    ):
        super().__init__()

        self.title = title
        self.subtitle = subtitle

        self.build_ui()

    def build_ui(self):

        self.setStyleSheet(f"""
            QWidget {{
                background:{BACKGROUND};
            }}
        """)

        self.main_layout = QVBoxLayout(self)

        self.main_layout.setContentsMargins(35, 25, 35, 25)

        self.main_layout.setSpacing(20)

        # --------------------------------------

        if self.title:

            title_label = QLabel(self.title)

            title_label.setStyleSheet(f"""
                color:{TEXT};
                font-size:24px;
                font-weight:700;
            """)

            self.main_layout.addWidget(title_label)

        # --------------------------------------

        if self.subtitle:

            subtitle_label = QLabel(self.subtitle)

            subtitle_label.setWordWrap(True)

            subtitle_label.setStyleSheet(f"""
                color:{TEXT_SECONDARY};
                font-size:11pt;
            """)

            self.main_layout.addWidget(subtitle_label)

        # --------------------------------------

        self.content_layout = QVBoxLayout()

        self.content_layout.setSpacing(20)

        self.main_layout.addLayout(self.content_layout)

        self.main_layout.addStretch()

    # ======================================

    def add_widget(self, widget):
        """
        Add a widget to the page content area.
        """
        self.content_layout.addWidget(widget)

    # ======================================

    def add_layout(self, layout):
        """
        Add a layout to the page content area.
        """
        self.content_layout.addLayout(layout)