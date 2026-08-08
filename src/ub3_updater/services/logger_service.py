"""
=========================================================
UB3 Device Manager

Logger Service

Developer:
Benjamin William

Version:
0.2.0
=========================================================
"""

from pathlib import Path
import logging

from ub3_updater.services.config_service import ConfigService


class LoggerService:

    _logger = None

    @classmethod
    def get_logger(cls):

        if cls._logger is not None:
            return cls._logger

        app_cfg = ConfigService.app()

        project_root = Path(__file__).resolve().parents[3]

        log_folder = project_root / app_cfg["paths"]["logs"]

        log_folder.mkdir(exist_ok=True)

        log_file = log_folder / "updater.log"

        logger = logging.getLogger("UB3")

        logger.setLevel(logging.INFO)

        logger.handlers.clear()

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )

        # File Handler
        file_handler = logging.FileHandler(
            log_file,
            encoding="utf-8"
        )

        file_handler.setFormatter(formatter)

        # Console Handler
        console_handler = logging.StreamHandler()

        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        logger.addHandler(console_handler)

        cls._logger = logger

        return logger

    @classmethod
    def info(cls, message):

        cls.get_logger().info(message)

    @classmethod
    def warning(cls, message):

        cls.get_logger().warning(message)

    @classmethod
    def error(cls, message):

        cls.get_logger().error(message)

    @classmethod
    def debug(cls, message):

        cls.get_logger().debug(message)