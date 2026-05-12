"""MD 移动侦测配置标签页."""
from PySide6.QtWidgets import QWidget, QFormLayout, QComboBox

from core.dropdown_store import DropdownStore
from model.media_cfg_model import MdModel


class MdTab(QWidget):
    """md 移动侦测标签页。"""

    def __init__(self, dropdown: DropdownStore, parent=None):
        super().__init__(parent)
        self._dropdown = dropdown
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)

        self._widgets = {}
        for key, label in [("low", "low:"), ("mid", "mid:"), ("high", "high:")]:
            combo = QComboBox()
            combo.setEditable(True)
            for v in self._dropdown.get_options("md", key):
                combo.addItem(str(v))
            self._widgets[key] = combo
            layout.addRow(label, combo)

        # 默认值
        self._widgets["low"].setCurrentText("45")
        self._widgets["mid"].setCurrentText("35")
        self._widgets["high"].setCurrentText("25")

    def load_model(self, model: MdModel):
        self._widgets["low"].setCurrentText(str(model.low))
        self._widgets["mid"].setCurrentText(str(model.mid))
        self._widgets["high"].setCurrentText(str(model.high))

    def save_model(self, model: MdModel):
        for key in ("low", "mid", "high"):
            try:
                setattr(model, key, int(self._widgets[key].currentText()))
            except ValueError:
                pass
