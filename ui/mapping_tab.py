"""Mapping 设备通道映射标签页."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QGroupBox, QFormLayout, QSpinBox, QMessageBox,
)

from core.dropdown_store import DropdownStore
from core.mapping_generator import generate_mapping
from model.media_cfg_model import MappingModel, PipelineModel, ChannelMapping, DeviceMapping


class MappingTab(QWidget):
    """mapping 配置标签页。"""

    def __init__(self, dropdown: DropdownStore, parent=None):
        super().__init__(parent)
        self._dropdown = dropdown
        self._model = None
        self._pipeline = None
        self._channels = []
        self._channel_metas = []  # (dev_id, chn_id)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        # 顶部：通道卡片列表
        top_layout = QHBoxLayout()
        self._channel_list = QListWidget()
        self._channel_list.setMaximumHeight(100)
        self._channel_list.setFlow(QListWidget.LeftToRight)
        self._channel_list.currentRowChanged.connect(self._on_channel_selected)
        top_layout.addWidget(self._channel_list, 1)

        btn_layout = QVBoxLayout()
        self._add_channel_btn = QPushButton("+ 添加")
        self._add_channel_btn.clicked.connect(self._add_channel)
        self._remove_channel_btn = QPushButton("删除")
        self._remove_channel_btn.clicked.connect(self._remove_channel)
        self._auto_gen_btn = QPushButton("从 Pipeline 自动生成")
        self._auto_gen_btn.clicked.connect(self._auto_generate)
        btn_layout.addWidget(self._add_channel_btn)
        btn_layout.addWidget(self._remove_channel_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self._auto_gen_btn)
        top_layout.addLayout(btn_layout)
        main_layout.addLayout(top_layout)

        # 底部：通道详情
        self._detail_group = QGroupBox("Channel 详情")
        detail_layout = QFormLayout(self._detail_group)

        self._vi_dev = QSpinBox(); self._vi_dev.setRange(0, 99)
        self._vi_chn = QSpinBox(); self._vi_chn.setRange(0, 99)
        vi_row = QHBoxLayout(); vi_row.addWidget(self._vi_dev); vi_row.addWidget(self._vi_chn)
        detail_layout.addRow("VI (dev_id/chn_id):", vi_row)

        self._osd_dev = QSpinBox(); self._osd_dev.setRange(0, 99)
        self._osd_chn = QSpinBox(); self._osd_chn.setRange(0, 99)
        osd_row = QHBoxLayout(); osd_row.addWidget(self._osd_dev); osd_row.addWidget(self._osd_chn)
        detail_layout.addRow("OSD (dev_id/chn_id):", osd_row)

        self._venc_dev = QSpinBox(); self._venc_dev.setRange(0, 99)
        self._venc_chn = QSpinBox(); self._venc_chn.setRange(0, 99)
        venc_row = QHBoxLayout(); venc_row.addWidget(self._venc_dev); venc_row.addWidget(self._venc_chn)
        detail_layout.addRow("VENC (dev_id/chn_id):", venc_row)

        main_layout.addWidget(self._detail_group)

    def set_pipeline(self, pipeline: PipelineModel):
        self._pipeline = pipeline

    def load_model(self, model: MappingModel):
        self._model = model
        self._channels.clear()
        self._channel_metas.clear()
        for dev in model.devices:
            for ch in dev.channels:
                cm = ChannelMapping(
                    chn_id=ch.chn_id,
                    vi_dev_id=ch.vi_dev_id, vi_chn_id=ch.vi_chn_id,
                    osd_dev_id=ch.osd_dev_id, osd_chn_id=ch.osd_chn_id,
                    venc_dev_id=ch.venc_dev_id, venc_chn_id=ch.venc_chn_id,
                )
                self._channels.append(cm)
                self._channel_metas.append((ch.venc_dev_id, ch.chn_id))
        self._refresh_channel_list()
        if self._channel_list.count() > 0:
            self._channel_list.setCurrentRow(0)

    def save_model(self, model: MappingModel):
        self._save_current_channel()
        dev_map = {}
        for ch in self._channels:
            dev_id = ch.venc_dev_id
            if dev_id not in dev_map:
                dev_map[dev_id] = []
            dev_map[dev_id].append(ch)
        model.devices.clear()
        for dev_id in sorted(dev_map.keys()):
            dm = DeviceMapping(dev_id=dev_id, channels=dev_map[dev_id])
            model.devices.append(dm)

    def _refresh_channel_list(self):
        self._channel_list.clear()
        for dev_id, chn_id in self._channel_metas:
            self._channel_list.addItem(f"dev{dev_id}/chn{chn_id}")

    def _on_channel_selected(self, index):
        self._save_current_channel()
        if 0 <= index < len(self._channels):
            ch = self._channels[index]
            self._vi_dev.setValue(ch.vi_dev_id)
            self._vi_chn.setValue(ch.vi_chn_id)
            self._osd_dev.setValue(ch.osd_dev_id)
            self._osd_chn.setValue(ch.osd_chn_id)
            self._venc_dev.setValue(ch.venc_dev_id)
            self._venc_chn.setValue(ch.venc_chn_id)
            self._detail_group.setTitle(f"Channel 详情: dev{self._channel_metas[index][0]}/chn{self._channel_metas[index][1]}")
        self._detail_group.setEnabled(index >= 0)

    def _save_current_channel(self):
        idx = self._channel_list.currentRow()
        if idx < 0 or idx >= len(self._channels):
            return
        ch = self._channels[idx]
        ch.vi_dev_id = self._vi_dev.value()
        ch.vi_chn_id = self._vi_chn.value()
        ch.osd_dev_id = self._osd_dev.value()
        ch.osd_chn_id = self._osd_chn.value()
        ch.venc_dev_id = self._venc_dev.value()
        ch.venc_chn_id = self._venc_chn.value()
        self._channel_metas[idx] = (ch.venc_dev_id, ch.chn_id)

    def _add_channel(self):
        ch = ChannelMapping()
        self._channels.append(ch)
        self._channel_metas.append((0, 0))
        self._refresh_channel_list()
        self._channel_list.setCurrentRow(self._channel_list.count() - 1)

    def _remove_channel(self):
        idx = self._channel_list.currentRow()
        if idx < 0:
            return
        self._channels.pop(idx)
        self._channel_metas.pop(idx)
        self._refresh_channel_list()

    def _auto_generate(self):
        if self._pipeline is None:
            QMessageBox.warning(self, "提示", "请先配置 Pipeline")
            return
        reply = QMessageBox.question(
            self, "确认", "从 Pipeline 自动生成将覆盖当前 Mapping 配置，确认继续？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        new_mapping = generate_mapping(self._pipeline)
        self._channels.clear()
        self._channel_metas.clear()
        for dev in new_mapping.devices:
            for ch in dev.channels:
                self._channels.append(ChannelMapping(
                    chn_id=ch.chn_id,
                    vi_dev_id=ch.vi_dev_id, vi_chn_id=ch.vi_chn_id,
                    osd_dev_id=ch.osd_dev_id, osd_chn_id=ch.osd_chn_id,
                    venc_dev_id=ch.venc_dev_id, venc_chn_id=ch.venc_chn_id,
                ))
                self._channel_metas.append((ch.venc_dev_id, ch.chn_id))
        self._refresh_channel_list()
        if self._channel_list.count() > 0:
            self._channel_list.setCurrentRow(0)
