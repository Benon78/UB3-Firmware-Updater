@echo off
setlocal

rem ================================================================
rem UB3 Firmware Updater - Bundled Maple Loader Runtime
rem
rem The upload command contract is intentionally unchanged:
rem
rem     maple_upload <COM> <ALT-ID> <DFU-ID> <firmware.bin>
rem
rem Java is PRIVATE to this process and is always taken from the
rem bundled runtime. No JAVA_HOME or system Java is required.
rem ================================================================

set "MAPLE_DIR=%~dp0"
set "MAPLE_JAVA=%MAPLE_DIR%java\bin\java.exe"

if not exist "%MAPLE_JAVA%" (
    echo ERROR: Bundled Java runtime not found.
    echo Expected: %MAPLE_JAVA%
    exit /b 2
)

if not exist "%MAPLE_DIR%dfu-util.exe" (
    echo ERROR: Bundled dfu-util.exe not found.
    exit /b 3
)

if not exist "%MAPLE_DIR%libusb0.dll" (
    echo ERROR: Bundled libusb0.dll not found.
    exit /b 4
)

if not exist "%MAPLE_DIR%maple_loader.jar" (
    echo ERROR: maple_loader.jar not found.
    exit /b 5
)

if not exist "%MAPLE_DIR%lib\jssc.jar" (
    echo ERROR: lib\jssc.jar not found.
    exit /b 6
)

rem Process-local PATH only. This does NOT modify Windows PATH.
set "PATH=%MAPLE_DIR%;%MAPLE_DIR%java\bin;%PATH%"

cd /d "%MAPLE_DIR%"

rem IMPORTANT:
rem Keep the Maple Loader arguments unchanged.
"%MAPLE_JAVA%" -jar "%MAPLE_DIR%maple_loader.jar" %1 %2 %3 %4
set "MAPLE_LOADER_EXIT=%ERRORLEVEL%"

exit /b %MAPLE_LOADER_EXIT%
