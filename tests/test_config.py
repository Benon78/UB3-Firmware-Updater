"""
=========================================================
UB3 Firmware Updater

Configuration Test
=========================================================
"""

import bootstrap

from ub3_updater.services.config_service import (
    ConfigService,
)


print()
print("=" * 70)
print("UB3 CONFIGURATION TEST")
print("=" * 70)


# =========================================================
# PROJECT ROOT
# =========================================================

print()
print("PROJECT ROOT")
print(
    ConfigService.PROJECT_ROOT
)

assert (
    ConfigService.PROJECT_ROOT.exists()
)

print(
    "[PASS] Project root"
)


# =========================================================
# CONFIGURATION
# =========================================================

print()
print("CONFIGURATION DIRECTORY")

print(
    ConfigService.CONFIG_DIR
)

assert (
    ConfigService.CONFIG_DIR.exists()
)

print(
    "[PASS] Configuration directory"
)


# =========================================================
# PATHS
# =========================================================

print()
print("CONFIGURED PATHS")

paths = (
    ConfigService.paths()
)


for name, path in paths.items():

    print(
        f"{name:15} : {path}"
    )


# =========================================================
# FIRMWARE
# =========================================================

firmware_root = (
    ConfigService.firmware_root()
)


print()
print(
    "Firmware root:"
)

print(
    firmware_root
)


assert (
    firmware_root
    == ConfigService.PROJECT_ROOT
    / "resources"
    / "firmware"
)


assert (
    firmware_root.exists()
)


print(
    "[PASS] Firmware path"
)


# =========================================================
# TOOLS
# =========================================================

tools_root = (
    ConfigService.tools_root()
)


print()
print(
    "Tools root:"
)

print(
    tools_root
)


assert (
    tools_root
    == ConfigService.PROJECT_ROOT
    / "resources"
    / "tools"
)


print(
    "[PASS] Tools path"
)


# =========================================================
# MAPLE
# =========================================================

maple_root = (
    ConfigService.maple_tools_root()
)


maple_uploader = (
    ConfigService.maple_uploader()
)


print()
print(
    "Maple tools:"
)

print(
    maple_root
)

print()
print(
    "Maple uploader:"
)

print(
    maple_uploader
)

assert (
    maple_root
    == tools_root
    / "maple"
)


assert (
    maple_uploader
    == maple_root
    / "maple_upload.bat"
)


print(
    "[PASS] Maple path configuration"
)


# =========================================================
# FIRMWARE CONFIG
# =========================================================

firmware_config = (
    ConfigService.firmware()
)


print()
print(
    "Firmware configuration:"
)

print(
    firmware_config
)


assert (
    firmware_config["default_firmware"]
    == "ZNA2US"
)


print(
    "[PASS] Firmware configuration"
)


# =========================================================
# PATH SUMMARY
# =========================================================

print()
print(
    "PATH SUMMARY"
)


for name, value in (
    ConfigService
    .path_summary()
    .items()
):

    print(
        f"{name:15} : {value}"
    )


# =========================================================
# COMPLETE
# =========================================================

print()
print("=" * 70)
print("ALL CONFIGURATION TESTS PASSED")
print("=" * 70)