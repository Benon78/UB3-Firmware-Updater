"""
Regression test for UploadService default Maple uploader resolution.
"""

from pathlib import Path

import bootstrap

from ub3_updater.services.config_service import ConfigService
from ub3_updater.services.upload_service import UploadService

print("=" * 70)
print("UPLOAD SERVICE DEFAULT UPLOADER TEST")
print("=" * 70)

service = UploadService()
resolved = service.resolve_default_uploader()

print("\nResolved uploader:")
print(resolved)
print("\nConfigured project uploader:")
print(ConfigService.maple_uploader())

assert isinstance(resolved, Path)
assert resolved.is_absolute()
assert service.uploader_path == resolved

print("\n[PASS] resolve_default_uploader() is available")
print("[PASS] Resolved path is absolute")
print("[PASS] UploadService constructs successfully")
print("\nNo physical UB3 was programmed.")
