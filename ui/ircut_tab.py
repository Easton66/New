"""Ircut 红外滤光片配置标签页."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QCheckBox, QSpinBox, QComboBox, QGroupBox,
)

from core.dropdown_store import DropdownStore
from model.media_cfg_model import IrcutModel


class IrcutTab(QWidget):
    """ircut 配置标签页。"""

    def __init__(self, dropdown: DropdownStore, parent=None):
        super().__init__(parent)
        self._dropdown = dropdown
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # 红外支持
        self.support_ir = QCheckBox("支持红外 (SupportIR)")
        self.support_ir.setChecked(True)
        layout.addWidget(self.support_ir)

        # soft_sensor
        soft_layout = QFormLayout()
        self.soft_sensor = QSpinBox()
        self.soft_sensor.setRange(0, 1)
        self.soft_sensor.setSpecialValueText("无")
        soft_layout.addRow("soft_sensor:", self.soft_sensor)
        layout.addLayout(soft_layout)
        layout.addSpacing(8)

        # d2n 组
        self._d2n_group = QGroupBox("日→夜切换 (d2n)")
        d2n_layout = QFormLayout(self._d2n_group)
        self._d2n_widgets = {}

        d2n_fields = [("d2n_luma_th", "亮度阈值"), ("d2n_iso_th", "ISO 阈值"),
                      ("low", "low"), ("th", "th"), ("high", "high")]
        for key, label in d2n_fields:
            combo = QComboBox()
            combo.setEditable(True)
            for v in self._dropdown.get_options("ircut", f"d2n.{key}"):
                combo.addItem(str(v))
            self._d2n_widgets[key] = combo
            d2n_layout.addRow(f"{label}:", combo)

        self._set_defaults(self._d2n_widgets, {
            "d2n_luma_th": "0", "d2n_iso_th": "2000", "low": "0", "th": "120981", "high": "100",
        })
        layout.addWidget(self._d2n_group)

        # n2d 组
        self._n2d_group = QGroupBox("夜→日切换 (n2d)")
        n2d_layout = QFormLayout(self._n2d_group)
        self._n2d_widgets = {}

        n2d_fields = [("n2d_luma_th", "亮度阈值"), ("n2d_iso_th", "ISO 阈值"),
                      ("low", "low"), ("ir", "ir"), ("high", "high"),
                      ("bGain", "bGain"), ("vl", "vl")]
        for key, label in n2d_fields:
            combo = QComboBox()
            combo.setEditable(True)
            for v in self._dropdown.get_options("ircut", f"n2d.{key}"):
                combo.addItem(str(v))
            self._n2d_widgets[key] = combo
            n2d_layout.addRow(f"{label}:", combo)

        self._set_defaults(self._n2d_widgets, {
            "n2d_luma_th": "15", "n2d_iso_th": "20000", "low": "0",
            "ir": "6741", "high": "1500", "bGain": "240", "vl": "0",
        })
        layout.addWidget(self._n2d_group)

    def _set_defaults(self, widgets: dict, defaults: dict):
        for key, val in defaults.items():
            if key in widgets:
                combo = widgets[key]
                if combo.findText(val) < 0:
                    combo.addItem(val)
                combo.setCurrentText(val)

    def load_model(self, model: IrcutModel):
        self.support_ir.setChecked(model.SupportIR)
        if model.soft_sensor is not None:
            self.soft_sensor.setValue(model.soft_sensor)
        else:
            self.soft_sensor.setValue(0)
        self._load_to_widgets(self._d2n_widgets, model.d2n)
        self._load_to_widgets(self._n2d_widgets, model.n2d)

    def _load_to_widgets(self, widgets: dict, submodel):
        for key, combo in widgets.items():
            val = getattr(submodel, key, None)
            if val is not None:
                combo.setCurrentText(str(val))

    def save_model(self, model: IrcutModel):
        model.SupportIR = self.support_ir.isChecked()
        model.soft_sensor = self.soft_sensor.value() if self.soft_sensor.value() > 0 else None
        self._save_from_widgets(self._d2n_widgets, model.d2n)
        self._save_from_widgets(self._n2d_widgets, model.n2d)

    def _save_from_widgets(self, widgets: dict, submodel):
        for key, combo in widgets.items():
            try:
                setattr(submodel, key, int(combo.currentText()))
            except ValueError:
                pass
