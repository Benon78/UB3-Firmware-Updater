# UB3 Firmware Updater

A Windows desktop application for safely updating firmware on UB3 (Unlock Box 3) devices using the STM32 Maple Loader workflow.

## Purpose

The application provides a controlled operator workflow to:

- Automatically detect a connected UB3.
- Verify that the UB3 is in Maple Serial mode before an update.
- Automatically determine the current COM port.
- Select firmware from the project firmware repository.
- Validate the firmware before programming.
- Re-check the intended UB3 immediately before programming.
- Require explicit operator confirmation.
- Run the Maple Loader workflow without requiring manual COM-port entry.
- Display live upload progress and Maple Loader output.
- Report successful updates, non-fatal warnings, failures, cancellation, and timeouts.

The application is designed to prevent an update from being sent to a different UB3 if the original device is disconnected or replaced during the confirmation stage.

## Requirements

- Windows
- Python 3.11 or compatible supported Python version
- Project virtual environment
- Project dependencies from `requirements.txt`
- Maple Loader runtime bundled under `resources/tools/maple/`
- Firmware packages under `resources/firmware/`

The application does not require a separate Arduino STM32 installation for normal project operation.

## Project Layout

```text
UB3-Firmware-Updater/
├── main.py
├── src/
│   └── ub3_updater/
│       ├── controllers/
│       ├── models/
│       ├── services/
│       ├── themes/
│       ├── ui/
│       ├── utils/
│       └── widgets/
├── resources/
│   ├── firmware/
│   │   └── <firmware packages>
│   └── tools/
│       └── maple/
│           ├── maple_upload.bat
│           ├── maple_loader.jar
│           ├── lib/
│           │   └── jssc.jar
│           └── tool_manifest.json
├── tests/
├── logs/
├── requirements.txt
└── README.md
```

## Installing the Application for Development

From the project root:

```powershell
python -m venv .venv
.venv\Scriptsctivate
pip install -r requirements.txt
```

## Starting the Application

With the virtual environment activated:

```powershell
python main.py
```

The application is intended to be launched from the project root so the project-local resources and configuration are resolved correctly.

## Preparing Firmware

Place firmware packages in:

```text
resources/firmware/
```

Each firmware package is managed by the application's firmware repository/service.

For example:

```text
resources/firmware/
└── ZNA2US/
    ├── firmware.json
    └── UnlockBoxIII_260123_ZNA2US-WWDG2d_1.00.ino.generic_stm32f103r.bin
```

The firmware selector reads the available packages and displays the package name and version. The firmware information panel provides the available target, release, filename, size, and validation information.

The application uses the selected firmware file directly from the project firmware repository. It does not require `C:\tmp` as a production staging directory.

## Maple Loader Runtime

The application uses the bundled Maple runtime:

```text
resources/tools/maple/
├── maple_upload.bat
├── maple_loader.jar
├── lib/
│   └── jssc.jar
└── tool_manifest.json
```

The production upload path is therefore self-contained within the project.

The underlying Maple command uses the detected COM port and the established UB3 Maple parameters:

```text
maple_upload COM3 2 1EAF:003 <firmware>
```

The application automatically substitutes the actual detected COM port and selected firmware path.

Operators do not manually type the COM port into the upload command.

## Device Detection

The application automatically scans connected USB devices.

The normal starting state for an update is:

```text
Maple Serial
VID:PID = 1EAF:0004
```

The application detects the COM port from the current `Device` model.

The bootloader/USB Serial state is treated separately. Operators should not manually force the UB3 into bootloader mode before starting the normal update workflow.

## How to Perform a Firmware Update

### 1. Start the application

```powershell
python main.py
```

### 2. Connect the UB3

Connect the UB3 through USB and wait for the application to detect it.

The Home page should show:

- UB3 connection state
- COM port
- USB mode
- VID:PID
- Device information

### 3. Select firmware

Select the required firmware package and version from the firmware selector.

Review the firmware information shown by the application.

### 4. Confirm readiness

The application only enables the update action when the required device and firmware conditions are satisfied.

### 5. Start the update

Select **Update UB3**.

The application performs a fresh pre-update validation before programming.

The validation checks include:

- Device is connected.
- Device is in Maple Serial mode.
- The currently detected device matches the intended device.
- Firmware is selected.
- Firmware file exists and is valid.

### 6. Confirm the update

Review the confirmation dialog and verify the displayed device and firmware information.

The operator must explicitly acknowledge the update before programming starts.

### 7. Firmware programming

The application runs:

