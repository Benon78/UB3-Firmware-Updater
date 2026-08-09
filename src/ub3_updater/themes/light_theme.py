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

PRIMARY = "#2563EB"
PRIMARY_DARK = "#1E3A8A"

SUCCESS = "#10B981"
WARNING = "#F59E0B"
ERROR = "#EF4444"
NEUTRAL = "#6B7280"

BACKGROUND = "#F3F4F6"
CARD = "#FFFFFF"

TEXT = "#111827"
TEXT_SECONDARY = "#6B7280"
BORDER = "#E5E7EB"

INFO_BACKGROUND = "#EFF6FF"
SUCCESS_BACKGROUND = "#ECFDF5"
WARNING_BACKGROUND = "#FFFBEB"
ERROR_BACKGROUND = "#FEF2F2"

WINDOW_RADIUS = 10
CARD_RADIUS = 8
BUTTON_RADIUS = 6
FONT = "Segoe UI"

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
    background: {SUCCESS};
    color: white;
    border: 1px solid #059669;
    border-radius: {BUTTON_RADIUS}px;
    min-height: 44px;
    min-width: 140px;
    padding: 0 20px;
    font-size: 11pt;
    font-weight: 700;
}}
QPushButton#updateButton:hover {{
    background: #059669;
}}
QPushButton#updateButton:pressed {{
    background: #047857;
}}
QPushButton#updateButton:disabled {{
    background: #D1D5DB;
    color: #6B7280;
    border-color: #D1D5DB;
}}

QPushButton#cancelButton {{
    background: {ERROR};
    color: white;
    border: 1px solid #DC2626;
    border-radius: {BUTTON_RADIUS}px;
    min-height: 44px;
    min-width: 120px;
    padding: 0 18px;
    font-weight: 700;
}}
QPushButton#cancelButton:hover {{
    background: #DC2626;
}}
QPushButton#cancelButton:pressed {{
    background: #B91C1C;
}}
QPushButton#cancelButton:disabled {{
    background: #D1D5DB;
    color: #6B7280;
    border-color: #D1D5DB;
}}

QPushButton#refreshButton {{
    background: white;
    color: {PRIMARY_DARK};
    border: 1px solid {PRIMARY};
    min-height: 38px;
    min-width: 38px;
}}
QPushButton#refreshButton:hover {{
    background: {INFO_BACKGROUND};
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
    background: white;
    border: 1px solid {BORDER};
    border-radius: {BUTTON_RADIUS}px;
    padding: 7px 10px;
    min-height: 22px;
}}

QComboBox:focus,
QLineEdit:focus {{
    border: 2px solid {PRIMARY};
}}
QComboBox QAbstractItemView {{
    background: white;
    color: {TEXT};
    border: 1px solid {BORDER};
    selection-background-color: {PRIMARY};
    selection-color: white;
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
