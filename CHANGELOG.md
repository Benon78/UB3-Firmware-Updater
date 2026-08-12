## Step 6.7 — Success / Warning / Failure UX

- Add a reusable terminal result banner to the update dashboard.
- Present success, success-with-warning, failure, and cancelled outcomes using semantic UI states.
- Preserve existing UploadResult interpretation and upload architecture.
- Clear the terminal result banner when a new upload starts.
- Add dedicated Step 6.7 GUI regression coverage.
- No firmware, Maple, device detection, worker, or upload execution changes.

## Step 6.6.1 test correction

- Align worker lifecycle regression coverage with the existing architecture: upload completion and worker reset are owned by `HomePage`.
- Preserve `MainWindow` as the top-level GUI container; no lifecycle responsibility was moved into it.
- Correct escaped lifecycle docstring delimiters in `HomePage`.

## Step 6.6.1 follow-up — safe UploadWorker reset

- Added GUI-side terminal worker reset polling after UploadResult delivery.
- The existing `UpdateController.reset_worker()` API is used only after the worker stops.
- Supports repeated firmware updates without restarting the application.
- No Maple/upload command or firmware architecture changes.

## Step 6.6.1 — UploadWorker lifecycle reusability

- Reset the completed/failed UploadWorker through the existing controller API after the worker thread has actually exited.
- Prevent the GUI from becoming unable to start a second firmware update in the same application session.
- Preserve UploadWorker terminal-state protection, UploadService, ProcessRunner, Maple command, device detection, COM detection, and firmware handling.
- Add regression coverage for sequential updates with different firmware packages.

## Step 6.6 — Upload / Progress UI

- Added operator-facing upload workflow phase indicators.
- Added explicit post-upload USB re-enumeration / Maple Serial recovery presentation.
- Preserved workflow-phase progress semantics; no fabricated byte-transfer percentage.
- Preserved existing UploadWorker, UploadService, ProcessRunner, and Maple command architecture.
- Added Step 6.6 GUI regression coverage.

## Step 6.5 — Firmware Selection UI

- Improve firmware-selection presentation using reusable UB3 UI components.
- Add structured firmware details card and semantic validation badge.
- Preserve real `Firmware` model selection and repository paths.
- Preserve existing firmware dropdown object contract and upload architecture.
- Add dedicated Step 6.5 GUI regression coverage.
- No firmware binaries or Maple upload behavior changed.

## Step 6.4 test correction

- Updated the Step 6.4 `ControllerStub` to implement the existing MainWindow controller callback registration contract.
- No production architecture or device/upload behavior changed.

## Step 6.4 — Device Information UI

- Redesigned the Device Information card using reusable UB3 presentation components.
- Preserved the existing Device model and all device-information contracts.
- Preserved the rule that unavailable firmware, bootloader, hardware, board, and device-type values are shown as `Not reported`.
- Added a horizontally scrollable Connection Status content area for narrow Home page layouts.
- Horizontal scrolling is enabled only when required; vertical scrolling is disabled for the connection-status strip.
- No device detection, firmware, worker, upload, or Maple architecture changes.

## Step 6.3 — Home / Connect UI

- Redesigned the Home page connection presentation using the Step 6 design system.
- Added a clear operator-facing device connection status and contextual connection hint.
- Added semantic Connected / Disconnected status presentation.
- Preserved automatic COM-port detection and existing device/controller data flow.
- Preserved the existing two-column independent-scroll HomePage architecture.
- Preserved existing GUI object names and controller/worker/upload contracts.
- Added Step 6.3 Home / Connect UI regression coverage.
- No physical UB3 was programmed.

## Step 6.1 follow-up — GUI action-button application fix

- Applied the Step 6.1 UB3 primary/secondary styles directly to the Dashboard update and cancel buttons.
- Preserved existing button object names and controller/worker behavior.
- No upload, device-detection, firmware, or Maple architecture changes.

## 2026-08-12 — Step 6.1 Started: GUI Design System Foundation

### GUI foundation
- Reviewed and preserved the Step 5.5 GUI/controller/service/worker architecture.
- Added a centralized UB3 GUI design-system module for semantic colors, spacing, typography, radii, control dimensions, cards, buttons, and firmware dropdown styling.
- Kept hardware detection, firmware discovery, upload orchestration, workers, and Maple command execution unchanged.
- Applied explicit UB3 styling directly to the firmware dropdown and operator action buttons so native Qt rendering cannot replace the intended background/border treatment.
- Centralized application-version display through `ConfigService` instead of hardcoded GUI footer/version strings.
- Added a Step 6.1 GUI design-system regression test.
- Extended the full regression runner to include the Step 6.1 test.

