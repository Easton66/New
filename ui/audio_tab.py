"""Audio 音频配置标签页."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QCheckBox, QSpinBox, QComboBox, QGroupBox,
)

from core.dropdown_store import DropdownStore
from model.media_cfg_model import AudioModel


class _AudioSection(QGroupBox):
    """通用音频子模块表单。"""

    def __init__(self, title: str, fields: list, dropdown: DropdownStore, parent=None):
        """
        fields: list of (attr_key, label, widget_type)
        widget_type: "int" | "bool" | "combo"
        """
        super().__init__(title, parent)
        self._fields = fields
        self._widgets = {}
        self._dropdown = dropdown
        self._setup()

    def _setup(self):
        layout = QFormLayout(self)
        for key, label, wtype in self._fields:
            if wtype == "bool":
                w = QCheckBox()
            elif wtype == "combo":
                w = QComboBox()
                w.setEditable(True)
            else:
                w = QSpinBox()
                w.setRange(-9999, 999999)
            self._widgets[key] = w
            layout.addRow(f"{label}:", w)

    def load_submodel(self, submodel):
        for key, w in self._widgets.items():
            val = getattr(submodel, key, None)
            if val is None:
                continue
            if isinstance(w, QCheckBox):
                w.setChecked(bool(val))
            elif isinstance(w, QComboBox):
                w.setCurrentText(str(val))
            elif isinstance(w, QSpinBox):
                w.setValue(int(val))

    def save_submodel(self, submodel):
        for key, w in self._widgets.items():
            if isinstance(w, QCheckBox):
                setattr(submodel, key, w.isChecked())
            elif isinstance(w, QComboBox):
                try:
                    setattr(submodel, key, int(w.currentText()))
                except ValueError:
                    setattr(submodel, key, w.currentText())
            elif isinstance(w, QSpinBox):
                setattr(submodel, key, w.value())


class AudioTab(QWidget):
    """audio 配置标签页。"""

    def __init__(self, dropdown: DropdownStore, parent=None):
        super().__init__(parent)
        self._dropdown = dropdown
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # AI 组
        ai_fields = [
            ("gain", "gain", "int"), ("vol", "vol", "int"),
            ("SampleRate", "SampleRate", "int"), ("NumPerFrm", "NumPerFrm", "int"),
            ("NrLevel", "NrLevel", "int"), ("NrEnable", "NrEnable", "bool"),
            ("AgcTarget", "AgcTarget", "int"), ("AgcMaxGain", "AgcMaxGain", "int"),
            ("AgcEnable", "AgcEnable", "bool"), ("HsEnable", "HsEnable", "bool"),
        ]
        self._ai_section = _AudioSection("音频输入 (ai)", ai_fields, self._dropdown)
        layout.addWidget(self._ai_section)

        # AEC 组
        aec_fields = [
            ("enable", "enable", "bool"), ("SafeSuppression", "SafeSuppression", "int"),
            ("TargetLevel", "TargetLevel", "int"), ("CompressionGain", "CompressionGain", "int"),
            ("FarFrm", "FarFrm", "int"), ("NearFrm", "NearFrm", "int"),
            ("DelayMs", "DelayMs", "int"),
        ]
        self._aec_section = _AudioSection("回声消除 (aec)", aec_fields, self._dropdown)
        layout.addWidget(self._aec_section)

        # AO 组
        ao_fields = [
            ("gain", "gain", "int"), ("vol", "vol", "int"),
            ("SampleRate", "SampleRate", "int"), ("NumPerFrm", "NumPerFrm", "int"),
            ("AgcTarget", "AgcTarget", "int"), ("AgcMaxGain", "AgcMaxGain", "int"),
            ("AgcEnable", "AgcEnable", "bool"),
        ]
        self._ao_section = _AudioSection("音频输出 (ao)", ao_fields, self._dropdown)
        layout.addWidget(self._ao_section)

    def load_model(self, model: AudioModel):
        self._ai_section.load_submodel(model.ai)
        self._aec_section.load_submodel(model.aec)
        self._ao_section.load_submodel(model.ao)

    def save_model(self, model: AudioModel):
        self._ai_section.save_submodel(model.ai)
        self._aec_section.save_submodel(model.aec)
        self._ao_section.save_submodel(model.ao)
