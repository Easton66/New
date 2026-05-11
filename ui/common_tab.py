# -*- coding: utf-8 -*-
"""Common 配置标签页."""
from PySide6.QtWidgets import QWidget, QFormLayout, QComboBox

from core.dropdown_store import DropdownStore
from model.media_cfg_model import CommonModel


class CommonTab(QWidget):
    """common 基本配置标签页。"""

    def __init__(self, dropdown: DropdownStore, parent=None):
        super().__init__(parent)
        self._dropdown = dropdown
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)

        self.ver_combo = QComboBox()
        self.ver_combo.setEditable(True)
        for v in self._dropdown.get_options("common", "ver"):
            self.ver_combo.addItem(str(v))
        self.ver_combo.setCurrentText("0")
        layout.addRow("ver:", self.ver_combo)

        self.plat_combo = QComboBox()
        self.plat_combo.setEditable(True)
        for v in self._dropdown.get_options("common", "plat"):
            self.plat_combo.addItem(str(v))
        self.plat_combo.setCurrentText("17")
        layout.addRow("plat:", self.plat_combo)

    def load_model(self, model: CommonModel):
        self.ver_combo.setCurrentText(str(model.ver))
        self.plat_combo.setCurrentText(str(model.plat))

    def save_model(self, model: CommonModel):
        try:
            model.ver = int(self.ver_combo.currentText())
        except ValueError:
            model.ver = 0
        try:
            model.plat = int(self.plat_combo.currentText())
        except ValueError:
            model.plat = 0
