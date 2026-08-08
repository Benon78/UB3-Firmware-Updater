import bootstrap

from ub3_updater.services.logger_service import LoggerService

LoggerService.info("Application started")

LoggerService.info("Searching COM ports")

LoggerService.warning("No UB3 detected")

LoggerService.error("DFU device not found")

print("Logger Test Completed")