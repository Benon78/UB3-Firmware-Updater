"""
UB3 Firmware Updater - Update Confirmation Dialog

Step 4.2

A focused, operator-oriented confirmation dialog shown after the
pre-update safety validation has passed.

This dialog is presentation-only. It NEVER starts an upload.
The caller remains responsible for performing a second validation
immediately after confirmation and before starting UploadWorker.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from ub3_updater.models.pre_update_validation import (
    PreUpdateValidationResult,
)
from ub3_updater.themes.light_theme import (
    BORDER,
    CARD,
    ERROR,
    INFO_BACKGROUND,
    PRIMARY,
    PRIMARY_DARK,
    TEXT,
    TEXT_SECONDARY,
    WARNING,
    WARNING_BACKGROUND,
)


class UpdateConfirmationDialog(QDialog):
    """
    Confirm programming of the validated UB3 with the validated firmware.

    Parameters
    ----------
    validation_result:
        A successful ``PreUpdateValidationResult`` containing the device
        and firmware that were validated.

    Notes
    -----
    The dialog does not call the controller and does not start an upload.
    After ``Accepted``, the caller MUST run the final validation again
    before starting ``UploadWorker``.
    """

    def __init__(
        self,
        validation_result: PreUpdateValidationResult,
        parent=None,
    ):
        super().__init__(parent)

        self.validation_result = validation_result
        self.confirmation_checked = False

        self.setObjectName("updateConfirmationDialog")
        self.setWindowTitle("Confirm Firmware Update")
        self.setModal(True)
        self.setMinimumWidth(640)
        self.setMaximumWidth(760)

        self._build_ui()
        self._connect_signals()
        self._refresh_confirm_button()

    # ================================================================
    # UI construction
    # ================================================================

    def _build_ui(self):
        self.setStyleSheet(
            f"""
            QDialog#updateConfirmationDialog {{
                background: {CARD};
            }}

            QFrame#dialogHeader {{
                background: {INFO_BACKGROUND};
                border: 1px solid #BFDBFE;
                border-radius: 10px;
            }}

            QFrame#deviceCard,
            QFrame#firmwareCard {{
                background: {CARD};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}

            QLabel#dialogTitle {{
                color: {TEXT};
                font-size: 17pt;
                font-weight: 700;
                background: transparent;
                border: none;
            }}

            QLabel#dialogSubtitle {{
                color: {TEXT_SECONDARY};
                font-size: 10pt;
                background: transparent;
                border: none;
            }}

            QLabel#sectionTitle {{
                color: {TEXT};
                font-size: 11pt;
                font-weight: 700;
                background: transparent;
                border: none;
            }}

            QLabel#fieldLabel {{
                color: {TEXT_SECONDARY};
                font-size: 9pt;
                background: transparent;
                border: none;
            }}

            QLabel#fieldValue {{
                color: {TEXT};
                font-size: 10pt;
                font-weight: 600;
                background: transparent;
                border: none;
            }}

            QFrame#warningPanel {{
                background: {WARNING_BACKGROUND};
                border: 1px solid #FDE68A;
                border-radius: 8px;
            }}

            QLabel#warningTitle {{
                color: #92400E;
                font-size: 10pt;
                font-weight: 700;
                background: transparent;
                border: none;
            }}

            QLabel#warningText {{
                color: #78350F;
                font-size: 9pt;
                background: transparent;
                border: none;
            }}

            QCheckBox#confirmationCheck {{
                color: {TEXT};
                font-size: 9pt;
                font-weight: 600;
                spacing: 8px;
                background: transparent;
            }}

            QCheckBox#confirmationCheck::indicator {{
                width: 18px;
                height: 18px;
            }}

            QPushButton#dialogCancelButton,
            QPushButton#dialogUpdateButton {{
                background: {PRIMARY};
                color: white;
                border: 1px solid {PRIMARY_DARK};
                border-radius: 6px;
                min-height: 42px;
                padding: 0 20px;
                font-size: 10pt;
                font-weight: 700;
            }}

            QPushButton#dialogCancelButton:hover,
            QPushButton#dialogUpdateButton:hover {{
                background: #1D4ED8;
            }}

            QPushButton#dialogCancelButton:pressed,
            QPushButton#dialogUpdateButton:pressed {{
                background: {PRIMARY_DARK};
            }}

            QPushButton#dialogUpdateButton:disabled {{
                background: #D1D5DB;
                color: #6B7280;
                border-color: #D1D5DB;
            }}
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 20)
        root.setSpacing(14)

        # ------------------------------------------------------------
        # Header
        # ------------------------------------------------------------

        header = QFrame()
        header.setObjectName("dialogHeader")

        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 14, 16, 14)
        header_layout.setSpacing(4)

        title = QLabel("Ready to update this UB3?")
        title.setObjectName("dialogTitle")
        header_layout.addWidget(title)

        subtitle = QLabel(
            "The final safety checks passed. Review the device and "
            "firmware below before programming."
        )
        subtitle.setObjectName("dialogSubtitle")
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)

        root.addWidget(header)

        # ------------------------------------------------------------
        # Device + firmware cards
        # ------------------------------------------------------------

        cards = QHBoxLayout()
        cards.setSpacing(12)

        device_card = self._build_device_card()
        firmware_card = self._build_firmware_card()

        cards.addWidget(device_card, 1)
        cards.addWidget(firmware_card, 1)

        root.addLayout(cards)

        # ------------------------------------------------------------
        # Validation strip
        # ------------------------------------------------------------

        validation_frame = QFrame()
        validation_frame.setObjectName("validationPanel")
        validation_frame.setStyleSheet(
            f"""
            QFrame#validationPanel {{
                background: #ECFDF5;
                border: 1px solid #A7F3D0;
                border-radius: 8px;
            }}
            QLabel {{
                background: transparent;
                border: none;
                color: #065F46;
            }}
            """
        )

        validation_layout = QHBoxLayout(validation_frame)
        validation_layout.setContentsMargins(14, 10, 14, 10)
        validation_layout.setSpacing(8)

        check_icon = QLabel("✓")
        check_icon.setStyleSheet(
            "color: #059669; font-size: 15pt; font-weight: 800;"
        )
        validation_layout.addWidget(check_icon)

        validation_text = QLabel(
            "Pre-update checks passed: device identity, Maple Serial "
            "mode, and firmware file are valid."
        )
        validation_text.setObjectName("validationText")
        validation_text.setWordWrap(True)
        validation_layout.addWidget(
            validation_text,
            1,
        )

        root.addWidget(validation_frame)

        # ------------------------------------------------------------
        # Safety warning
        # ------------------------------------------------------------

        warning = QFrame()
        warning.setObjectName("warningPanel")

        warning_layout = QVBoxLayout(warning)
        warning_layout.setContentsMargins(14, 11, 14, 11)
        warning_layout.setSpacing(4)

        warning_title = QLabel(
            "⚠  Firmware programming will change the UB3"
        )
        warning_title.setObjectName("warningTitle")
        warning_layout.addWidget(warning_title)

        warning_text = QLabel(
            "Keep this UB3 connected during the update. Do not "
            "manually switch it into USB Serial / flash mode. "
            "The Maple Loader will perform the reset required for programming."
        )
        warning_text.setObjectName("warningText")
        warning_text.setWordWrap(True)
        warning_layout.addWidget(warning_text)

        root.addWidget(warning)

        # ------------------------------------------------------------
        # Explicit operator acknowledgement
        # ------------------------------------------------------------

        self.confirmation_check = QCheckBox(
            "I have reviewed the device and firmware information "
            "and want to continue."
        )
        self.confirmation_check.setObjectName(
            "confirmationCheck"
        )
        self.confirmation_check.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        root.addWidget(self.confirmation_check)

        # ------------------------------------------------------------
        # Buttons
        # ------------------------------------------------------------

        self.button_box = QDialogButtonBox()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName(
            "dialogCancelButton"
        )
        self.cancel_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.update_button = QPushButton(
            "Update UB3"
        )
        self.update_button.setObjectName(
            "dialogUpdateButton"
        )
        self.update_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.update_button.setDefault(True)

        self.button_box.addButton(
            self.cancel_button,
            QDialogButtonBox.ButtonRole.RejectRole,
        )
        self.button_box.addButton(
            self.update_button,
            QDialogButtonBox.ButtonRole.AcceptRole,
        )

        root.addWidget(self.button_box)

        # ------------------------------------------------------------
        # Guard invalid input
        # ------------------------------------------------------------

        if not self.validation_result.valid:
            self.confirmation_check.setEnabled(False)
            self.update_button.setEnabled(False)
            self.warning_text = QLabel(
                "The supplied validation result is not valid. "
                "Return to the main screen and run validation again."
            )
            self.warning_text.setStyleSheet(
                f"color: {ERROR}; background: transparent; border: none;"
            )
            self.warning_text.setWordWrap(True)
            root.insertWidget(
                root.count() - 1,
                self.warning_text,
            )

        self.adjustSize()

    # ================================================================
    # Cards
    # ================================================================

    def _build_device_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("deviceCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 13, 14, 13)
        layout.setSpacing(8)

        title = QLabel("UB3 TO PROGRAM")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        device = self.validation_result.device

        if device is None:
            values = {
                "Device": "Unavailable",
                "COM Port": "Unavailable",
                "USB Mode": "Unavailable",
                "VID:PID": "Unavailable",
                "Manufacturer": "Unavailable",
            }
        else:
            values = {
                "Device": device.display_name or "Unavailable",
                "COM Port": device.com_port or "Unavailable",
                "USB Mode": device.state.value,
                "VID:PID": self._format_vid_pid(device),
                "Manufacturer": device.manufacturer or "Unavailable",
            }

        for label, value in values.items():
            row = self._field_row(label, value)
            layout.addLayout(row)

        return card

    def _build_firmware_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("firmwareCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 13, 14, 13)
        layout.setSpacing(8)

        title = QLabel("FIRMWARE TO INSTALL")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        firmware = self.validation_result.firmware

        if firmware is None:
            values = {
                "Firmware": "Unavailable",
                "Version": "Unavailable",
                "Target": "Unavailable",
                "File": "Unavailable",
                "Size": "Unavailable",
            }
        else:
            size = (
                f"{firmware.size_mb:.2f} MB"
                if firmware.size > 0
                else "Unavailable"
            )

            values = {
                "Firmware": firmware.name or "Unavailable",
                "Version": firmware.version or "Unavailable",
                "Target": (
                    firmware.target_device
                    or firmware.hardware
                    or "Unavailable"
                ),
                "File": firmware.filename or "Unavailable",
                "Size": size,
            }

        for label, value in values.items():
            row = self._field_row(label, value)
            layout.addLayout(row)

        return card

    @staticmethod
    def _field_row(
        label: str,
        value: str,
    ) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)

        label_widget = QLabel(label)
        label_widget.setObjectName("fieldLabel")
        label_widget.setMinimumWidth(78)

        value_widget = QLabel(value)
        value_widget.setObjectName("fieldValue")
        value_widget.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        value_widget.setWordWrap(True)

        row.addWidget(label_widget)
        row.addWidget(value_widget, 1)

        return row

    @staticmethod
    def _format_vid_pid(device) -> str:
        vid = device.vid or "--"
        pid = device.pid or "--"
        return f"{vid}:{pid}"

    # ================================================================
    # Signals
    # ================================================================

    def _connect_signals(self):
        self.confirmation_check.toggled.connect(
            self._on_confirmation_changed
        )

        self.cancel_button.clicked.connect(
            self.reject
        )

        self.update_button.clicked.connect(
            self.accept
        )

    def _on_confirmation_changed(
        self,
        checked: bool,
    ):
        self.confirmation_checked = bool(checked)
        self._refresh_confirm_button()

    def _refresh_confirm_button(self):
        self.update_button.setEnabled(
            bool(
                self.validation_result.valid
                and self.confirmation_checked
            )
        )

    # ================================================================
    # Public API
    # ================================================================

    @property
    def confirmed(self) -> bool:
        """Return True only after the operator accepted the dialog."""
        return self.result() == QDialog.DialogCode.Accepted

    @property
    def device(self):
        """The device displayed for confirmation."""
        return self.validation_result.device

    @property
    def firmware(self):
        """The firmware displayed for confirmation."""
        return self.validation_result.firmware
