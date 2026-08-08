# Changelog

All notable changes to this project will be documented in this file.

The project follows Semantic Versioning (SemVer).

---

## [Unreleased]

### Planned
- Modern desktop interface
- Automatic COM port detection
- DFU device detection
- Firmware library manager
- Firmware upload engine
- Upload logging
- Configuration manager
- Settings page

---

## [0.1.0] - In Development

### Added
- Project structure
- Git repository
- Python virtual environment
- PySide6 framework
- Application entry point (`main.py`)
- Application bootstrap (`app.py`)
- Initial documentation

## v0.2.0

### Added
- Professional src package architecture
- Application launcher
- Configuration Service
- JSON configuration system
- Firmware configuration
- Application settings

## [0.6.0] - 2026-08-08

### Added

- Added `UploadResult` model for structured firmware upload results.
- Added upload status states:
  - `NOT_STARTED`
  - `DEVICE_NOT_READY`
  - `FIRMWARE_INVALID`
  - `PROCESS_ERROR`
  - `UPLOADING`
  - `SUCCESS`
  - `SUCCESS_WITH_WARNING`
  - `FAILED`
  - `CANCELLED`
  - `TIMEOUT`
- Added `UploadResult.to_dict()` serialization.
- Added `UploadResult.from_dict()` deserialization.
- Added Maple Loader result interpretation tests.
- Added real Maple Loader process test.
- Added firmware upload service tests.
- Added real firmware upload test workflow.

### Changed

- Refined `UploadService` to automatically detect the current UB3 before every upload.
- Removed dependency on a potentially stale cached COM port during firmware upload.
- Upload now uses the COM port detected from the current `Device` object.
- Refined Maple Loader command construction for Windows.
- Firmware is prepared in `C:\tmp` before Maple Loader execution.
- Improved Maple Loader output interpretation.
- Firmware download completion is now distinguished from post-upload USB reset warnings.
- `SUCCESS_WITH_WARNING` is now supported for successful firmware programming followed by a non-fatal USB reset warning.
- Improved `ProcessRunner` integration with the firmware upload workflow.

### Verified

- UB3 detected automatically in Maple Serial mode.
- Maple Serial `VID:PID = 1EAF:0004` confirmed as the valid firmware-update starting state.
- USB Serial Device / bootloader mode is not used as the starting state.
- Maple Loader `ALT ID = 2` confirmed.
- Maple DFU ID `1EAF:003` confirmed.
- Real ZNA2US firmware upload successfully completed through Maple Loader.
- Firmware transfer reached `Done!`.
- Post-upload USB reset warning was observed and correctly classified as non-fatal.

### Tests

- `test_upload_result.py` — PASS
- `test_maple_result.py` — PASS
- `test_upload_service.py` — PASS
- `test_maple_process.py` — PASS
- Real Maple Loader process test — PASS
- Real ZNA2US firmware transfer — PASS

### Notes

The current Maple Loader workflow starts from Maple Serial mode and performs the DTR reset automatically. The operator should not manually place the UB3 into flash/bootloader mode before starting an update.

### Verified - Real Hardware Integration

- Completed real end-to-end `UploadService.upload()` test using a physical UB3.
- Automatic Maple Serial detection verified.
- Automatic COM port detection verified.
- UB3 `VID:PID = 1EAF:0004` validation verified.
- Maple Loader DTR reset workflow verified.
- Maple DFU device `1EAF:003` detection verified.
- Firmware staging to `C:\tmp` verified.
- Real ZNA2US 1.00 firmware transfer completed successfully.
- Maple Loader reported `Done!` after firmware download.
- Post-upload USB reset warning correctly classified as `SUCCESS_WITH_WARNING`.
- Real upload completed with return code `0`.
- End-to-end upload duration observed at approximately 18.6 seconds.