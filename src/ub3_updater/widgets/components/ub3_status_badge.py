"""Reusable semantic status badge."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from ub3_updater.themes.design_system import (
    ERROR,
    ERROR_BACKGROUND,
    INFO_BACKGROUND,
    PRIMARY,
    STATUS_BADGE_STYLE,
    SUCCESS,
    SUCCESS_BACKGROUND,
    TEXT_SECONDARY,
    WARNING,
    WARNING_BACKGROUND,
)

_STATES = {
    "info": (PRIMARY, INFO_BACKGROUND),
    "success": (SUCCESS, SUCCESS_BACKGROUND),
    "warning": (WARNING, WARNING_BACKGROUND),
    "error": (ERROR, ERROR_BACKGROUND),
    "neutral": (TEXT_SECONDARY, "#F3F4F6"),
}


class UB3StatusBadge(QLabel):
    """Compact semantic status indicator."""

    def __init__(self, text="", status="neutral", parent=None):
        super().__init__(text, parent)
        self.setObjectName("ub3StatusBadge")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_status(status)

    def set_status(self, status: str) -> None:
        key = str(status).strip().lower()
        if key not in _STATES:
            raise ValueError(
                f"Unknown UB3 status: {status!r}. "
                f"Expected one of: {', '.join(_STATES)}"
            )
        foreground, background = _STATES[key]
        self._status = key
        self.setStyleSheet(
            STATUS_BADGE_STYLE
            + f"\nQLabel#ub3StatusBadge {{ color: {foreground}; background-color: {background}; }}"
        )

    def status(self) -> str:
        return self._status
