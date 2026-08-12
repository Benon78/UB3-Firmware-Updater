"""
UB3 Firmware Updater - GUI Design System

Step 6.1 establishes reusable visual tokens and component styles.
This module contains presentation-only definitions. It must not
contain device, firmware, worker, or upload logic.
"""

# =========================================================
# Color tokens - approved UB3 palette
# =========================================================

PRIMARY = "#2563EB"
PRIMARY_DARK = "#1E3A8A"
PRIMARY_HOVER = "#1D4ED8"
PRIMARY_PRESSED = "#1E3A8A"

SUCCESS = "#10B981"
SUCCESS_DARK = "#059669"
WARNING = "#F59E0B"
WARNING_DARK = "#D97706"
ERROR = "#EF4444"
ERROR_DARK = "#DC2626"
NEUTRAL = "#6B7280"

BACKGROUND = "#F3F4F6"
SURFACE = "#FFFFFF"
SURFACE_SUBTLE = "#F9FAFB"
TEXT = "#111827"
TEXT_SECONDARY = "#6B7280"
BORDER = "#E5E7EB"
BORDER_STRONG = "#D1D5DB"

INFO_BACKGROUND = "#EFF6FF"
INFO_BORDER = "#BFDBFE"
SUCCESS_BACKGROUND = "#ECFDF5"
SUCCESS_BORDER = "#A7F3D0"
WARNING_BACKGROUND = "#FFFBEB"
WARNING_BORDER = "#FCD34D"
ERROR_BACKGROUND = "#FEF2F2"
ERROR_BORDER = "#FECACA"

# =========================================================
# Layout tokens
# =========================================================

SPACE_1 = 4
SPACE_2 = 8
SPACE_3 = 12
SPACE_4 = 16
SPACE_5 = 20
SPACE_6 = 24
SPACE_7 = 32

CARD_RADIUS = 10
BUTTON_RADIUS = 7
INPUT_RADIUS = 7
BADGE_RADIUS = 999

CONTROL_HEIGHT = 40
PRIMARY_BUTTON_HEIGHT = 44

FONT_FAMILY = "Segoe UI"
FONT_SIZE = "10pt"
TITLE_SIZE = "18pt"
SECTION_SIZE = "14pt"
BODY_SIZE = "10pt"
SMALL_SIZE = "8pt"

# =========================================================
# Reusable component styles
# =========================================================

PRIMARY_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {PRIMARY};
    color: #FFFFFF;
    border: 1px solid {PRIMARY_DARK};
    border-radius: {BUTTON_RADIUS}px;
    min-height: {PRIMARY_BUTTON_HEIGHT}px;
    padding: 0 18px;
    font-family: \"{FONT_FAMILY}\";
    font-size: {BODY_SIZE};
    font-weight: 700;
}}
QPushButton:hover {{
    background-color: {PRIMARY_HOVER};
    color: #FFFFFF;
}}
QPushButton:pressed {{
    background-color: {PRIMARY_PRESSED};
    color: #FFFFFF;
}}
QPushButton:disabled {{
    background-color: {BORDER_STRONG};
    color: {NEUTRAL};
    border-color: {BORDER_STRONG};
}}
"""

SECONDARY_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {SURFACE};
    color: {PRIMARY};
    border: 1px solid {PRIMARY};
    border-radius: {BUTTON_RADIUS}px;
    min-height: {CONTROL_HEIGHT}px;
    padding: 0 16px;
    font-family: \"{FONT_FAMILY}\";
    font-size: {BODY_SIZE};
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: {INFO_BACKGROUND};
    color: {PRIMARY_DARK};
    border-color: {PRIMARY_HOVER};
}}
QPushButton:pressed {{
    background-color: #DBEAFE;
    color: {PRIMARY_DARK};
}}
QPushButton:disabled {{
    background-color: {SURFACE_SUBTLE};
    color: #9CA3AF;
    border-color: {BORDER_STRONG};
}}
"""

SUCCESS_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {SUCCESS};
    color: #FFFFFF;
    border: 1px solid {SUCCESS_DARK};
    border-radius: {BUTTON_RADIUS}px;
    min-height: {CONTROL_HEIGHT}px;
    padding: 0 16px;
    font-weight: 700;
}}
QPushButton:hover {{ background-color: {SUCCESS_DARK}; }}
QPushButton:pressed {{ background-color: #047857; }}
QPushButton:disabled {{
    background-color: {BORDER_STRONG};
    color: {NEUTRAL};
    border-color: {BORDER_STRONG};
}}
"""

DANGER_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {ERROR};
    color: #FFFFFF;
    border: 1px solid {ERROR_DARK};
    border-radius: {BUTTON_RADIUS}px;
    min-height: {CONTROL_HEIGHT}px;
    padding: 0 16px;
    font-weight: 700;
}}
QPushButton:hover {{ background-color: {ERROR_DARK}; }}
QPushButton:pressed {{ background-color: #B91C1C; }}
QPushButton:disabled {{
    background-color: {BORDER_STRONG};
    color: {NEUTRAL};
    border-color: {BORDER_STRONG};
}}
"""

ICON_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {SURFACE};
    color: {PRIMARY};
    border: 1px solid {BORDER_STRONG};
    border-radius: 18px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    padding: 0;
    font-weight: 700;
}}
QPushButton:hover {{
    background-color: {INFO_BACKGROUND};
    border-color: {PRIMARY};
}}
QPushButton:pressed {{ background-color: #DBEAFE; }}
"""

COMBO_BOX_STYLE = f"""
QComboBox {{
    background-color: {SURFACE};
    color: {TEXT};
    border: 1px solid {BORDER_STRONG};
    border-radius: {INPUT_RADIUS}px;
    min-height: {CONTROL_HEIGHT}px;
    padding: 0 34px 0 12px;
    font-family: \"{FONT_FAMILY}\";
    font-size: {BODY_SIZE};
    font-weight: 600;
}}
QComboBox:hover {{
    border-color: {PRIMARY};
    background-color: #FCFDFF;
}}
QComboBox:focus {{
    border: 2px solid {PRIMARY};
    padding-left: 11px;
    padding-right: 33px;
}}
QComboBox:disabled {{
    background-color: {SURFACE_SUBTLE};
    color: {NEUTRAL};
    border-color: {BORDER};
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 30px;
    border-left: 1px solid {BORDER};
    background-color: {SURFACE_SUBTLE};
    border-top-right-radius: {INPUT_RADIUS}px;
    border-bottom-right-radius: {INPUT_RADIUS}px;
}}
QComboBox::down-arrow {{
    width: 10px;
    height: 10px;
}}
QComboBox QAbstractItemView {{
    background-color: {SURFACE};
    color: {TEXT};
    border: 1px solid {BORDER_STRONG};
    selection-background-color: {PRIMARY};
    selection-color: #FFFFFF;
    padding: 4px;
    outline: none;
}}
QComboBox QAbstractItemView::item {{
    min-height: 34px;
    padding: 7px 10px;
}}
QComboBox QAbstractItemView::item:hover {{
    background-color: {INFO_BACKGROUND};
    color: {PRIMARY_DARK};
}}
"""

CARD_STYLE = f"""
QFrame {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: {CARD_RADIUS}px;
}}
"""

STATUS_BADGE_STYLE = f"""
QLabel {{
    border: none;
    border-radius: 8px;
    padding: 6px 10px;
    font-weight: 700;
}}
"""