```text
UpdateController
    ↓
UploadWorker
    ↓
UploadService
    ↓
ProcessRunner
    ↓
maple_upload.bat
    ↓
Maple Loader
```

The GUI displays the current workflow phase and live process output.

### 8. Review the result

The application reports one of the supported result conditions, including:

- Successful update
- Successful update with a non-fatal warning
- Failed update
- Cancelled update
- Timeout
- Device-not-ready condition
- Invalid firmware

A successful firmware transfer followed by a Maple USB-reset warning can be reported as `SUCCESS_WITH_WARNING` because the programming operation itself may have completed successfully.

## Update Safety

The application blocks programming when:

- No UB3 is detected.
- The UB3 is disconnected.
- The UB3 is not in Maple Serial mode.
- A different UB3 is connected.
- No firmware is selected.
- The firmware file is missing.
- Firmware validation fails.
- The confirmed firmware identity changes.
- Another update is already running.

A fresh device scan is performed immediately before upload so a stale COM port is not reused after a USB disconnect/reconnect.

## Canceling an Update

The application provides a Cancel action while an upload is active.

Cancellation is handled through the existing upload process chain and process runner. The process is terminated and the worker reports the resulting cancellation state.

Do not disconnect the UB3 intentionally during programming unless performing an approved hardware-recovery test.

## Logs

Application logs are stored under:

```text
logs/
```

The GUI also provides live upload output during programming.

## Testing

The project contains automated regression tests for the GUI, device handling, firmware validation, upload worker, Maple command generation, Maple resources, and process execution.

Activate the environment:

```powershell
.venv\Scripts\activate
```

Run an individual test:

```powershell
python tests/test_gui.py
```

Run the complete regression suite from the project root:

```powershell
$tests = @(
    "tests/test_gui.py",
    "tests/test_gui_device_information.py",
    "tests/test_gui_layout.py",
    "tests/test_gui_firmware_selection.py",
    "tests/test_gui_update_progress.py",
    "tests/test_pre_update_validation.py",
    "tests/test_upload_worker.py",
    "tests/test_upload_worker_streaming.py",
    "tests/test_maple_resources.py",
    "tests/test_maple_command_contract.py",
    "tests/test_upload_service.py",
    "tests/test_upload_integration.py",
    "tests/test_process_runner_step_5_3.py",
    "tests/test_maple_process_step_5_3.py",
    "tests/test_maple_runtime_step_5_3.py"
)

foreach ($test in $tests) {
    Write-Host "RUNNING: $test"
    python $test

    if ($LASTEXITCODE -ne 0) {
        Write-Host "FAILED: $test" -ForegroundColor Red
        exit $LASTEXITCODE
    }

    Write-Host "PASSED: $test" -ForegroundColor Green
}
```

Unless a test is explicitly identified as a hardware test, the regression suite does not program a physical UB3.

## Development Architecture

The application keeps hardware access and GUI responsibilities separated:

```text
HomePage
   ↓
UpdateController
   ├── DeviceMonitor
   ├── DeviceService
   ├── FirmwareService
   └── UploadWorker
           ↓
       UploadService
           ↓
       ProcessRunner
           ↓
       Maple Loader
```

The GUI does not execute Maple Loader directly.

Device detection remains centralized in the existing device services and models. Firmware discovery remains centralized in the firmware service and repository. Upload execution remains isolated in the upload worker/service and process runner.

## Troubleshooting

### UB3 is not detected

Check:

1. USB cable and connection.
2. Windows Device Manager.
3. Whether the UB3 appears as the expected Maple Serial device.
4. Whether another application has opened the COM port.
5. Use the Home page **Refresh** action.

### Update is disabled

Check that:

- A UB3 is detected.
- The device is in Maple Serial mode.
- Firmware is selected.
- The selected firmware passes validation.

### Maple Loader cannot be found

Verify:

```text
resources/tools/maple/maple_upload.bat
resources/tools/maple/maple_loader.jar
resources/tools/maple/lib/jssc.jar
```

are present.

### Firmware cannot be found

Verify that the selected firmware exists under:

```text
resources/firmware/
```

and that its repository metadata references the correct binary file.

## Operational Notes

- Do not manually enter a COM port for normal operation.
- Do not manually force the UB3 into DFU/bootloader mode before starting an update.
- Verify the selected firmware before confirming the update.
- Do not disconnect the UB3 during programming unless intentionally performing a controlled recovery test.
- Use the bundled Maple runtime for normal application operation.
- Keep firmware packages and their metadata together in the firmware repository.