### Scope
- Step 6.1 is presentation-only.
- Home-page layout, device card redesign, firmware card redesign, progress/result redesign, and full UI/UX integration remain subsequent Step 6 deliverables.
- `README.md` remains unchanged; milestone history is recorded only in `CHANGELOG.md`.

## 2026-08-12 — Step 5.5 Baseline: Version 0.5.5

- Established the complete Step 5.5 codebase as the baseline after the full regression suite passed 17/17.
- Updated the application version from `0.2.0` to `0.5.5` in application configuration and visible application version references.
- Updated the GUI footer to display `v0.5.5`.
- Preserved the existing Maple upload architecture, command contract, bundled runtime, driver resources, firmware repository, and post-upload re-enumeration behavior.
- `README.md` remains user/project documentation only; milestone history remains in this changelog.

## 2026-08-11 — Step 5.5 Finalized: Maple Runtime, Drivers & Post-Upload Re-enumeration

### Runtime
- Bundled the approved Arduino STM32 Maple runtime required by the proven manual upload workflow.
- Bundled Java `1.8.0_191` (`i586`) from the supplied Arduino environment.
- Corrected Java runtime validation to the actual supplied layout: `java/bin/client/jvm.dll`.
- No `JAVA_HOME`, system Java, Arduino IDE, or system Java `PATH` configuration is required.
- The Maple launcher uses the project's bundled Java runtime directly.

### USB Drivers
- Bundled the supplied Arduino STM32 Windows driver package.
- Included Maple DFU, Maple Serial, and STM COM driver resources.
- Included `install_drivers.bat` and `install_STM_COM_drivers.bat`.
- Driver installation remains an explicit privileged setup operation; the updater does not silently modify Windows drivers during normal upload.

### Upload Architecture
- Existing `UploadService -> ProcessRunner -> maple_upload.bat -> maple_loader.jar` architecture is unchanged.
- Existing Maple command contract is unchanged:
  `maple_upload <detected COM> 2 1EAF:003 <firmware.bin>`.
- COM ports remain runtime-detected; COM3 is only a test fixture and is not a production configuration.
- No firmware binary is modified, converted, staged to `C:\tmp`, or rewritten.

### Post-Upload Verification
- Added verification that the UB3 re-enumerates as Maple Serial after Maple Loader completes.
- Firmware transfer complete + Maple Serial returned = `SUCCESS`.
- Firmware transfer complete + Maple Serial not returned within the verification window = `SUCCESS_WITH_WARNING`.
- Actual Maple/DFU transfer failure remains `FAILED`.

### Firmware Maintenance
- Firmware remains data-driven through the existing firmware repository and JSON metadata.
- New firmware releases require only the new `.bin` and corresponding JSON metadata; no uploader/source-code modification is required.

### Documentation
- `README.md` remains project/user documentation only and was not modified for milestone history.
- Step 5.5 implementation/history is recorded here in `CHANGELOG.md`.

## 2026-08-11 — Step 5.5 Final Runtime, Driver & Re-enumeration Baseline

### Changed

- Bundled the complete approved Windows driver package from the supplied Arduino STM32 environment.
- Included `install_drivers.bat` for Maple DFU (`1EAF:0003`) and Maple Serial (`1EAF:0004`).
- Included `install_STM_COM_drivers.bat` and the supplied STM Serial (`0483:5740`) driver resources.
- Kept the supplied Maple driver binaries, INF/CAT files, installers, and `wdi-simple.exe` unchanged.
- Removed all production dependence on `JAVA_HOME`, system Java, and the external Arduino installation.
- `maple_upload.bat` now uses only `resources/tools/maple/java/bin/java.exe`.
- The launcher uses a process-local PATH only to allow the bundled Maple runtime to locate its bundled executables; Windows system PATH is not modified.
- COM port remains runtime-detected through `DeviceService`; `COM3` is not a production configuration.
- Post-upload verification remains in `UploadService` and confirms return to Maple Serial after Maple Loader completes.
- Firmware files remain opaque artifacts; new firmware releases require only the firmware `.bin` and JSON metadata.
- README.md remains unchanged. Project history and milestone changes are recorded only in CHANGELOG.md.

### Runtime Independence

The target PC no longer needs:
- Arduino IDE
- Arduino STM32 installation
- manually configured `JAVA_HOME`
- manually added Java PATH

The updater uses its bundled Maple Loader, DFU runtime, Java runtime, and USB driver package.

### Driver Scope

