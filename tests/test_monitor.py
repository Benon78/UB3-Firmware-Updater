import sys
import bootstrap

from PySide6.QtCore import QCoreApplication

from ub3_updater.workers.device_monitor import DeviceMonitor

app = QCoreApplication(sys.argv)

monitor = DeviceMonitor()


monitor.device_connected.connect(
    lambda d: print(f"[CONNECTED] {d}")
)

monitor.device_disconnected.connect(
    lambda: print("[DISCONNECTED]")
)

monitor.maple_detected.connect(
    lambda d: print(f"[MAPLE] {d}")
)

monitor.bootloader_detected.connect(
    lambda d: print(f"[BOOTLOADER] {d}")
)

monitor.state_changed.connect(
    lambda old, new: print(f"[STATE] {old.state.value} -> {new.state.value}")
)

monitor.device_changed.connect(
    lambda d: print(f"[DEVICE] {d}")
)

monitor.start()

sys.exit(app.exec())