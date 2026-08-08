"""
=========================================================
UB3 Firmware Updater

USB Hardware Definitions

Developer:
Benjamin William

Description:
Central repository for all known USB identifiers used by
the UB3 Firmware Updater.

Every hardware detection routine should use these
constants instead of hard-coded values.

Version:
0.4.0
=========================================================
"""

# =========================================================
# Vendor
# =========================================================

STM32_VENDOR_ID = "1EAF"

# =========================================================
# Product IDs
# =========================================================

# UB3 Normal Operating Mode
MAPLE_SERIAL_PID = "0004"

# UB3 Bootloader / Flash Mode
BOOTLOADER_PID = "0029"

# =========================================================
# USB Descriptions
# =========================================================

MAPLE_SERIAL_DESCRIPTION = "Maple Serial"

BOOTLOADER_DESCRIPTION = "USB Serial Device"

# =========================================================
# Device States
# =========================================================

SUPPORTED_DEVICES = {

    (
        STM32_VENDOR_ID,
        MAPLE_SERIAL_PID,
    ): {
        "name": "UB3 Runtime",
        "state": "MAPLE_SERIAL",
        "description": MAPLE_SERIAL_DESCRIPTION,
    },

    (
        STM32_VENDOR_ID,
        BOOTLOADER_PID,
    ): {
        "name": "UB3 Bootloader",
        "state": "USB_SERIAL",
        "description": BOOTLOADER_DESCRIPTION,
    },
}