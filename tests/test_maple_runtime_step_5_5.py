
"""
STEP 5.5 - MAPLE RUNTIME COMPATIBILITY &
POST-UPLOAD RE-ENUMERATION TEST

No physical UB3 is programmed.
"""

from pathlib import Path
import hashlib
import json

import bootstrap

from ub3_updater.models.device import Device, DeviceState
from ub3_updater.models.firmware import Firmware
from ub3_updater.models.upload_result import UploadStatus
from ub3_updater.services.config_service import ConfigService
from ub3_updater.services.maple_resource_service import MapleResourceService
from ub3_updater.services.upload_service import UploadService
from ub3_updater.utils.process_runner import ProcessResult


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAPLE_ROOT = ConfigService.maple_tools_root().resolve()
MANIFEST = MAPLE_ROOT / "tool_manifest.json"
UPLOADER = MAPLE_ROOT / "maple_upload.bat"
MAPLE_LOADER = MAPLE_ROOT / "maple_loader.jar"
JSSC = MAPLE_ROOT / "lib" / "jssc.jar"
DFU = MAPLE_ROOT / "dfu-util.exe"
LIBUSB = MAPLE_ROOT / "libusb0.dll"
JAVA = MAPLE_ROOT / "java" / "bin" / "java.exe"
JAVA_CLIENT_JVM = MAPLE_ROOT / "java" / "bin" / "client" / "jvm.dll"
JAVA_RELEASE = MAPLE_ROOT / "java" / "release"
DRIVERS_ROOT = MAPLE_ROOT / "drivers" / "win"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def make_device() -> Device:
    return Device(
        connected=True,
        state=DeviceState.MAPLE_SERIAL,
        com_port="COM3",
        usb_name="Maple Serial (COM3)",
        description="Maple Serial (COM3)",
        manufacturer="LeafLabs, LLC",
        vid="1EAF",
        pid="0004",
    )


class FakeDeviceService:
    def __init__(self, states):
        self.states = list(states)
        self.scan_count = 0

    def scan(self):
        self.scan_count += 1
        if self.states:
            return self.states.pop(0)
        return Device(
            connected=False,
            state=DeviceState.DISCONNECTED,
        )


class FakeFirmwareService:
    def validate(self, firmware):
        return True, None


class FakeProcessRunner:
    def __init__(self, stdout, stderr="", return_code=0):
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code
        self.last_command = None
        self.run_count = 0

    def run(self, command, cwd=None, timeout=None,
            on_output=None, on_error=None):
        self.run_count += 1
        self.last_command = list(command)

        if on_output:
            for line in self.stdout.splitlines():
                if line.strip():
                    on_output(line.strip())

        if on_error:
            for line in self.stderr.splitlines():
                if line.strip():
                    on_error(line.strip())

        return ProcessResult(
            command=list(command),
            return_code=self.return_code,
            stdout=self.stdout,
            stderr=self.stderr,
            started=True,
            duration_seconds=0.1,
        )


def make_service(device_states, stdout, stderr="", return_code=0):
    return UploadService(
        device_service=FakeDeviceService(device_states),
        firmware_service=FakeFirmwareService(),
        process_runner=FakeProcessRunner(
            stdout=stdout,
            stderr=stderr,
            return_code=return_code,
        ),
        uploader_path=UPLOADER,
        timeout=5,
    )


def firmware() -> Firmware:
    fixture = PROJECT_ROOT / "tests" / "fixtures" / "step55_test.bin"
    fixture.parent.mkdir(parents=True, exist_ok=True)
    if not fixture.exists():
        fixture.write_bytes(b"STEP-5.5-TEST-FIRMWARE")
    return Firmware(
        name="TEST",
        version="1.00",
        path=str(fixture),
    )


SUCCESS_OUTPUT = """
maple_loader v0.1
Resetting to bootloader via DTR pulse
Searching for DFU device [1EAF:003]...
Found it!
Starting download: [##################################################] finished!
Done!
Resetting USB to switch back to runtime mode
"""

FAIL_OUTPUT = """
maple_loader v0.1
Resetting to bootloader via DTR pulse
Searching for DFU device [1EAF:003]...
Couldn't find the DFU device: [1EAF:003]
"""


print("=" * 70)
print("STEP 5.5 - MAPLE RUNTIME COMPATIBILITY & POST-UPLOAD")
print("=" * 70)

validation = MapleResourceService(MAPLE_ROOT).validate()
assert validation.valid, (
    "Bundled Maple runtime validation failed: "
    f"{validation.message} {validation.missing_files}"
)
print("[PASS] Bundled approved Maple runtime is complete")

