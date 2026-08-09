"""
Maple runtime resource validation.

Step 5.1 only validates bundled runtime resources.
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
    """Validate the bundled Windows Maple Loader runtime."""

    REQUIRED_FILES = (
        "maple_upload.bat",
        "maple_loader.jar",
        "lib/jssc.jar",
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

        return MapleResourceValidation(
            valid=True,
            message="Maple Loader runtime resources are available.",
        )
