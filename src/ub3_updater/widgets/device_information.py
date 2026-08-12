"""
UB3 Firmware Updater - Device Information Widget

GUI Step 2:
Displays hardware/device information after a UB3 is detected.

The widget only displays information actually available from
the current Device model. Values not supplied by USB detection
are explicitly shown as "Not reported" rather than invented.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QVBoxLayout,
)

from ub3_updater.models.device import Device
from ub3_updater.widgets.components import UB3Card, UB3InfoRow, UB3SectionHeader
from ub3_updater.themes.design_system import (
    BORDER,
    INFO_BACKGROUND,
    PRIMARY_DARK,
    TEXT,
    TEXT_SECONDARY,
    SURFACE,
    SPACE_3,
    SPACE_4,
)


class DeviceInformationWidget(UB3Card):
    """Display structured UB3 device information."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("deviceInformationCard")
        self._value_labels: dict[str, QLabel] = {}

        self._build_ui()
        self.set_disconnected()

    def _build_ui(self):
        """Build the operator-facing device information card.

        The widget remains presentation-only. The existing value-label
        dictionary is intentionally preserved for backwards-compatible
        GUI tests and callers.
        """
        self.setObjectName("deviceInformationCard")
        self.setStyleSheet(
            f"""
            QFrame#deviceInformationCard {{
                background: {SURFACE};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
            """
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 16, 18, 16)
        outer.setSpacing(SPACE_3)

        header = UB3SectionHeader(
            "Device Information",
            "Information detected from the connected UB3.",
        )
        outer.addWidget(header)

        subtitle = QLabel(
            "Only information reported by the current USB device is displayed."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(
            f"color: {TEXT_SECONDARY}; border: none;"
        )
        outer.addWidget(subtitle)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(7)
        grid.setColumnMinimumWidth(0, 135)
        grid.setColumnStretch(1, 1)

        fields = (
            ("device_name", "Device Name"),
            ("board_id", "Board ID"),
            ("bootloader_version", "Bootloader Version"),
            ("firmware_version", "Firmware Version"),
            ("hardware_version", "Hardware Version"),
            ("device_type", "Device Type"),
            ("com_port", "COM Port"),
            ("usb_mode", "USB Mode"),
            ("vid_pid", "VID:PID"),
            ("manufacturer", "Manufacturer"),
            ("hardware_id", "Hardware ID"),
        )

        for row, (key, caption) in enumerate(fields):
            info_row = UB3InfoRow(caption, "Not reported")
            self._value_labels[key] = info_row._value
            grid.addWidget(info_row, row, 0, 1, 2)

        outer.addLayout(grid)

        note = QLabel(
            "Firmware and bootloader versions are shown when reported by the device. "
            "USB detection alone does not read application firmware metadata."
        )
        note.setWordWrap(True)
        note.setStyleSheet(
            f"""
            color: {TEXT_SECONDARY};
            font-size: 9pt;
            border: none;
            padding-top: 3px;
            """
        )
        outer.addWidget(note)

    def set_disconnected(self):
        for label in self._value_labels.values():
            label.setText("Not reported")

    def update_device(self, device: Device | None):
        if device is None or not device.connected:
            self.set_disconnected()
            return

        self._set("device_name", "UB3")

        # The current Device model does not expose a separate
        # board-ID field. Do not silently equate HWID to Board ID.
        self._set("board_id", "Not reported")
        self._set("bootloader_version", "Not reported")
        self._set("firmware_version", "Not reported")
        self._set("hardware_version", "Not reported")

        # The current USB detection layer does not identify the
        # MCU part number independently.
        self._set("device_type", "Not reported")

        self._set(
            "com_port",
            device.com_port or "Not reported",
        )

        self._set(
            "usb_mode",
            device.state.value
            if device.state is not None
            else "Not reported",
        )

        vid = device.vid or "--"
        pid = device.pid or "--"

        self._set(
            "vid_pid",
            f"{vid}:{pid}",
        )

        self._set(
            "manufacturer",
            device.manufacturer or "Not reported",
        )

        self._set(
            "hardware_id",
            device.hwid or "Not reported",
        )

    def _set(self, key: str, value: str):
        label = self._value_labels.get(key)
        if label is not None:
            label.setText(value)