for path in (UPLOADER, MAPLE_LOADER, JSSC, DFU, LIBUSB, JAVA, JAVA_CLIENT_JVM, JAVA_RELEASE):
    assert path.is_file(), f"Missing runtime file: {path}"
print("[PASS] Required Maple/Java runtime files exist")

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
for relative in manifest["driver_required_files"]:
    assert (MAPLE_ROOT / relative).is_file(), (
        f"Missing bundled driver resource: {relative}"
    )
print("[PASS] Complete bundled Maple/STM USB driver package exists")
assert manifest["java_bundled"] is True
assert manifest["java_resolution_order"] == [
    "resources/tools/maple/java/bin/java.exe"
]
assert manifest["java_version"] == "1.8.0_191"
assert manifest["dfu_util_version"] == "0.1+svn"
assert "java/bin/java.exe" in manifest["required_files"]
assert "java/bin/client/jvm.dll" in manifest["required_files"]
assert "java/bin/server/jvm.dll" not in manifest["required_files"]
print("[PASS] Runtime manifest identifies bundled Java and legacy DFU")

release = JAVA_RELEASE.read_text(encoding="utf-8", errors="replace")
assert 'JAVA_VERSION="1.8.0_191"' in release
assert 'OS_ARCH="i586"' in release
print("[PASS] Bundled Java version/architecture validated")

EXPECTED = {
    "maple_loader.jar": "2304e30578ce47c2e607a2f98d3b59f6eb91358bf3fefcefb15ff161b1e61018",
    "lib/jssc.jar": "be0792d66354213b245f434adddb008597d03d5ad65225d4c5f37cb3982d5227",
    "dfu-util.exe": "dfde44fba517bad8eb72e1074cb8621d931a0b56a8d2e1c9c854156e1dec3afd",
    "libusb0.dll": "ee7c1b141bee34a4b1d819ed48c84c859e8dd44bcae577b456f60e3fc359c80c",
}
for relative, expected_hash in EXPECTED.items():
    actual = sha256(MAPLE_ROOT / relative)
    assert actual.lower() == expected_hash.lower(), (
        f"Runtime hash mismatch for {relative}: {actual}"
    )
print("[PASS] Maple runtime binaries match supplied Arduino environment")

service = make_service([make_device(), make_device()], SUCCESS_OUTPUT)
result = service.upload(firmware())
command = result.command

assert command[0] == "cmd.exe"
assert command[1] == "/d"
assert command[2] == "/c"
assert command[3] == "call"
assert command[4] == str(UPLOADER)
assert command[5] == "COM3"
assert command[6] == "2"
assert command[7] == "1EAF:003"
assert command[8].endswith("step55_test.bin")
print("[PASS] Exact Maple upload command contract unchanged")

assert result.status == UploadStatus.SUCCESS
assert result.success is True
assert result.has_warning is False
print("[PASS] Firmware transfer + Maple Serial re-enumeration = SUCCESS")

no_return = Device(connected=False, state=DeviceState.DISCONNECTED)
service = make_service([make_device(), no_return], SUCCESS_OUTPUT)
service.POST_UPLOAD_REENUMERATION_TIMEOUT = 0.10
service.POST_UPLOAD_REENUMERATION_INTERVAL = 0.02
result = service.upload(firmware())

assert result.status == UploadStatus.SUCCESS_WITH_WARNING
assert result.success is True
assert "did not return to Maple Serial" in result.message
print("[PASS] Transfer-complete/no-re-enumeration reported as warning")

service = make_service([make_device()], FAIL_OUTPUT)
result = service.upload(firmware())
assert result.status == UploadStatus.FAILED
assert result.success is False
print("[PASS] Incomplete DFU transfer remains FAILED")

source = (
    PROJECT_ROOT / "src" / "ub3_updater" / "services" /
    "upload_service.py"
).read_text(encoding="utf-8")

assert "cmd.exe" in source
assert 'MAPLE_ALT_ID = "2"' in source
assert 'MAPLE_DFU_ID = "1EAF:003"' in source
assert "ProcessRunner" in source
assert "maple_upload.bat" in source
assert "dfu-util" not in source.lower()
print("[PASS] Existing upload architecture remains unchanged")

batch_source = UPLOADER.read_text(encoding="utf-8", errors="replace")
assert "JAVA_HOME" not in batch_source
assert "where java" not in batch_source
assert "%~5" not in batch_source
assert "java\\bin\\java.exe" in batch_source
print("[PASS] Maple launcher is independent of JAVA_HOME, system Java, and Arduino")

assert "C:\\tmp" not in source
assert "COM3" not in source
print("[PASS] Production upload code does not hardcode COM3 or C:\\tmp")

print()
print("=" * 70)
print("ALL STEP 5.5 TESTS PASSED")
print("=" * 70)
print()
print("No physical UB3 was programmed.")
