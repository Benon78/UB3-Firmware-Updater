"""
=========================================================
UB3 Firmware Updater

Professional Light Theme

Developer:
Benjamin William
=========================================================
"""

PRIMARY = "#2563EB"
PRIMARY_DARK = "#1E3A8A"

SUCCESS = "#10B981"
WARNING = "#F59E0B"
ERROR = "#EF4444"

BACKGROUND = "#F8FAFC"
CARD = "#FFFFFF"

TEXT = "#111827"
TEXT_SECONDARY = "#6B7280"

BORDER = "#E5E7EB"

WINDOW_RADIUS = 10
CARD_RADIUS = 8
BUTTON_RADIUS = 6

FONT = "Segoe UI"

STYLE = f"""

QMainWindow {{
    background:{BACKGROUND};
}}

QWidget {{
    background:{BACKGROUND};
    color:{TEXT};
    font-family:"Segoe UI";
    font-size:10pt;
}}

QFrame {{
    background:{CARD};
    border:1px solid {BORDER};
    border-radius:8px;
}}

QPushButton {{

    background:{PRIMARY};

    color:white;

    border:none;

    border-radius:6px;

    min-height:38px;

    font-weight:600;

}}

QPushButton:hover {{

    background:#1D4ED8;

}}

QPushButton:pressed {{

    background:{PRIMARY_DARK};

}}

QLineEdit,
QComboBox,
QPlainTextEdit,
QTextEdit {{

    background:white;

    border:1px solid {BORDER};

    border-radius:6px;

    padding:6px;

}}

QTableWidget {{

    background:white;

    gridline-color:{BORDER};

    border:1px solid {BORDER};

}}

QHeaderView::section {{

    background:#F3F4F6;

    padding:8px;

    border:none;

    border-bottom:1px solid {BORDER};

    font-weight:600;

}}

QStatusBar {{

    background:white;

    border-top:1px solid {BORDER};

}}

"""