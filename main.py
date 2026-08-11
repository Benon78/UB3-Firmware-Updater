"""
=========================================================
UB3 Device Manager

Project Launcher

Developer:
Benjamin William

Version:
0.5.5
=========================================================
"""

from pathlib import Path
import sys

# -------------------------------------------------------
# Add src folder to Python path
# -------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent

SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

# -------------------------------------------------------
# Launch application
# -------------------------------------------------------

from ub3_updater.main import main

if __name__ == "__main__":
    main()