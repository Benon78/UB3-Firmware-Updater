"""Pre-update validation result model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ub3_updater.models.device import Device
from ub3_updater.models.firmware import Firmware


@dataclass(frozen=True, slots=True)
class PreUpdateValidationResult:
    """Result of the final safety validation before programming."""

    valid: bool
    message: str
    device: Device | None = None
    firmware: Firmware | None = None
    checks: dict[str, bool] = field(default_factory=dict)

    @property
    def failed(self) -> bool:
        return not self.valid

    def check_passed(self, name: str) -> bool:
        return bool(self.checks.get(name, False))

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "message": self.message,
            "device": (
                self.device.to_dict()
                if self.device
                else None
            ),
            "firmware": (
                self.firmware.to_dict()
                if self.firmware
                else None
            ),
            "checks": dict(self.checks),
        }
    