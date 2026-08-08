"""
=========================================================
UB3 Firmware Updater

Device Monitor Worker

Developer:
Benjamin William
=========================================================
"""

from PySide6.QtCore import (
    QObject,
    Signal,
    QTimer,
)

from ub3_updater.services.device_service import DeviceService


class DeviceMonitor(QObject):

    device_changed = Signal(object)

    def __init__(self):

        super().__init__()

        self.service = DeviceService()

        self.timer = QTimer()

        self.timer.timeout.connect(self.check_device)

        self.previous_state = None

    # ------------------------------------

    def start(self):

        """
        Starts monitoring every second.
        """

        self.timer.start(1000)

    # ------------------------------------

    def stop(self):

        self.timer.stop()

    # ------------------------------------

    def check_device(self):

        device = self.service.get_device()

        if device != self.previous_state:

            self.previous_state = device

            self.device_changed.emit(device)