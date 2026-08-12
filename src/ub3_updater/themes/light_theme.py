"""
UB3 Firmware Updater - Light Theme

UI palette based on the approved UB3 UI/UX design:
Primary Dark  #1E3A8A
Primary Blue  #2563EB
Success       #10B981
Warning       #F59E0B
Error         #EF4444
Neutral       #6B7280
Background    #F3F4F6
"""

from ub3_updater.themes.design_system import (
    PRIMARY, PRIMARY_DARK, PRIMARY_HOVER, PRIMARY_PRESSED,
    SUCCESS, WARNING, ERROR, NEUTRAL,
    BACKGROUND, SURFACE as CARD, TEXT, TEXT_SECONDARY, BORDER,
    INFO_BACKGROUND, SUCCESS_BACKGROUND, WARNING_BACKGROUND,
    ERROR_BACKGROUND, CARD_RADIUS, BUTTON_RADIUS, FONT_FAMILY as FONT,
)

STYLE = f"""
QMainWindow {{
    background: {BACKGROUND};
}}

QWidget {{
    background: {BACKGROUND};
    color: {TEXT};
    font-family: "{FONT}";
    font-size: 10pt;
}}

QFrame {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: {CARD_RADIUS}px;
}}

QLabel {{
    background: transparent;
}}

QPushButton {{
    background: {PRIMARY};
    color: white;
    border: none;
    border-radius: {BUTTON_RADIUS}px;
    min-height: 38px;
    padding: 0 16px;
    font-weight: 600;
}}

QPushButton:hover {{
    background: #1D4ED8;
}}

QPushButton:pressed {{
    background: {PRIMARY_DARK};
}}

QPushButton:disabled {{
    background: #D1D5DB;
    color: #6B7280;
}}


QPushButton#updateButton {{
    background: {PRIMARY};
    color: white;
    border: 1px solid {PRIMARY_DARK};
    border-radius: {BUTTON_RADIUS}px;
    min-height: 44px;
    min-width: 140px;
    padding: 0 20px;
    font-size: 11pt;
    font-weight: 700;
}}
QPushButton#updateButton:hover {{
    background: #1D4ED8;
}}
QPushButton#updateButton:pressed {{
    background: {PRIMARY_DARK};
}}
QPushButton#updateButton:disabled {{
    background: #D1D5DB;
    color: #6B7280;
    border-color: #D1D5DB;
}}

QPushButton#cancelButton {{
    background: {PRIMARY};
    color: white;
    border: 1px solid {PRIMARY_DARK};
    border-radius: {BUTTON_RADIUS}px;
    min-height: 44px;
    min-width: 120px;
    padding: 0 18px;
    font-weight: 700;
}}
QPushButton#cancelButton:hover {{
    background: #1D4ED8;
}}
QPushButton#cancelButton:pressed {{
    background: {PRIMARY_DARK};
}}
QPushButton#cancelButton:disabled {{
    background: #D1D5DB;
    color: #6B7280;
    border-color: #D1D5DB;
}}

QPushButton#refreshButton {{
    background: {PRIMARY};
    color: white;
    border: 1px solid {PRIMARY_DARK};
    border-radius: {BUTTON_RADIUS}px;
    min-height: 38px;
    min-width: 90px;
    padding: 0 14px;
    font-weight: 700;
}}
QPushButton#refreshButton:hover {{
    background: #1D4ED8;
}}
QPushButton#refreshButton:pressed {{
    background: {PRIMARY_DARK};
}}
QPushButton#refreshButton:disabled {{
    background: #D1D5DB;
    color: #6B7280;
    border-color: #D1D5DB;
}}

QPushButton[class="secondary"] {{
    background: white;
    color: {PRIMARY};
    border: 1px solid {PRIMARY};
}}

QPushButton[class="secondary"]:hover {{
    background: {INFO_BACKGROUND};
}}

QPushButton[class="success"] {{
    background: {SUCCESS};
}}

QPushButton[class="danger"] {{
    background: {ERROR};
}}

QComboBox,
QLineEdit {{
    background: {CARD};
    color: {TEXT};
    border: 1px solid #D1D5DB;
    border-radius: {BUTTON_RADIUS}px;
    padding: 0 12px;
    min-height: 40px;
    font-family: "{FONT}";
    font-weight: 600;
}}

QComboBox:hover {{
    border-color: {PRIMARY};
}}

QComboBox:focus,
QLineEdit:focus {{
    border: 2px solid {PRIMARY};
}}

QComboBox::drop-down {{
    width: 30px;
    border-left: 1px solid {BORDER};
    background: #F9FAFB;
}}

QComboBox QAbstractItemView {{
    background: {CARD};
    color: {TEXT};
    border: 1px solid #D1D5DB;
    selection-background-color: {PRIMARY};
    selection-color: white;
    padding: 4px;
}}

QComboBox QAbstractItemView::item {{
    min-height: 34px;
    padding: 7px 10px;
}}

QComboBox QAbstractItemView::item:hover {{
    background: {INFO_BACKGROUND};
    color: {PRIMARY_DARK};
}}

QComboBox:disabled {{
    background: #F9FAFB;
    color: {NEUTRAL};
}}

QProgressBar {{
    background: #E5E7EB;
    border: none;
    border-radius: 7px;
    height: 14px;
    text-align: center;
    color: {TEXT};
}}

QProgressBar::chunk {{
    background: {PRIMARY};
    border-radius: 7px;
}}

QPlainTextEdit,
QTextEdit {{
    background: white;
    border: 1px solid {BORDER};
    border-radius: {BUTTON_RADIUS}px;
    padding: 8px;
}}

QScrollBar:vertical {{
    background: #F9FAFB;
    width: 10px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: #D1D5DB;
    border-radius: 5px;
    min-height: 30px;
}}

QStatusBar {{
    background: white;
    border-top: 1px solid {BORDER};
}}
"""

def card_style():
    return f"""
        QFrame {{
            background: {CARD};
            border: 1px solid {BORDER};
            border-radius: {CARD_RADIUS}px;
        }}
    """

def title_style():
    return f"""
        color: {TEXT};
        font-size: 14pt;
        font-weight: 600;
        border: none;
    """

def secondary_style():
    return f"""
        color: {TEXT_SECONDARY};
        border: none;
    """
