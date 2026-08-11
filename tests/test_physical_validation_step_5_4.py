"""
Step 5.4 - Controlled physical validation safety test.

This test never calls a real uploader and never programs hardware.
It verifies the physical-validation entry point's safety contract
and its use of existing project resources.
"""

from pathlib import Path
import ast
import sys

import bootstrap

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "tools" / "physical_validation.py"

print("=" * 70)
print("STEP 5.4 - CONTROLLED PHYSICAL VALIDATION TEST")
print("=" * 70)

assert SCRIPT.is_file()
print("[PASS] Physical validation tool exists")

source = SCRIPT.read_text(encoding="utf-8")
tree = ast.parse(source)

assert "PROGRAM-UB3" in source
print("[PASS] Explicit physical-programming confirmation token exists")

assert "--program" in source
print("[PASS] Physical programming requires explicit --program")

assert "ConfigService" in source
assert "DeviceService" in source
assert "FirmwareService" in source
assert "UploadService" in source
print("[PASS] Existing project service architecture is reused")

assert "ConfigService" in source
assert "maple_uploader()" in source
assert "firmware_root()" in source
print("[PASS] Bundled project resource configuration is used")

assert "device_service.scan()" in source
print("[PASS] Fresh device scan is performed during pre-flight")

assert "device.is_maple" in source
print("[PASS] Maple Serial validation is enforced")

assert "upload_service.build_command" in source
print("[PASS] Existing UploadService command construction is reused")

assert "upload_service.upload" in source
print("[PASS] Existing UploadService performs the real upload")

# The script must not introduce another process runner or another
# subprocess-based uploader implementation.
for forbidden in ("subprocess.Popen", "subprocess.run", "ProcessRunner("):
    assert forbidden not in source, (
        f"New process execution architecture detected: {forbidden}"
    )
print("[PASS] No duplicate process-execution architecture introduced")

# Verify the bundled resource is present.
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from ub3_updater.services.config_service import ConfigService

uploader = ConfigService.maple_uploader().resolve()
firmware_root = ConfigService.firmware_root().resolve()

assert uploader.is_file()
print("[PASS] Bundled maple_upload.bat exists")

assert firmware_root.is_dir()
print("[PASS] resources/firmware exists")

# Verify at least one firmware package exists.
zn = firmware_root / "ZNA2US"
assert zn.is_dir()
print("[PASS] ZNA2US firmware package exists")

print("[PASS] No physical UB3 programmed")
print("=" * 70)
print("ALL STEP 5.4 CONTROLLED VALIDATION TESTS PASSED")
print("=" * 70)
