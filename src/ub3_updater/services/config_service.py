"""
=========================================================
UB3 Firmware Updater

Configuration Service

Purpose
-------
Central configuration access for the application.

Configuration files:

    config/app_config.json
    config/settings.json
    config/firmware.json

Path configuration is resolved relative to the project
root, not the current working directory.

This allows the application to be started from:

    PowerShell
    CMD
    IDE
    packaged executable

without changing resource paths.

=========================================================
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigService:
    """
    Central service for application configuration.
    """

    # =====================================================
    # PROJECT ROOT
    # =====================================================

    PROJECT_ROOT = (
        Path(__file__)
        .resolve()
        .parents[3]
    )

    # =====================================================
    # CONFIGURATION DIRECTORY
    # =====================================================

    CONFIG_DIR = (
        PROJECT_ROOT
        / "config"
    )

    APP_CONFIG = (
        CONFIG_DIR
        / "app_config.json"
    )

    SETTINGS = (
        CONFIG_DIR
        / "settings.json"
    )

    FIRMWARE = (
        CONFIG_DIR
        / "firmware.json"
    )

    # =====================================================
    # JSON LOADER
    # =====================================================

    @staticmethod
    def _load_json(
        path: Path,
    ) -> dict[str, Any]:

        if not path.exists():

            raise FileNotFoundError(
                f"Missing configuration file: {path}"
            )

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if not isinstance(
            data,
            dict,
        ):

            raise ValueError(
                f"Configuration must be a JSON object: "
                f"{path}"
            )

        return data

    # =====================================================
    # Application Configuration
    # =====================================================

    @classmethod
    def app(cls) -> dict[str, Any]:

        return cls._load_json(
            cls.APP_CONFIG
        )

    # =====================================================
    # Settings
    # =====================================================

    @classmethod
    def settings(cls) -> dict[str, Any]:

        return cls._load_json(
            cls.SETTINGS
        )

    # =====================================================
    # Firmware Configuration
    # =====================================================

    @classmethod
    def firmware(cls) -> dict[str, Any]:

        return cls._load_json(
            cls.FIRMWARE
        )

    # =====================================================
    # Paths Configuration
    # =====================================================

    @classmethod
    def paths(cls) -> dict[str, Path]:
        """
        Resolve configured application paths.

        Paths in app_config.json are relative to the
        project root.
        """

        config = cls.app()

        configured_paths = (
            config.get(
                "paths",
                {},
            )
        )

        if not isinstance(
            configured_paths,
            dict,
        ):

            raise ValueError(
                "Application 'paths' configuration "
                "must be an object."
            )

        resolved = {}

        for name, value in configured_paths.items():

            path = Path(
                str(value)
            )

            if not path.is_absolute():

                path = (
                    cls.PROJECT_ROOT
                    / path
                )

            resolved[name] = (
                path.resolve()
            )

        return resolved

    # =====================================================
    # Single Path
    # =====================================================

    @classmethod
    def path(
        cls,
        name: str,
    ) -> Path:
        """
        Return one configured application path.

        Example:

            ConfigService.path("firmware")

        """

        paths = cls.paths()

        if name not in paths:

            raise KeyError(
                f"Configured path does not exist: "
                f"{name}"
            )

        return paths[name]

    # =====================================================
    # Firmware Directory
    # =====================================================

    @classmethod
    def firmware_root(cls) -> Path:
        """
        Return the root firmware directory.
        """

        return cls.path(
            "firmware"
        )

    # =====================================================
    # Tools Directory
    # =====================================================

    @classmethod
    def tools_root(cls) -> Path:
        """
        Return the root tools directory.
        """

        return cls.path(
            "tools"
        )

    # =====================================================
    # Maple Tools Directory
    # =====================================================

    @classmethod
    def maple_tools_root(cls) -> Path:
        """
        Return the project-local Maple tools directory.

        Expected future location:

            resources/tools/maple/
        """

        return (
            cls.tools_root()
            / "maple"
        )

    # =====================================================
    # Maple Uploader
    # =====================================================

    @classmethod
    def maple_uploader(
        cls,
    ) -> Path:
        """
        Return the project-local Maple uploader path.

        Expected future location:

            resources/tools/maple/maple_upload.bat
        """

        return (
            cls.maple_tools_root()
            / "maple_upload.bat"
        )

    # =====================================================
    # Logs Directory
    # =====================================================

    @classmethod
    def logs_root(cls) -> Path:

        return cls.path(
            "logs"
        )

    # =====================================================
    # Drivers Directory
    # =====================================================

    @classmethod
    def drivers_root(cls) -> Path:

        return cls.path(
            "drivers"
        )

    # =====================================================
    # Configuration Summary
    # =====================================================

    @classmethod
    def path_summary(
        cls,
    ) -> dict[str, str]:
        """
        Return resolved paths for diagnostics.
        """

        paths = cls.paths()

        summary = {
            name: str(path)
            for name, path in paths.items()
        }

        summary[
            "maple"
        ] = str(
            cls.maple_tools_root()
        )

        summary[
            "maple_uploader"
        ] = str(
            cls.maple_uploader()
        )

        return summary