Bundled driver resources cover:
- Maple DFU: `1EAF:0003`
- Maple Serial: `1EAF:0004`
- STM Serial: `0483:5740`

Driver installation is an administrative Windows operation and should be invoked by the application's installer/setup flow rather than requiring users to browse into the resource directory.

## 2026-08-11 — Step 5.5 Maple Runtime Compatibility & Post-Upload Re-enumeration

### Changed

- Rebased the bundled Maple runtime on the exact approved Arduino STM32 Windows Maple tooling supplied for this project.
- Replaced the previously bundled `dfu-util 0.9` runtime with the approved legacy `dfu-util 0.1+svn` executable and its matching `libusb0.dll`.
- Bundled the supplied Arduino Java runtime `1.8.0_191` (`i586`) under `resources/tools/maple/java/` so Maple Loader no longer depends on an Arduino installation or system Java on the target PC.
- Kept `maple_loader.jar` and `lib/jssc.jar` unchanged from the supplied approved runtime.
- Kept the existing Maple upload command contract unchanged: COM port, ALT ID `2`, DFU ID `1EAF:003`, selected firmware path.
- Added post-upload USB re-enumeration verification through the existing `DeviceService`/`UploadService` architecture.
- The updater now distinguishes firmware-transfer completion from return to normal Maple Serial operation.
- If the firmware transfer completes but the UB3 does not return to Maple Serial within the verification timeout, the result is reported as `SUCCESS_WITH_WARNING` with an explicit recovery diagnostic.
- No `.bin` firmware file is modified, converted, staged, or rewritten.
- README.md is unchanged; project milestone/history changes are recorded only in CHANGELOG.md.

### Verified

- Exact Maple Loader/JSSC binaries match the supplied Arduino STM32 runtime.
- Bundled Java version and architecture match the supplied Arduino environment.
- Existing command structure remains unchanged.
- Post-upload Maple Serial re-enumeration is verified after Maple Loader exits.
- Existing upload architecture remains `UploadService -> ProcessRunner -> maple_upload.bat -> maple_loader.jar`.
- No Python DFU uploader was introduced.

### Tests

- `tests/test_maple_runtime_step_5_5.py` — added.
- `tests/test_upload_integration.py` — updated for post-upload re-enumeration.
- No physical UB3 is programmed by the Step 5.5 software-only tests.

## 2026-08-09 — Step 5.4 Maple DFU Runtime Bundling

- Bundled the Windows `dfu-util 0.9` executable from the supplied Arduino_STM32 toolchain under `resources/tools/maple/`.
- Bundled the matching `libusb-1.0.dll` required by `dfu-util.exe`.
- Updated `maple_upload.bat` to expose the bundled DFU runtime through its local directory.
- Hardened Java resolution for `maple_loader.jar`: bundled JRE if present, `JAVA_HOME`, system `PATH`, then the legacy Arduino `%5\java\bin` location.
- Added an explicit Java-runtime pre-flight failure instead of allowing Maple Loader to fail later with an opaque process error.
- Updated Maple runtime manifest and resource validation to include the DFU runtime files.
- Preserved the existing ConfigService, DeviceService, FirmwareService, UploadService, UploadWorker, and ProcessRunner architecture.
- The supplied `Arduino_STM32.zip` contains the Maple/DFU tooling but does not contain a Java runtime; Java is therefore not yet bundled in this baseline.
- A future self-contained release can place a compatible Windows x64 JRE under `resources/tools/maple/java/` without changing the Maple command contract.

## Step 5.4 — Firmware Selection Integrity Hardening

- Strengthened controlled physical-validation coverage for firmware selection.
- Added regression coverage for every real firmware package exposed by the repository.
- Verified GUI dropdown selection returns the same real `Firmware` model object.
- Verified selected firmware paths remain inside `resources/firmware`.
- Verified selected firmware passes the existing repository validation API.
- Verified `UploadService` receives the selected firmware and passes its exact binary path to Maple Loader.
- Verified changing firmware selection cannot leak the previously selected firmware path into a new Maple command.
- Preserved the existing ConfigService, FirmwareService, DeviceService, UploadService, GUI, controller, and worker architecture.
- No physical UB3 is programmed by the new selection-integrity test.

## Step 5.4 - Controlled Physical Validation

- Added a guarded Windows physical-validation entry point.
- Safe mode performs firmware, bundled Maple runtime, device, Maple Serial, COM-port, and command pre-flight checks without programming hardware.
- Physical programming requires explicit `--program --confirm PROGRAM-UB3` and a second interactive confirmation.
- Reuses ConfigService, FirmwareService, DeviceService, UploadService, and ProcessRunner through the existing architecture.
- Added post-upload device re-enumeration verification.
- Added software-only Step 5.4 safety/architecture regression tests.
- No automatic physical programming is performed by the test suite.

