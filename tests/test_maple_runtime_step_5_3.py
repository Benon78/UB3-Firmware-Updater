"""
=========================================================
UB3 Firmware Updater

Step 5.3 - Bundled Maple Runtime Contract Test

Purpose
-------
Verify that production UploadService execution resolves
the Maple uploader from the project resources and validates
the bundled runtime before execution.

This test does not execute maple_upload.bat.
No physical UB3 is programmed.
=========================================================
"""

from pathlib import Path

import bootstrap

from ub3_updater.services.config_service import ConfigService
from ub3_updater.services.maple_resource_service import (
    MapleResourceService,
)
from ub3_updater.services.upload_service import UploadService


print("=" * 70)
print("BUNDLED MAPLE RUNTIME CONTRACT - STEP 5.3")
print("=" * 70)


configured = (
    ConfigService.maple_uploader()
    .resolve()
)

service = UploadService()

resolved = service.resolve_default_uploader()

print("\nConfigured uploader:")
print(configured)

print("\nResolved uploader:")
print(resolved)


assert resolved == configured
print("[PASS] UploadService uses bundled Maple uploader")


assert resolved.is_file()
print("[PASS] Bundled maple_upload.bat exists")


resource_service = MapleResourceService(
    resource_root=resolved.parent
)

validation = resource_service.validate()

assert validation.valid, (
    "Bundled Maple runtime invalid: "
    f"{validation.message}; "
    f"missing={validation.missing_files}"
)

print("[PASS] Bundled Maple runtime validated")

for required in ("dfu-util.exe", "libusb-1.0.dll"):
    assert (resolved.parent / required).is_file(), required
    print(f"[PASS] Bundled {required} exists")



assert service.uploader_path == configured
print("[PASS] UploadService stores bundled uploader path")


assert "resources" in str(resolved).lower()
assert "tools" in str(resolved).lower()
assert "maple" in str(resolved).lower()
print("[PASS] Uploader path belongs to project resources")


# ---------------------------------------------------------
# C:\\tmp must not be a production firmware dependency.
# ---------------------------------------------------------

assert "c:\\tmp" not in str(resolved).lower()
print("[PASS] C:\\tmp is not used for Maple uploader")


print("\n" + "=" * 70)
print("ALL STEP 5.3 BUNDLED RUNTIME TESTS PASSED")
print("=" * 70)

print("\nmaple_upload.bat was not executed.")
print("No physical UB3 was programmed.")
