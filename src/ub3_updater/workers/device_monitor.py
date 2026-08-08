"""
=========================================================
UB3 Firmware Updater

Device Monitor Worker

Developer:
Benjamin William

Description:
Continuously monitors USB devices and emits signals when
the device state changes.

Version:
0.3.0
=========================================================
"""

from PySide6.QtCore import QObject, Signal, QTimer

from ub3_updater.models.device import DeviceState
from ub3_updater.services.device_service import DeviceService
from ub3_updater.services.logger_service import LoggerService


class DeviceMonitor(QObject):

    # --------------------------------------------
    # Signals
    # --------------------------------------------

    device_changed = Signal(object)

    device_connected = Signal(object)

    device_disconnected = Signal()

    runtime_detected = Signal(object)

    dfu_detected = Signal(object)

    # --------------------------------------------

    def __init__(self):

        super().__init__()

        self.service = DeviceService()

        self.timer = QTimer()

        self.timer.timeout.connect(self.check_device)

        self.previous_device = None
        self.current_device = None

    # --------------------------------------------

    def start(self, interval=500):
        """
        Start monitoring.
        """
        self.timer.start(interval)

    # --------------------------------------------

    def stop(self):

        self.timer.stop()

    # --------------------------------------------

    def check_device(self):

        self.current_device = self.service.scan()
        device = self.current_device

        # First detection
        if self.previous_device is None:

            self.previous_device = device

            if device.connected:
                self.device_connected.emit(device)

                if device.is_runtime:
                    self.runtime_detected.emit(device)

                elif device.is_dfu:
                    self.dfu_detected.emit(device)

            self.device_changed.emit(device)

            return

        # ------------------------------------------------
        # Connected
        # ------------------------------------------------

        if (not self.previous_device.connected) and device.connected:

            LoggerService.info(
                f"Device Connected ({device.com_port})"
            )

            self.device_connected.emit(device)

        # ------------------------------------------------
        # Disconnected
        # ------------------------------------------------

        elif self.previous_device.connected and (not device.connected):
            LoggerService.info("Device Disconnected")
            self.device_disconnected.emit()

        # ------------------------------------------------
        # Runtime → DFU
        # ------------------------------------------------

        elif (
            self.previous_device.state != device.state
        ):

            if device.state == DeviceState.RUNTIME:
                LoggerService.info(
                    f"Runtime Mode ({device.com_port})"
                )
                self.runtime_detected.emit(device)

            elif device.state == DeviceState.DFU:
                LoggerService.info(
                    f"DFU Bootloader ({device.com_port})"
                )
                self.dfu_detected.emit(device)

        # ------------------------------------------------

        if not device.same_device(self.previous_device):

            self.previous_device = device

            self.device_changed.emit(device)