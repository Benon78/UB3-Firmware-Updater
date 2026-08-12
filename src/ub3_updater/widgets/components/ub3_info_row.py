"""Reusable label/value information row."""
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel

from ub3_updater.themes.design_system import BORDER, TEXT, TEXT_SECONDARY


class UB3InfoRow(QFrame):
    """Presentation-only key/value row used by device and firmware cards."""

    def __init__(self, label="", value="Not reported", parent=None):
        super().__init__(parent)
        self.setObjectName("ub3InfoRow")
        self._label = QLabel(str(label))
        self._value = QLabel(str(value))
        self._value.setObjectName("ub3InfoRowValue")
        self._value.setTextInteractionFlags(
            self._value.textInteractionFlags()
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(12)
        layout.addWidget(self._label, 0)
        layout.addWidget(self._value, 1)

        self._label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-weight: 600; border: none;"
        )
        self._value.setStyleSheet(
            f"QLabel#ub3InfoRowValue {{ color: {TEXT}; background: #F9FAFB; "
            f"border: 1px solid {BORDER}; border-radius: 6px; padding: 6px 9px; }}"
        )

    def label(self) -> str:
        return self._label.text()

    def value(self) -> str:
        return self._value.text()

    def set_value(self, value) -> None:
        self._value.setText(str(value))
