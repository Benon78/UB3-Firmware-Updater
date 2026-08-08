"""
UB3 Firmware Updater - Main Window

GUI integration layer.

The MainWindow owns Qt widgets and translates
UpdateController callbacks into Qt signals so worker-thread
callbacks never update widgets directly.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ub3_updater.controllers.update_controller import (
    UpdateController,
    UpdateControllerState,
)
from ub3_updater.models.device import Device
from ub3_updater.models.upload_result import UploadResult
from ub3_updater.services.firmware_service import (
    FirmwareService,
)
from ub3_updater.themes.light_theme import (
    BORDER,
    PRIMARY_DARK,
    TEXT,
    TEXT_SECONDARY,
)
from ub3_updater.ui.pages.home_page import HomePage
from ub3_updater.workers.device_monitor import (
    DeviceMonitor,
)


class ControllerSignalBridge(QObject):
    """
    Qt bridge between UpdateController callbacks and the
    GUI thread.
    """

    device_changed = Signal(object)
    state_changed = Signal(object)
    status_changed = Signal(str)
    output = Signal(str)
    result = Signal(object)
    error = Signal(str)


class MainWindow(QMainWindow):
    """
    Main application window.

    Dependency injection is supported so GUI tests can use
    a fake controller without hardware.
    """

    def __init__(
        self,
        controller: UpdateController | None = None,
        parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle(
            "UB3 Firmware Updater Tool"
        )

        self.resize(
            1200,
            760,
        )

        self.setMinimumSize(
            1050,
            680,
        )

        self.controller = (
            controller
            if controller is not None
            else self._create_controller()
        )

        self.bridge = (
            ControllerSignalBridge()
        )

        self._build_ui()
        self._connect_controller()

    # ==================================================
    # Dependency construction
    # ==================================================

    @staticmethod
    def _create_controller() -> UpdateController:
        monitor = DeviceMonitor()

        firmware_service = (
            FirmwareService()
        )

        return UpdateController(
            device_monitor=monitor,
            firmware_service=firmware_service,
        )

    # ==================================================
    # UI
    # ==================================================

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(
            central
        )

        main_layout.setContentsMargins(
            0, 0, 0, 0
        )
        main_layout.setSpacing(0)

        # ----------------------------------------------
        # Header
        # ----------------------------------------------

        header = QWidget()
        header.setFixedHeight(58)
        header.setStyleSheet(
            f"""
            QWidget {{
                background: white;
                border-bottom: 1px solid {BORDER};
            }}
            """
        )

        header_layout = QHBoxLayout(
            header
        )
        header_layout.setContentsMargins(
            20, 8, 20, 8
        )

        title = QLabel(
            "UB3 Firmware Updater Tool"
        )
        title.setStyleSheet(
            f"""
            color: {PRIMARY_DARK};
            font-size: 18pt;
            font-weight: 700;
            border: none;
            """
        )

        header_layout.addWidget(title)
        header_layout.addStretch()

        self.header_status = QLabel(
            "Waiting for UB3"
        )
        self.header_status.setStyleSheet(
            f"""
            color: {TEXT_SECONDARY};
            font-weight: 600;
            border: none;
            """
        )

        header_layout.addWidget(
            self.header_status
        )

        main_layout.addWidget(
            header
        )

        # ----------------------------------------------
        # Home
        # ----------------------------------------------

        self.home_page = HomePage(
            controller=self.controller
        )

        main_layout.addWidget(
            self.home_page,
            1,
        )

        # ----------------------------------------------
        # Footer
        # ----------------------------------------------

        footer = QWidget()
        footer.setFixedHeight(32)
        footer.setStyleSheet(
            f"""
            QWidget {{
                background: white;
                border-top: 1px solid {BORDER};
            }}
            """
        )

        footer_layout = QHBoxLayout(
            footer
        )
        footer_layout.setContentsMargins(
            12, 4, 12, 4
        )

        self.version_label = QLabel(
            "v0.2.0"
        )
        self.version_label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; border: none;"
        )

        footer_layout.addWidget(
            self.version_label
        )
        footer_layout.addStretch()

        self.footer_status = QLabel(
            "Offline Mode"
        )
        self.footer_status.setStyleSheet(
            f"color: {TEXT_SECONDARY}; border: none;"
        )

        footer_layout.addWidget(
            self.footer_status
        )

        main_layout.addWidget(
            footer
        )

    # ==================================================
    # Controller connection
    # ==================================================

    def _connect_controller(self):
        self.controller.set_on_device_changed(
            self.bridge.device_changed.emit
        )

        self.controller.set_on_state_changed(
            self.bridge.state_changed.emit
        )

        self.controller.set_on_status(
            self.bridge.status_changed.emit
        )

        self.controller.set_on_output(
            self.bridge.output.emit
        )

        self.controller.set_on_result(
            self.bridge.result.emit
        )

        self.controller.set_on_error(
            self.bridge.error.emit
        )

        self.bridge.device_changed.connect(
            self._on_device_changed
        )

        self.bridge.state_changed.connect(
            self._on_state_changed
        )

        self.bridge.status_changed.connect(
            self._on_status
        )

        self.bridge.output.connect(
            self._on_output
        )

        self.bridge.result.connect(
            self._on_result
        )

        self.bridge.error.connect(
            self._on_error
        )

        self.controller.start()

        # Controller.start() does not immediately scan, so
        # perform an initial scan for the initial GUI state.
        self.controller.refresh_device()

    # ==================================================
    # Slots
    # ==================================================

    @Slot(object)
    def _on_device_changed(
        self,
        device,
    ):
        if isinstance(device, Device):
            self.home_page.update_device(
                device
            )
        else:
            self.home_page.update_device(
                None
            )

        self._update_header()

    @Slot(object)
    def _on_state_changed(
        self,
        state,
    ):
        if not isinstance(
            state,
            UpdateControllerState,
        ):
            return

        self.home_page.update_controller_state(
            state,
            self.controller.status_message,
        )

        self._update_header()

    @Slot(str)
    def _on_status(
        self,
        message: str,
    ):
        self.home_page.update_status(
            message
        )

        self.footer_status.setText(
            message
        )

        self._update_header()

    @Slot(str)
    def _on_output(
        self,
        output: str,
    ):
        self.home_page.append_output(
            output
        )

    @Slot(object)
    def _on_result(
        self,
        result,
    ):
        if isinstance(
            result,
            UploadResult,
        ):
            self.home_page.show_result(
                result
            )

        self._update_header()

    @Slot(str)
    def _on_error(
        self,
        message: str,
    ):
        self.home_page.update_status(
            message
        )

        self.footer_status.setText(
            message
        )

    # ==================================================
    # Header
    # ==================================================

    def _update_header(self):
        state = self.controller.state

        self.header_status.setText(
            state.value
        )

        if state in (
            UpdateControllerState.SUCCESS,
            UpdateControllerState.SUCCESS_WITH_WARNING,
        ):
            self.header_status.setStyleSheet(
                "color: #10B981; font-weight: 600; border: none;"
            )

        elif state in (
            UpdateControllerState.FAILED,
            UpdateControllerState.ERROR,
        ):
            self.header_status.setStyleSheet(
                "color: #EF4444; font-weight: 600; border: none;"
            )

        elif state == UpdateControllerState.UPLOADING:
            self.header_status.setStyleSheet(
                "color: #F59E0B; font-weight: 600; border: none;"
            )

        else:
            self.header_status.setStyleSheet(
                "color: #6B7280; font-weight: 600; border: none;"
            )

    # ==================================================
    # Shutdown
    # ==================================================

    def closeEvent(self, event):
        try:
            self.controller.stop()
        finally:
            event.accept()


def run_app() -> int:
    """
    Convenience entry point for manual launching.
    """

    app = QApplication.instance()

    owns_app = app is None

    if owns_app:
        app = QApplication(sys.argv)

    from ub3_updater.themes.light_theme import STYLE

    app.setStyleSheet(STYLE)

    window = MainWindow()
    window.show()

    if owns_app:
        return app.exec()

    return 0
