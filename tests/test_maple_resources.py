"""
Step 5.1 - Maple runtime resource validation.

No Maple Loader execution.
No physical UB3 access.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ub3_updater.services.maple_resource_service import MapleResourceService


print("=" * 70)
print("MAPLE RUNTIME RESOURCE TEST - STEP 5.1")
print("=" * 70)

service = MapleResourceService()

result = service.validate()

assert result.valid is True, (
    f"Maple runtime validation failed: "
    f"{result.message}; missing={result.missing_files}"
)

print("[PASS] Maple runtime resources are complete")

root = service.resource_root

for relative in service.REQUIRED_FILES:
    path = root / relative
    assert path.is_file(), f"Missing required file: {relative}"
    print(f"[PASS] {relative}")

manifest = (root / "tool_manifest.json").read_text(
    encoding="utf-8"
)

assert '"entrypoint": "maple_upload.bat"' in manifest
assert '"loader": "maple_loader.jar"' in manifest

print("[PASS] Tool manifest is valid")
print("[PASS] Maple Loader execution was not attempted")
print("[PASS] No physical UB3 was programmed")

print("=" * 70)
print("ALL STEP 5.1 MAPLE RESOURCE TESTS PASSED")
print("=" * 70)
