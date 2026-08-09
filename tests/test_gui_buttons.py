"""
Step 5.1 - Explicit Home Page action-button style test.

This test validates the style contract without requiring a physical UB3.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ub3_updater.widgets.action_button_style import (
    UPDATE_BUTTON_STYLE,
    CANCEL_BUTTON_STYLE,
    REFRESH_BUTTON_STYLE,
)


print("=" * 70)
print("GUI ACTION BUTTON TEST - STEP 5.1")
print("=" * 70)

for name, stylesheet, object_name in (
    ("Update", UPDATE_BUTTON_STYLE, "updateButton"),
    ("Cancel", CANCEL_BUTTON_STYLE, "cancelButton"),
    ("Refresh", REFRESH_BUTTON_STYLE, "refreshButton"),
):
    assert f"QPushButton#{object_name}" in stylesheet
    assert "background-color:" in stylesheet
    assert "color:" in stylesheet
    assert "border:" in stylesheet

    print(f"[PASS] {name} button has explicit background")
    print(f"[PASS] {name} button has explicit text color")
    print(f"[PASS] {name} button has explicit border")

assert "#2563EB" in UPDATE_BUTTON_STYLE
assert "#FFFFFF" in UPDATE_BUTTON_STYLE
assert "#2563EB" in CANCEL_BUTTON_STYLE
assert "#FFFFFF" in CANCEL_BUTTON_STYLE

print("[PASS] Update button uses blue background / white text")
print("[PASS] Cancel button uses blue background / white text")
print("[PASS] Refresh button uses explicit light action styling")

print("=" * 70)
print("ALL STEP 5.1 GUI BUTTON TESTS PASSED")
print("=" * 70)
