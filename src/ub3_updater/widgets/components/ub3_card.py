"""Reusable UB3 card container."""
from PySide6.QtWidgets import QFrame

from ub3_updater.themes.design_system import CARD_STYLE


class UB3Card(QFrame):
    """Standard UB3 surface/card with no application behavior."""

    def __init__(self, parent=None, object_name="ub3Card"):
        super().__init__(parent)
        self.setObjectName(object_name)
        self.setStyleSheet(CARD_STYLE)
