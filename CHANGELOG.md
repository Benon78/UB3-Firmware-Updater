## 2026-08-09 - Step 4 Baseline - Home Page Action Controls

- Promoted the Home page device refresh control as a HomePage-level reference while keeping ownership in the Connection Status card.
- Changed the Refresh button to an explicit blue primary action with white text.
- Changed the Update button to the primary blue action colour with white text.
- Changed the Cancel button to the same blue action colour with white text for consistent operator controls.
- Added GUI regression coverage confirming the Home page Refresh button invokes device refresh.
- Preserved the existing independent Home page scrolling and firmware-selection behavior.

## 2026-08-09 - GUI Step 3 Test Harness Fix

- Updated GUI test controller stubs to implement the MainWindow callback registration contract.
- Added the controller state property required by the MainWindow header.
- Kept layout and firmware-selection tests independent of the production controller.

## 2026-08-09 - GUI Step 3 Layout Refinement

- Added independent vertical scroll areas for the Home page device and firmware sections.
- Prevented sections from compressing into each other as content grows or window height decreases.
- Disabled horizontal scrolling to preserve the responsive two-column layout.
- Added GUI layout regression tests.

## 2026-08-09 - GUI Step 3 - Firmware Selection

- Improved firmware package selection presentation.
- Added version, target, release date, filename, file size and validation status details.
- Added firmware selection regression tests.

# Changelog

## Step 4.2 — Update Confirmation Dialog

- Added a dedicated, operator-focused firmware update confirmation dialog.
- Displays the validated UB3 identity and connection details.
- Displays the validated firmware name, version, target, file, and size.
- Shows a clear pre-update validation success state.
- Requires explicit operator acknowledgement before enabling `Update UB3`.
- Uses the established blue/white action-button styling.
- Dialog is presentation-only and never starts `UploadWorker`.
- Added isolated confirmation-dialog tests.


## Step 4.1 Validation Fix

- Fixed pre-update validation so a fresh USB scan returning no device is treated as a real disconnect.
- Removed stale-device fallback after an authoritative scan result.
- Prevents an update from proceeding when the intended UB3 has been unplugged.
- Existing GUI and controller behavior remains unchanged.


## Step 4.1 — Pre-Update Safety Validation

- Added `PreUpdateValidationResult` model for final update safety checks.
- Added `UpdateController.validate_before_update()`.
- Performs a fresh device scan before programming.
- Verifies the UB3 is connected in Maple Serial mode.
- Verifies the connected device matches the device captured before confirmation.
- Re-validates the selected firmware file immediately before update.
- Blocks the update when the intended UB3 is disconnected or replaced.
- Added `tests/test_pre_update_validation.py`.
- No physical UB3 programming is performed by the new tests.


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

### Implement the initial UB3 Firmware Updater GUI foundation.

- Add light theme and base UI styling
- Add MainWindow and HomePage
- Add ConnectionStatus widget
- Add DashboardWidget
- Integrate firmware repository into the GUI
- Display firmware package and version
- Add automatic UB3 connection state handling
- Display detected COM port and Maple Serial state
- Enable Update only when the device is ready
- Disable Update when the device disconnects
- Add GUI regression tests
- Preserve existing UploadService, UploadWorker and UpdateController architecture

## 2026-08-09 - GUI Step 2 - Device Information

- Added Device Information panel to the Home screen.
- Displays detected COM port, USB mode, VID:PID, manufacturer and hardware ID.
- Unavailable firmware/bootloader metadata is explicitly shown as Not reported.
- Added device information GUI regression tests.

## 2026-08-09 - GUI UX Step 1.1

- Improved button contrast and explicit action colours.
- Improved firmware selector to show package name and version.
- Added GUI UX regression coverage.