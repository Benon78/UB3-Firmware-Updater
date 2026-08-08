import sys
import bootstrap

from PySide6.QtCore import (
    QCoreApplication,
    QTimer
)

from ub3_updater.workers.device_monitor import DeviceMonitor

app = QCoreApplication(sys.argv)

monitor = DeviceMonitor()

monitor.device_changed.connect(
    lambda d: print("Changed:", d)
)

monitor.device_connected.connect(
    lambda d: print("Connected:", d)
)

monitor.device_disconnected.connect(
    lambda: print("Disconnected")
)

monitor.runtime_detected.connect(
    lambda d: print("Runtime:", d)
)

monitor.dfu_detected.connect(
    lambda d: print("DFU:", d)
)

monitor.start()

# Stop automatically after 20 seconds
QTimer.singleShot(20000, app.quit)

sys.exit(app.exec())