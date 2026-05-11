"""主窗口 - Tab 管理和菜单栏."""
import os
import subprocess
import sys
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QMenuBar, QStatusBar, QFileDialog, QMessageBox,
)
from PySide6.QtCore import Qt

from core.dropdown_store import DropdownStore
from core.file_manager import save_to_file, load_from_file
from core.json_exporter import export_to_file, export_to_clipboard
from model.media_cfg_model import MediaCfgModel

from ui.common_tab import CommonTab
from ui.ircut_tab import IrcutTab
from ui.audio_tab import AudioTab
from ui.md_tab import MdTab
from ui.pipeline_tab import PipelineTab
from ui.mapping_tab import MappingTab


class MainWindow(QMainWindow):
    """MediaCfg 编辑器主窗口。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MediaCfg Editor")
        self.resize(1100, 750)

        self._model = MediaCfgModel()
        self._current_file = None
        self._dropdown = DropdownStore()

        self._setup_menu()
        self._setup_tabs()
        self._setup_statusbar()

    def _setup_menu(self):
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")
        file_menu.addAction("新建", self._file_new, "Ctrl+N")
        file_menu.addAction("打开草稿...", self._file_open, "Ctrl+O")
        file_menu.addAction("保存", self._file_save, "Ctrl+S")
        file_menu.addAction("另存为...", self._file_save_as, "Ctrl+Shift+S")
        file_menu.addSeparator()
        file_menu.addAction("退出", self.close, "Ctrl+Q")

        # 导出菜单
        export_menu = menubar.addMenu("导出")
        export_menu.addAction("导出 JSON 到剪贴板", self._export_clipboard, "Ctrl+Shift+C")
        export_menu.addAction("导出 JSON 到文件...", self._export_file, "Ctrl+E")

        # 选项菜单
        option_menu = menubar.addMenu("选项")
        option_menu.addAction("下拉配置...", self._open_dropdown_config)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        help_menu.addAction("关于", self._show_about)

    def _setup_tabs(self):
        self._tabs = QTabWidget()
        self.setCentralWidget(self._tabs)

        self._common_tab = CommonTab(self._dropdown)
        self._ircut_tab = IrcutTab(self._dropdown)
        self._audio_tab = AudioTab(self._dropdown)
        self._md_tab = MdTab(self._dropdown)
        self._pipeline_tab = PipelineTab(self._dropdown)
        self._mapping_tab = MappingTab(self._dropdown)
        self._mapping_tab.set_pipeline(self._model.pipeline)

        self._tabs.addTab(self._common_tab, "common")
        self._tabs.addTab(self._ircut_tab, "ircut")
        self._tabs.addTab(self._audio_tab, "audio")
        self._tabs.addTab(self._md_tab, "md")
        self._tabs.addTab(self._pipeline_tab, "pipeline")
        self._tabs.addTab(self._mapping_tab, "mapping")

        self._load_model_to_tabs()

    def _setup_statusbar(self):
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)
        self._update_status("就绪 - 未保存")

    def _update_status(self, msg):
        self._statusbar.showMessage(msg)

    def _load_model_to_tabs(self):
        self._common_tab.load_model(self._model.common)
        self._ircut_tab.load_model(self._model.ircut)
        self._audio_tab.load_model(self._model.audio)
        self._md_tab.load_model(self._model.md)
        self._pipeline_tab.load_model(self._model.pipeline)
        self._mapping_tab.load_model(self._model.mapping)

    def _save_model_from_tabs(self):
        self._common_tab.save_model(self._model.common)
        self._ircut_tab.save_model(self._model.ircut)
        self._audio_tab.save_model(self._model.audio)
        self._md_tab.save_model(self._model.md)
        self._pipeline_tab.save_model(self._model.pipeline)
        self._mapping_tab.save_model(self._model.mapping)

    # ---- 文件操作 ----
    def _file_new(self):
        self._save_model_from_tabs()
        self._model = MediaCfgModel()
        self._current_file = None
        self._mapping_tab.set_pipeline(self._model.pipeline)
        self._load_model_to_tabs()
        self._update_status("新建 - 未保存")

    def _file_open(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "打开草稿", "", "JSON 文件 (*.json);;所有文件 (*)",
        )
        if not filepath:
            return
        try:
            self._model = load_from_file(filepath)
            self._current_file = filepath
            self._mapping_tab.set_pipeline(self._model.pipeline)
            self._load_model_to_tabs()
            self._update_status(f"已打开: {filepath}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文件: {e}")

    def _file_save(self):
        self._save_model_from_tabs()
        if self._current_file:
            try:
                save_to_file(self._model, self._current_file)
                self._update_status(f"已保存: {self._current_file}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {e}")
        else:
            self._file_save_as()

    def _file_save_as(self):
        self._save_model_from_tabs()
        filepath, _ = QFileDialog.getSaveFileName(
            self, "另存为", "", "JSON 文件 (*.json);;所有文件 (*)",
        )
        if not filepath:
            return
        try:
            save_to_file(self._model, filepath)
            self._current_file = filepath
            self._update_status(f"已保存: {filepath}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {e}")

    # ---- 导出 ----
    def _export_clipboard(self):
        self._save_model_from_tabs()
        try:
            export_to_clipboard(self._model)
            self._update_status("MediaCfg JSON 已复制到剪贴板")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {e}")

    def _export_file(self):
        self._save_model_from_tabs()
        filepath, _ = QFileDialog.getSaveFileName(
            self, "导出 MediaCfg JSON", "", "JSON 文件 (*.json);;所有文件 (*)",
        )
        if not filepath:
            return
        try:
            export_to_file(self._model, filepath)
            self._update_status(f"已导出: {filepath}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {e}")

    # ---- 选项 ----
    def _open_dropdown_config(self):
        filepath = self._dropdown.filepath
        if sys.platform == "win32":
            os.startfile(filepath)
        else:
            subprocess.run(["xdg-open", filepath])

    # ---- 帮助 ----
    def _show_about(self):
        QMessageBox.about(self, "关于 MediaCfg Editor",
                          "MediaCfg Editor v1.0\n\n"
                          "IP 摄像头 MediaCfg JSON 配置编辑器\n"
                          "面向开发/测试人员的可视化配置工具")
