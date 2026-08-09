## Step 4.5 — Live Update Progress UI

The GUI now presents a dedicated operator-facing update progress panel while firmware programming is active.

- Added a circular workflow progress indicator and a horizontal progress bar.
- Progress values represent verified workflow phases, not transferred bytes.
- The UI never fabricates a byte-level percentage because Maple Loader does not expose a trustworthy numeric transfer percentage through the current integration.
- Workflow phases include Preparing (10%), Starting (25%), Uploading (60%), Finalizing (85%), and Complete (100%).
- Live controller progress messages and recognized Maple Loader output update the progress presentation.
- The active update keeps the Update button disabled and Cancel available.
- Successful updates retain a 100% completion summary; failures do not present a misleading completion percentage.
- The upload log automatically follows the newest live output.
- Added `tests/test_gui_update_progress.py`.
- No physical UB3 is programmed by the Step 4.5 GUI test.

## Step 4.4 — UploadWorker Progress and Live Output

The application receives UploadWorker lifecycle/progress events and live Maple Loader output without blocking the UI.

- UploadWorker forwards `UploadService` stdout/stderr through callbacks.
- UpdateController forwards worker output to the GUI signal bridge.
- Dashboard consumes textual progress phases without inventing byte-level transfer progress.
- Upload/Cancel controls remain locked to the active operation state.
- The Step 4.4 streaming test uses a fake upload service and never programs a physical UB3.

# UB3 Firmware Updater

A Windows desktop application for safely updating UB3 firmware using the existing Arduino STM32 / Maple Loader upload environment.

## Purpose

The application provides a controlled operator workflow for:

- Detecting UB3 devices automatically.
- Verifying the device is in Maple Serial mode before programming.
- Selecting firmware from the local firmware repository.
- Validating firmware files before programming.
- Re-validating the intended UB3 immediately before upload.
- Showing the operator exactly which device and firmware will be programmed.
- Requiring explicit confirmation before programming.
- Running firmware programming through `UploadWorker` → `UploadService` → Maple Loader.
- Reporting success, warnings, failures, cancellation and timeout states.

The application is designed so that replacing a UB3 while the confirmation dialog is open cannot silently result in programming the replacement device.

## Technology

- Python
- PySide6
- Arduino STM32
- Maple Loader / `maple_upload.bat`
- Local firmware repository
- Windows USB/serial device detection

## Architecture

```text
GUI
 │
 ▼
HomePage
 │
 ▼
UpdateController
 │
 ├── DeviceMonitor
 ├── FirmwareService
 └── UploadWorker
       │
       ▼
   UploadService
       │
       ▼
   ProcessRunner
       │
       ▼
 maple_upload.bat
```

The GUI does not execute Maple Loader directly.

## Safe Update Workflow

```text
UB3 detected
    ↓
Firmware selected
    ↓
Update
    ↓
Pre-update validation
    ↓
Confirmation dialog
    ↓
Operator acknowledgement
    ↓
SECOND / FINAL validation
    ↓
UploadWorker
    ↓
UploadService
    ↓
Maple Loader
    ↓
UploadResult
    ↓
GUI result state
```

### Why two validations?

The first validation establishes the device and firmware shown to the operator.

The confirmation dialog can remain open while the physical USB device changes. Therefore, after the operator confirms, the controller performs a second fresh scan.

If the intended UB3 has been:

- disconnected,
- replaced by another UB3,
- switched out of Maple Serial mode,

the upload is blocked.

The controller also protects the confirmed firmware identity from changing while the confirmation dialog is open.

## GUI

The Home page uses a two-column operator layout:

### Left column

- Connection Status
- Refresh control
- Device Information
- Operator instructions

### Right column

- Firmware selection
- Firmware details
- Update controls
- Upload status/log information

Both columns have independent vertical scrolling so the interface does not compress sections into each other on smaller windows.

Update and Cancel actions use the application primary blue/white action styling.

## Firmware Repository

Firmware packages are loaded from the configured local firmware repository.

The firmware selector displays:

- Package name
- Version

The firmware information area displays available metadata such as:

- Target device
- Release date
- Filename
- File size
- Validation status

The application does not fabricate unavailable device or firmware metadata.

## Safety Controls

The following conditions block programming:

- No UB3 connected.
- UB3 is not in Maple Serial mode.
- Intended UB3 was replaced.
- Intended UB3 was disconnected.
- No firmware selected.
- Firmware file does not exist.
- Firmware file is invalid.
- Firmware identity changes after confirmation.
- Another upload is already running.

## Development Milestones

### Foundation

- [x] Project structure
- [x] Configuration system
- [x] Firmware repository/service
- [x] Device detection
- [x] Maple Loader upload service
- [x] UploadResult model
- [x] ProcessRunner
- [x] UploadWorker
- [x] UpdateController

### GUI

- [x] Main Window
- [x] Connection Status
- [x] Device Information
- [x] Firmware Selection
- [x] Firmware version display
- [x] Refresh action
- [x] High-contrast Update/Cancel controls
- [x] Independent Home page scrolling

### Safe Update Workflow

- [x] Step 4.1 — Pre-update safety validation
- [x] Step 4.2 — Operator confirmation dialog
- [x] Step 4.3 — Confirmation → second validation → UploadWorker gate
- [x] Step 4.4 — UploadWorker progress/status integration
- [x] Step 4.5 — Live progress UI with success/warning/failure presentation
- [ ] Step 4.6 — Cancellation workflow
- [ ] Step 4.7 — Disconnect handling during programming
- [ ] Step 4.8 — Full end-to-end GUI integration tests
- [ ] Step 4.9 — Controlled physical UB3 test
- [ ] Step 4.10 — Release packaging and deployment

## Testing

Tests are designed to run without programming a physical UB3 unless a test is explicitly marked as a real hardware test.

Current regression tests include:

```text
tests/test_gui.py
tests/test_gui_device_information.py
tests/test_gui_layout.py
tests/test_gui_firmware_selection.py
tests/test_update_controller.py
tests/test_pre_update_validation.py
tests/test_update_confirmation_dialog.py
tests/test_confirmation_update_workflow.py
tests/test_upload_worker_streaming.py
tests/test_gui_update_progress.py
```

Expected test environment:

```powershell
.venv\Scripts\activate
python tests/test_gui.py
```

Run the individual regression tests before committing changes.

## Current Status

**Safe update workflow through Step 4.5 is implemented and under test.**

No physical UB3 should be programmed during unit or GUI regression testing.

## Developer

Benjamin William
