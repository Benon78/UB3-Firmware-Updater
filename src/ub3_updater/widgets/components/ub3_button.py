"""Reusable UB3 button component.

Presentation-only. It does not own application actions or controller logic.
"""
from PySide6.QtWidgets import QPushButton

from ub3_updater.themes.design_system import (
    DANGER_BUTTON_STYLE,
    ICON_BUTTON_STYLE,
    PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE,
    SUCCESS_BUTTON_STYLE,
)

_STYLES = {
    "primary": PRIMARY_BUTTON_STYLE,
    "secondary": SECONDARY_BUTTON_STYLE,
    "success": SUCCESS_BUTTON_STYLE,
    "danger": DANGER_BUTTON_STYLE,
    "icon": ICON_BUTTON_STYLE,
}


class UB3Button(QPushButton):
    """A standardized UB3 action button.

    The component only standardizes presentation. Callers retain ownership
    of signals, slots, object names, enabled state, and business behavior.
    """

    def __init__(self, text="", variant="primary", parent=None):
        super().__init__(text, parent)
        self.setObjectName("ub3Button")
        self.set_variant(variant)

    def set_variant(self, variant: str) -> None:
        key = str(variant).strip().lower()
        if key not in _STYLES:
            raise ValueError(
                f"Unknown UB3 button variant: {variant!r}. "
                f"Expected one of: {', '.join(_STYLES)}"
            )
        self._variant = key
        self.setStyleSheet(_STYLES[key])

    def variant(self) -> str:
        return self._variant