# Changelog

## 2026-08-09 — Step 5.3 Process Execution and Bundled Runtime Integration

### Changed

- Hardened the existing `ProcessRunner` execution boundary for external Maple Loader processes.
- Added controlled stdout and stderr streaming through the existing upload architecture.
- Added timeout handling and process termination.
- Added cancellation handling and Windows process-tree cleanup for `cmd.exe` → batch → Java/Maple Loader execution.
- Preserved concurrent-process protection and cleanup behavior.
- Updated the upload integration test to use the bundled project Maple runtime at `resources/tools/maple/maple_upload.bat`.
- Removed the development-machine Arduino installation as a dependency of the upload integration test.
- Kept the existing `ConfigService`, `DeviceService`, `FirmwareService`, `UpdateController`, `UploadWorker`, `UploadService`, and `ProcessRunner` architecture unchanged.
- Confirmed that `C:\tmp` is not required by the application upload path.

### Verified

- Process startup and return-code propagation.
- stdout and stderr streaming.
- Working-directory propagation.
- Timeout handling.
- Cancellation.
- Concurrent execution protection.
- Process cleanup.
- Maple command argument propagation through the Windows batch boundary.
- Bundled Maple uploader resolution.

### Tests

- `tests/test_process_runner_step_5_3.py` — PASS
- `tests/test_maple_process_step_5_3.py` — PASS
- `tests/test_maple_runtime_step_5_3.py` — PASS
- Full regression suite — PASS
- No physical UB3 was programmed by the Step 5.3 regression suite.

## Step 5.2 - Maple Command Integration

- Preserved the existing device detection, controller, worker, and upload-service architecture.
- Maple command now passes the selected firmware repository path directly.
- Removed application dependence on `C:\\tmp`; that path remains only historical manual-CMD context.
- Verified exact Maple argument order: COM port, ALT ID `2`, DFU ID `1EAF:003`, firmware path.
- Added Step 5.2 command-contract regression coverage.

## Step 5.1 - Maple Runtime Resource Integration

- Added bundled Windows Maple Loader runtime resources from the supplied Arduino STM32 package.
- Added `tool_manifest.json` for runtime resource identification.
- Added `MapleResourceService` for safe pre-execution resource validation.
- Added explicit operator-action button styling for Update, Cancel, and Refresh controls.
- Added Step 5.1 resource and button-style tests.
- No physical UB3 programming is performed by Step 5.1.

# Changelog

## Step 4.5 — Live Update Progress UI

- Added a dedicated firmware update progress panel to the DashboardWidget.
- Added circular and horizontal progress indicators using the approved UB3 light-theme palette.
- Progress is phase-based and explicitly does not claim byte-level transfer accuracy.
- Added live phase mapping for preparation, Maple Loader startup, uploading, transfer completion and final success.
- Added a completion state that reaches 100% only when the UploadResult reports success.
- Added warning-aware completion styling.
- Added automatic scrolling of the live upload log.
- Added `tests/test_gui_update_progress.py`.
- No physical UB3 programming is performed by the Step 4.5 test.

## Step 4.4 — UploadWorker Progress and Live Output

- UploadWorker forwards live uploader stdout/stderr to the application.
- UpdateController wires worker progress/output callbacks into the GUI event bridge.
- Dashboard consumes textual workflow progress without fabricating byte-level percentages.
- Added `tests/test_upload_worker_streaming.py`.
- No physical UB3 programming is performed by the new test.

9 - Step 4.3 - Confirmation Final Validation Gate

- Integrated the Step 4.2 confirmation dialog into the Home page Update workflow.
- Update now performs pre-update validation before showing confirmation.
- Confirmation is followed by a mandatory second fresh device validation.
- Prevents programming if the UB3 is disconnected or replaced while the dialog is open.
- Prevents programming if the selected firmware changes after the first validation.
- Only starts `UploadWorker` after the final validation succeeds.
- Added `tests/test_confirmation_update_workflow.py`.
- Updated README with the complete safe-update workflow and current milestone status.


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

### Step 4.5 Fix — Failure Progress Visibility

- Keep the update progress card visible after failed/cancelled updates so operators retain immediate diagnostic context.
- Apply error/warning styling to the progress card and progress bar.
- Preserve the last meaningful workflow percentage instead of showing a false 100% on failure.
