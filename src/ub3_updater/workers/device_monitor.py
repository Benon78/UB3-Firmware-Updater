"""
=========================================================
UB3 Firmware Updater

Device Monitor

Developer:
Benjamin William

Description:
Monitors hardware changes and publishes events.

Responsibilities
----------------
• Poll DeviceService
• Detect connection changes
• Detect hardware state changes
• Publish Qt signals

This class NEVER:
• Detects USB VID/PID
• Uploads firmware
• Controls the UI

Version:
0.4.0
=========================================================
"""

from PySide6.QtCore import QObject, Signal, QTimer

from ub3_updater.models.device import Device
from ub3_updater.models.device import DeviceState
from ub3_updater.services.device_service import DeviceService


class DeviceMonitor(QObject):

    # -------------------------------------------------
    # Signals
    # -------------------------------------------------

    device_changed = Signal(object)

    device_connected = Signal(object)

    device_disconnected = Signal()

    maple_detected = Signal(object)

    bootloader_detected = Signal(object)

    state_changed = Signal(object, object)

    # -------------------------------------------------

    def __init__(self):

        super().__init__()

        self.service = DeviceService()

        self.timer = QTimer()

        self.timer.timeout.connect(self.check_device)

        self.previous_device = Device()

        self.current_device = Device()

        self._paused = False

    # -------------------------------------------------
    # Control
    # -------------------------------------------------

    def start(self, interval=500):

        self.timer.start(interval)

    def stop(self):

        self.timer.stop()

    def pause(self):

        self._paused = True

    def resume(self):

        self._paused = False

    # -------------------------------------------------
    # Monitor
    # -------------------------------------------------

    def check_device(self):

        if self._paused:
            return

        self.current_device = self.service.scan()

        # Nothing changed
        if self.current_device.same_device(self.previous_device):
            return

        old = self.previous_device
        new = self.current_device

        # ---------------------------------------------
        # Connected
        # ---------------------------------------------

        if (not old.connected) and new.connected:

            self.device_connected.emit(new)

        # ---------------------------------------------
        # Disconnected
        # ---------------------------------------------

        elif old.connected and (not new.connected):

            self.device_disconnected.emit()

        # ---------------------------------------------
        # Hardware Mode Changed
        # ---------------------------------------------

        if old.state != new.state:

            self.state_changed.emit(old, new)

            if new.state == DeviceState.MAPLE_SERIAL:

                self.maple_detected.emit(new)

            elif new.state == DeviceState.USB_SERIAL:

                self.bootloader_detected.emit(new)

        # ---------------------------------------------
        # Notify listeners
        # ---------------------------------------------

        self.device_changed.emit(new)

        self.previous_device = new