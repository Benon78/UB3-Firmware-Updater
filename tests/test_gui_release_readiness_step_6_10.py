"""
STEP 6.10 - FINAL GUI / UX ACCEPTANCE & RELEASE READINESS

Software-only release-readiness checks.
No physical UB3 programming is performed.
"""

from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "config" / "app_config.json"
CHANGELOG_PATH = PROJECT_ROOT / "CHANGELOG.md"
PROVENANCE_PATH = PROJECT_ROOT / "STEP_5_5_RUNTIME_PROVENANCE.md"
MAIN_WINDOW_PATH = PROJECT_ROOT / "src" / "ub3_updater" / "ui" / "main_window.py"
README_PATH = PROJECT_ROOT / "README.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


print("=" * 70)
print("STEP 6.10 - FINAL GUI / UX ACCEPTANCE & RELEASE READINESS")
print("=" * 70)

# --------------------------------------------------------------
# 1. Version source of truth
# --------------------------------------------------------------
config = json.loads(read_text(CONFIG_PATH))
version = config["application"]["version"]

assert version, "Application version is empty"
assert version != "0.2.0", "Legacy application version is still active"
print(f"[PASS] Application version is centrally configured: {version}")

# --------------------------------------------------------------
# 2. Footer uses ConfigService rather than hardcoded version
# --------------------------------------------------------------
main_window = read_text(MAIN_WINDOW_PATH)

assert "ConfigService.application_version()" in main_window
assert 'f"v{ConfigService.application_version()}"' in main_window
print("[PASS] GUI footer uses centralized application version")

# --------------------------------------------------------------
# 3. Standalone provenance document retired
# --------------------------------------------------------------
assert not PROVENANCE_PATH.exists()
print("[PASS] STEP_5_5_RUNTIME_PROVENANCE.md removed")

# --------------------------------------------------------------
# 4. Provenance retained in changelog
# --------------------------------------------------------------
changelog = read_text(CHANGELOG_PATH)

required_provenance = (
    "# Step 5.5 Final Runtime Provenance",
    "Arduino(2).zip supplied for the UB3 project.",
    "maple_upload <detected COM> 2 1EAF:003 <firmware.bin>",
    "The firmware binaries are not modified by Step 5.5.",
    "install_STM_COM_drivers.bat",
)

for item in required_provenance:
    assert item in changelog, f"Missing consolidated provenance entry: {item}"

print("[PASS] Step 5.5 runtime provenance is retained in CHANGELOG.md")

# --------------------------------------------------------------
# 5. Release documentation remains present
# --------------------------------------------------------------
assert README_PATH.exists()
print("[PASS] README.md retained as project/user documentation")

# --------------------------------------------------------------
# 6. Test suite remains a development/release-validation asset
# --------------------------------------------------------------
tests_dir = PROJECT_ROOT / "tests"
assert tests_dir.is_dir()
assert (tests_dir / "test_gui_complete_workflow_step_6_9.py").exists()
print("[PASS] Regression test suite remains available for validation")

print()
print("STEP 6.10 SOFTWARE RELEASE-READINESS CHECKS PASSED")
print("No physical UB3 was programmed.")
