"""Step 6.2 - reusable UB3 GUI component contract tests."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from PySide6.QtWidgets import QApplication

from ub3_updater.widgets.components import (
    UB3Button,
    UB3Card,
    UB3ComboBox,
    UB3InfoRow,
    UB3SectionHeader,
    UB3StatusBadge,
    UB3StatusBanner,
)
from ub3_updater.widgets.dashboard_widget import DashboardWidget
from ub3_updater.widgets.connection_status import ConnectionStatusWidget

app = QApplication.instance() or QApplication([])

print("======================================================================")
print("GUI COMPONENT SYSTEM TEST - STEP 6.2")
print("======================================================================")

# ---------------------------------------------------------------
# 1. Component construction
# ---------------------------------------------------------------
print("\nTEST 1 - REUSABLE COMPONENTS")
card = UB3Card()
button = UB3Button("Update", "primary")
combo = UB3ComboBox()
badge = UB3StatusBadge("Ready", "success")
row = UB3InfoRow("COM Port", "COM3")
banner = UB3StatusBanner("Firmware ready", "info")
header = UB3SectionHeader("Firmware Update", "Select approved firmware")

assert card.objectName() == "ub3Card"
print("[PASS] UB3Card created")
assert button.variant() == "primary" and button.styleSheet()
print("[PASS] UB3Button primary created and styled")
assert combo.styleSheet()
print("[PASS] UB3ComboBox created and styled")
assert badge.status() == "success"
print("[PASS] UB3StatusBadge success created")
assert row.label() == "COM Port" and row.value() == "COM3"
print("[PASS] UB3InfoRow created and populated")
assert banner.status() == "info" and banner.message() == "Firmware ready"
print("[PASS] UB3StatusBanner created")
assert header.text() == "Firmware Update"
print("[PASS] UB3SectionHeader created")

# ---------------------------------------------------------------
# 2. Component state variants
# ---------------------------------------------------------------
print("\nTEST 2 - SEMANTIC STATES")
for variant in ("secondary", "success", "danger", "icon"):
    b = UB3Button("Action", variant)
    assert b.variant() == variant and b.styleSheet()
    print(f"[PASS] UB3Button {variant} variant")

for state in ("info", "success", "warning", "error", "neutral"):
    badge.set_status(state)
    assert badge.status() == state and badge.styleSheet()
    print(f"[PASS] UB3StatusBadge {state} state")

for state in ("info", "success", "warning", "error"):
    banner.set_status(state)
    assert banner.status() == state and banner.styleSheet()
    print(f"[PASS] UB3StatusBanner {state} state")

# ---------------------------------------------------------------
# 3. Existing Dashboard integration
# ---------------------------------------------------------------
print("\nTEST 3 - DASHBOARD INTEGRATION")
dashboard = DashboardWidget()
assert isinstance(dashboard.firmware_combo, UB3ComboBox)
print("[PASS] Dashboard firmware dropdown uses UB3ComboBox")
assert isinstance(dashboard.update_button, UB3Button)
assert dashboard.update_button.objectName() == "updateButton"
assert dashboard.update_button.variant() == "primary"
print("[PASS] Dashboard Update uses UB3Button primary")
assert isinstance(dashboard.cancel_button, UB3Button)
assert dashboard.cancel_button.objectName() == "cancelButton"
assert dashboard.cancel_button.variant() == "secondary"
print("[PASS] Dashboard Cancel uses UB3Button secondary")

# ---------------------------------------------------------------
# 4. Existing Connection integration
# ---------------------------------------------------------------
print("\nTEST 4 - CONNECTION INTEGRATION")
connection = ConnectionStatusWidget()
assert isinstance(connection.refresh_button, UB3Button)
assert connection.refresh_button.objectName() == "refreshButton"
assert connection.refresh_button.variant() == "secondary"
print("[PASS] Connection Refresh uses UB3Button secondary")

# ---------------------------------------------------------------
# 5. Existing behavior contracts preserved
# ---------------------------------------------------------------
print("\nTEST 5 - EXISTING GUI CONTRACTS")
assert dashboard.update_button.isEnabled() is False
print("[PASS] Update remains disabled in initial state")
assert dashboard.cancel_button.isEnabled() is False
print("[PASS] Cancel remains disabled in initial state")
assert connection.refresh_button.isEnabled() is True
print("[PASS] Refresh remains enabled")
assert dashboard.firmware_combo.objectName() == "firmwareCombo"
print("[PASS] Firmware combo object identity preserved")

print("\n======================================================================")
print("ALL STEP 6.2 GUI COMPONENT TESTS PASSED")
print("======================================================================")
print("No physical UB3 was programmed.")
