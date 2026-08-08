"""
=========================================================
UB3 Firmware Updater

Home Page

Developer:
Benjamin William
=========================================================
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
)

from PySide6.QtCore import Qt

from ub3_updater.widgets.logo_widget import LogoWidget
from ub3_updater.widgets.connection_status import ConnectionStatusWidget
from ub3_updater.widgets.instruction_widget import InstructionWidget
from ub3_updater.widgets.footer_widget import FooterWidget
from ub3_updater.ui.base_page import BasePage

class HomePage(BasePage):

    def __init__(self):

        super().__init__(
            title="Home",
            subtitle="Connect your UB3 device to begin firmware management."
        )

        self.build_home()

    def build_home(self):

        self.add_widget(LogoWidget())

        self.add_widget(ConnectionStatusWidget())

        self.add_widget(InstructionWidget())

        self.add_widget(FooterWidget())