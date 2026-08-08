"""
=========================================================
UB3 Device Manager

Configuration Service

Developer:
Benjamin William

Version:
0.2.0

Description:
Loads and provides access to all JSON configuration
files used throughout the application.
=========================================================
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigService:
    """Loads application configuration."""

    PROJECT_ROOT = Path(__file__).resolve().parents[3]

    CONFIG_DIR = PROJECT_ROOT / "config"

    APP_CONFIG = CONFIG_DIR / "app_config.json"

    SETTINGS = CONFIG_DIR / "settings.json"

    FIRMWARE = CONFIG_DIR / "firmware.json"

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:

        if not path.exists():
            raise FileNotFoundError(f"Missing configuration file: {path}")

        with open(path, "r", encoding="utf-8") as file:

            return json.load(file)

    @classmethod
    def app(cls):

        return cls._load_json(cls.APP_CONFIG)

    @classmethod
    def settings(cls):

        return cls._load_json(cls.SETTINGS)

    @classmethod
    def firmware(cls):

        return cls._load_json(cls.FIRMWARE)