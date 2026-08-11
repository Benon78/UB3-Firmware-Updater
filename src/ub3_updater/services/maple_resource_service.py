"""
Maple runtime resource validation.

Step 5.1/5.5 validates the bundled runtime resources.
It does not execute Maple Loader and does not access a physical UB3.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class MapleResourceValidation:
    valid: bool
    message: str
    missing_files: tuple[str, ...] = ()


class MapleResourceService:
    """Validate the approved self-contained Windows Maple Loader runtime."""

    REQUIRED_FILES = (
        "maple_upload.bat",
        "maple_loader.jar",
        "lib/jssc.jar",
        "dfu-util.exe",
        "libusb0.dll",
        "java/bin/java.exe",
        "java/bin/client/jvm.dll",
        "java/lib/rt.jar",
        "java/release",
        "tool_manifest.json",
    )

    def __init__(self, resource_root: Path | None = None) -> None:
        if resource_root is None:
            resource_root = (
                Path(__file__).resolve().parents[3]
                / "resources"
                / "tools"
                / "maple"
            )

        self.resource_root = Path(resource_root)

    def resolve_java(self) -> Path | None:
        """Resolve only the Java runtime bundled with the application.

        The updater is self-contained. JAVA_HOME, system PATH Java,
        and an external Arduino installation are intentionally ignored.
        """
        bundled = self.resource_root / "java" / "bin" / "java.exe"

        if bundled.is_file():
            return bundled.resolve()

        return None

    def validate(self) -> MapleResourceValidation:
        missing = tuple(
            relative
            for relative in self.REQUIRED_FILES
            if not (self.resource_root / relative).is_file()
        )

        if missing:
            return MapleResourceValidation(
                valid=False,
                message="Maple Loader runtime is incomplete.",
                missing_files=missing,
            )

        manifest_path = self.resource_root / "tool_manifest.json"

        try:
            manifest = json.loads(
                manifest_path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            return MapleResourceValidation(
                valid=False,
                message="Maple Loader manifest is invalid.",
                missing_files=(),
            )

        required_files = tuple(
            manifest.get("required_files", ())
        )

        manifest_missing = tuple(
            relative
            for relative in required_files
            if not (self.resource_root / relative).is_file()
        )

        if manifest_missing:
            return MapleResourceValidation(
                valid=False,
                message="Maple Loader manifest requirements are incomplete.",
                missing_files=manifest_missing,
            )

        driver_files = tuple(
            manifest.get("driver_required_files", ())
        )

        driver_missing = tuple(
            relative
            for relative in driver_files
            if not (self.resource_root / relative).is_file()
        )

        if driver_missing:
            return MapleResourceValidation(
                valid=False,
                message="Bundled UB3 Windows USB driver package is incomplete.",
                missing_files=driver_missing,
            )

        release_path = self.resource_root / "java" / "release"

        try:
            release_text = release_path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        except OSError:
            return MapleResourceValidation(
                valid=False,
                message="Bundled Java runtime metadata could not be read.",
                missing_files=("java/release",),
            )

        expected_java = manifest.get("java_version")

        if (
            expected_java
            and f'JAVA_VERSION="{expected_java}"'
            not in release_text
        ):
            return MapleResourceValidation(
                valid=False,
                message=(
                    "Bundled Java runtime version does not match "
                    f"the manifest requirement ({expected_java})."
                ),
                missing_files=(),
            )

        return MapleResourceValidation(
            valid=True,
            message="Approved self-contained Maple Loader runtime is available.",
        )
