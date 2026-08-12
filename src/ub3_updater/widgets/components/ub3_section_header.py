"""Reusable UB3 section heading."""
from PySide6.QtWidgets import QLabel

from ub3_updater.themes.design_system import SECTION_SIZE, TEXT, TEXT_SECONDARY


class UB3SectionHeader(QLabel):
    """Standard title/subtitle presentation for a UI section."""

    def __init__(self, title="", subtitle="", parent=None):
        super().__init__(parent)
        self.setObjectName("ub3SectionHeader")
        self._subtitle = subtitle
        self.setText(title)
        self.setStyleSheet(
            f"QLabel#ub3SectionHeader {{ color: {TEXT}; font-size: {SECTION_SIZE}; "
            f"font-weight: 700; border: none; }}"
        )
        if subtitle:
            self.setToolTip(subtitle)
            self.setStatusTip(subtitle)

    def set_title(self, title: str) -> None:
        self.setText(title)
