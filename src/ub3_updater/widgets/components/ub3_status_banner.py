"""Reusable semantic status banner."""
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel

from ub3_updater.themes.design_system import (
    ERROR,
    ERROR_BACKGROUND,
    ERROR_BORDER,
    INFO_BACKGROUND,
    INFO_BORDER,
    PRIMARY_DARK,
    SUCCESS,
    SUCCESS_BACKGROUND,
    SUCCESS_BORDER,
    TEXT,
    WARNING,
    WARNING_BACKGROUND,
    WARNING_BORDER,
)

_STYLES = {
    "info": (PRIMARY_DARK, INFO_BACKGROUND, INFO_BORDER),
    "success": (SUCCESS, SUCCESS_BACKGROUND, SUCCESS_BORDER),
    "warning": (WARNING, WARNING_BACKGROUND, WARNING_BORDER),
    "error": (ERROR, ERROR_BACKGROUND, ERROR_BORDER),
}


class UB3StatusBanner(QFrame):
    """Semantic message banner with presentation-only state."""

    def __init__(self, message="", status="info", parent=None):
        super().__init__(parent)
        self.setObjectName("ub3StatusBanner")
        self._label = QLabel(str(message))
        self._label.setWordWrap(True)
        self._label.setStyleSheet(
            f"color: {TEXT}; border: none; font-weight: 600;"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.addWidget(self._label)
        self.set_status(status)

    def set_status(self, status: str) -> None:
        key = str(status).strip().lower()
        if key not in _STYLES:
            raise ValueError(
                f"Unknown UB3 banner status: {status!r}. "
                f"Expected one of: {', '.join(_STYLES)}"
            )
        foreground, background, border = _STYLES[key]
        self._status = key
        self.setStyleSheet(
            f"QFrame#ub3StatusBanner {{ background-color: {background}; "
            f"border: 1px solid {border}; border-radius: 8px; }}"
        )
        self._label.setStyleSheet(
            f"color: {foreground}; border: none; font-weight: 600;"
        )

    def set_message(self, message: str) -> None:
        self._label.setText(str(message))

    def message(self) -> str:
        return self._label.text()

    def status(self) -> str:
        return self._status
