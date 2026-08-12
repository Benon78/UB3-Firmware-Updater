"""Reusable UB3 action-button styles for Step 6.1."""

from ub3_updater.themes.design_system import (
    PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE,
    SUCCESS_BUTTON_STYLE,
    DANGER_BUTTON_STYLE,
    ICON_BUTTON_STYLE,
)

UPDATE_BUTTON_STYLE = PRIMARY_BUTTON_STYLE.replace(
    "QPushButton {", "QPushButton#updateButton {", 1
)

CANCEL_BUTTON_STYLE = SECONDARY_BUTTON_STYLE.replace(
    "QPushButton {", "QPushButton#cancelButton {", 1
)

REFRESH_BUTTON_STYLE = SECONDARY_BUTTON_STYLE.replace(
    "QPushButton {", "QPushButton#refreshButton {", 1
)

SUCCESS_BUTTON_STYLE_NAMED = SUCCESS_BUTTON_STYLE
DANGER_BUTTON_STYLE_NAMED = DANGER_BUTTON_STYLE
ICON_BUTTON_STYLE_NAMED = ICON_BUTTON_STYLE
