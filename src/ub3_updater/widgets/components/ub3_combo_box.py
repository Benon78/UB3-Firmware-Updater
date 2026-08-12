"""Reusable UB3 combo-box component."""
from PySide6.QtWidgets import QComboBox

from ub3_updater.themes.design_system import COMBO_BOX_STYLE


class UB3ComboBox(QComboBox):
    """Standard UB3 selection control; contains no selection business logic."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ub3ComboBox")
        self.setStyleSheet(COMBO_BOX_STYLE)
        self.setMinimumHeight(40)
