"""Pipeline 管道配置标签页."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton,
    QListWidget, QListWidgetItem, QStackedWidget, QSpinBox, QComboBox,
    QCheckBox, QGroupBox, QScrollArea, QDialog, QDialogButtonBox, QAbstractItemView,
)

from core.dropdown_store import DropdownStore
from model.media_cfg_model import (
    PipelineModel, PipelineEntry, SensorModel, IspModel,
    FsEntry, YuvEntry, OsdEntry, VencEntry,
    HybridZoomModel, HybridZoomSensor,
)


class EntryEditDialog(QDialog):
    """FS/YUV/OSD/VENC 条目编辑对话框。"""

    def __init__(self, entry, entry_type: str, dropdown: DropdownStore, parent=None):
        super().__init__(parent)
        self._entry = entry
        self._dropdown = dropdown
        self.setWindowTitle(f"编辑 {entry_type.upper()} 条目")
        self._setup(entry_type)

    def _setup(self, entry_type):
        layout = QFormLayout(self)

        if entry_type == "fs":
            self._add_spin("group", "group:")
            self._add_spin("dev_id", "dev_id:")
            self._add_spin("chn_id", "chn_id:")
            self._add_spin("width", "width:")
            self._add_spin("height", "height:")
            nrvbs = QSpinBox(); nrvbs.setRange(-1, 99)
            val = self._entry.nrvbs
            nrvbs.setValue(val if val is not None else -1)
            nrvbs.setSpecialValueText("无")
            setattr(self, "_field_nrvbs", nrvbs)
            layout.addRow("nrvbs:", nrvbs)

        elif entry_type == "yuv":
            self._add_spin("group", "group:")
            self._add_spin("dev_id", "dev_id:")
            self._add_spin("chn_id", "chn_id:")

        elif entry_type in ("osd", "venc"):
            self._add_combo("func", "func:", "pipeline", f"{entry_type}.func")
            self._add_combo("input_name", "input.name:", "pipeline", "venc.func")
            self._add_spin("input_group", "input.group:")
            self._add_spin("group", "group:")
            self._add_spin("dev_id", "dev_id:")
            self._add_spin("chn_id", "chn_id:")
            if entry_type == "venc":
                self._add_spin("width", "width:")
                self._add_spin("height", "height:")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _add_spin(self, attr, label):
        w = QSpinBox(); w.setRange(-1, 999999)
        w.setValue(getattr(self._entry, attr, 0))
        setattr(self, f"_field_{attr}", w)
        self.layout().addRow(label, w)

    def _add_combo(self, attr, label, section, dkey):
        w = QComboBox(); w.setEditable(True)
        for v in self._dropdown.get_options(section, dkey):
            w.addItem(str(v))
        val = getattr(self._entry, attr, "")
        w.setCurrentText(str(val))
        setattr(self, f"_field_{attr}", w)
        self.layout().addRow(label, w)

    def _on_accept(self):
        e = self._entry
        if isinstance(e, FsEntry):
            e.group = getattr(self, "_field_group").value()
            e.dev_id = getattr(self, "_field_dev_id").value()
            e.chn_id = getattr(self, "_field_chn_id").value()
            e.width = getattr(self, "_field_width").value()
            e.height = getattr(self, "_field_height").value()
            nrvbs = getattr(self, "_field_nrvbs").value()
            e.nrvbs = nrvbs if nrvbs >= 0 else None
        elif isinstance(e, YuvEntry):
            e.group = getattr(self, "_field_group").value()
            e.dev_id = getattr(self, "_field_dev_id").value()
            e.chn_id = getattr(self, "_field_chn_id").value()
        elif isinstance(e, (OsdEntry, VencEntry)):
            e.func = getattr(self, "_field_func").currentText()
            e.input_name = getattr(self, "_field_input_name").currentText()
            e.input_group = getattr(self, "_field_input_group").value()
            e.group = getattr(self, "_field_group").value()
            e.dev_id = getattr(self, "_field_dev_id").value()
            e.chn_id = getattr(self, "_field_chn_id").value()
            if isinstance(e, VencEntry):
                e.width = getattr(self, "_field_width").value()
                e.height = getattr(self, "_field_height").value()
        self.accept()


class PipelineTab(QWidget):
    """pipeline 配置标签页。"""

    def __init__(self, dropdown: DropdownStore, parent=None):
        super().__init__(parent)
        self._dropdown = dropdown
        self._model = None
        self._hz_sensors = []
        self._current_pipe_index = -1
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        # --- 顶部：Sensor 管道列表 ---
        top_layout = QHBoxLayout()
        self._pipe_list = QListWidget()
        self._pipe_list.setMaximumHeight(100)
        self._pipe_list.setFlow(QListWidget.LeftToRight)
        self._pipe_list.setWrapping(False)
        self._pipe_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self._pipe_list.currentRowChanged.connect(self._on_pipe_selected)
        top_layout.addWidget(self._pipe_list, 1)

        btn_layout = QVBoxLayout()
        self._add_pipe_btn = QPushButton("+ 添加 Sensor")
        self._add_pipe_btn.clicked.connect(self._add_pipe)
        self._remove_pipe_btn = QPushButton("删除 Sensor")
        self._remove_pipe_btn.clicked.connect(self._remove_pipe)
        btn_layout.addWidget(self._add_pipe_btn)
        btn_layout.addWidget(self._remove_pipe_btn)
        btn_layout.addStretch()
        top_layout.addLayout(btn_layout)
        main_layout.addLayout(top_layout)

        # --- 中间：Sensor 详细配置 ---
        self._detail_stack = QStackedWidget()
        main_layout.addWidget(self._detail_stack, 1)

        # --- 底部：Hybrid Zoom ---
        self._setup_hybrid_zoom()
        main_layout.addWidget(self._hz_group)

    def _create_pipe_detail(self, pipe: PipelineEntry) -> QWidget:
        """为单个 pipeline 创建详情面板。"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)

        # Sensor 基础
        sensor_group = QGroupBox("Sensor 基础")
        s_layout = QFormLayout(sensor_group)
        s_widgets = {}

        for dkey, attr, label in [("sensor.name", "name", "name:"), ("sensor.rst_gpio", "rst_gpio", "rst_gpio:"), ("sensor.video_interface", "video_interface", "video_interface:"), ("sensor.i2c.addr", "i2c_addr", "i2c_addr:")]:
            combo = QComboBox(); combo.setEditable(True)
            for v in self._dropdown.get_options("pipeline", dkey):
                combo.addItem(str(v))
            s_widgets[attr] = combo
            s_layout.addRow(label, combo)

        sid_spin = QSpinBox(); sid_spin.setRange(0, 99); s_widgets["sensor_id"] = sid_spin
        s_layout.addRow("sensor_id:", sid_spin)
        sensor_group._sw = s_widgets
        layout.addWidget(sensor_group)

        # sensor_id 或 name 变化时同步更新左侧列表项名称
        def _update_pipe_name():
            idx = self._detail_stack.indexOf(scroll)
            if idx >= 0:
                name = s_widgets["name"].currentText() or f"Sensor {s_widgets['sensor_id'].value()}"
                self._pipe_list.item(idx).setText(name)
        sid_spin.valueChanged.connect(lambda _: _update_pipe_name())
        s_widgets["name"].currentTextChanged.connect(lambda _: _update_pipe_name())

        # ISP
        isp_group = QGroupBox("ISP")
        i_layout = QFormLayout(isp_group)
        i_widgets = {}

        idx = QSpinBox(); idx.setRange(0, 9); i_widgets["index"] = idx
        i_layout.addRow("index:", idx)
        blc = QSpinBox(); blc.setRange(0, 255); i_widgets["blc"] = blc
        i_layout.addRow("blc:", blc)

        for label, nk, dk in [("日间帧率", "FrmRateDayNum", "FrmRateDayDen"), ("夜间帧率", "FrmRateNightNum", "FrmRateNightDen")]:
            num = QSpinBox(); num.setRange(1, 60); i_widgets[nk] = num
            den = QSpinBox(); den.setRange(1, 60); i_widgets[dk] = den
            row = QHBoxLayout(); row.addWidget(num); row.addWidget(den)
            i_layout.addRow(f"{label} (num/den):", row)

        for hz, nk, dk in [("50hz", "antiflicker_50hz_num", "antiflicker_50hz_den"), ("60hz", "antiflicker_60hz_num", "antiflicker_60hz_den")]:
            num = QSpinBox(); num.setRange(1, 60); i_widgets[nk] = num
            den = QSpinBox(); den.setRange(1, 60); i_widgets[dk] = den
            row = QHBoxLayout(); row.addWidget(num); row.addWidget(den)
            i_layout.addRow(f"antiflicker {hz} (num/den):", row)

        isp_group._iw = i_widgets
        layout.addWidget(isp_group)

        # FS / YUV / OSD / VENC 列表
        lists_layout = QHBoxLayout()
        self._setup_entry_list(lists_layout, "FS 帧源", FsEntry, "fs", pipe)
        self._setup_entry_list(lists_layout, "YUV", YuvEntry, "yuv", pipe)
        self._setup_entry_list(lists_layout, "OSD", OsdEntry, "osd", pipe)
        self._setup_entry_list(lists_layout, "VENC", VencEntry, "venc", pipe)
        layout.addLayout(lists_layout)

        container._sw = s_widgets
        container._iw = i_widgets
        container._pipe_ref = pipe

        scroll.setWidget(container)
        return scroll

    def _setup_entry_list(self, parent_layout, title, entry_class, entry_type, pipe):
        """创建条目列表组件。"""
        group = QGroupBox(title)
        vbox = QVBoxLayout(group)
        lst = QListWidget()
        vbox.addWidget(lst)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("+ 添加")
        remove_btn = QPushButton("删除")
        btn_row.addWidget(add_btn)
        btn_row.addWidget(remove_btn)
        vbox.addLayout(btn_row)

        group._lst = lst
        group._entry_type = entry_type
        group._pipe_ref = pipe

        def get_entries(p):
            if entry_type == "fs": return p.fs
            elif entry_type == "yuv": return p.yuv
            elif entry_type == "osd": return p.osd
            else: return p.venc

        add_btn.clicked.connect(lambda: self._add_entry(group, entry_class, entry_type))
        remove_btn.clicked.connect(lambda: self._remove_entry(group))

        parent_layout.addWidget(group)

    def _add_entry(self, group_widget, entry_class, entry_type):
        entry = entry_class()
        dialog = EntryEditDialog(entry, entry_type, self._dropdown, self)
        if dialog.exec() == QDialog.Accepted:
            pipe = group_widget._pipe_ref
            if entry_type == "fs": pipe.fs.append(entry)
            elif entry_type == "yuv": pipe.yuv.append(entry)
            elif entry_type == "osd": pipe.osd.append(entry)
            else: pipe.venc.append(entry)
            self._refresh_entry_list(group_widget)

    def _remove_entry(self, group_widget):
        lst = group_widget._lst
        pipe = group_widget._pipe_ref
        idx = lst.currentRow()
        if idx < 0: return

        if group_widget._entry_type == "fs": pipe.fs.pop(idx)
        elif group_widget._entry_type == "yuv": pipe.yuv.pop(idx)
        elif group_widget._entry_type == "osd": pipe.osd.pop(idx)
        else: pipe.venc.pop(idx)
        self._refresh_entry_list(group_widget)

    def _refresh_entry_list(self, group_widget):
        lst = group_widget._lst
        pipe = group_widget._pipe_ref
        lst.clear()

        if group_widget._entry_type == "fs":
            entries = pipe.fs
            for e in entries:
                lst.addItem(f"g{e.group} dev{e.dev_id} ch{e.chn_id} {e.width}x{e.height}")
        elif group_widget._entry_type == "yuv":
            entries = pipe.yuv
            for e in entries:
                lst.addItem(f"g{e.group} dev{e.dev_id} ch{e.chn_id}")
        elif group_widget._entry_type == "osd":
            entries = pipe.osd
            for e in entries:
                lst.addItem(f"{e.func} ← {e.input_name} g{e.input_group} → g{e.group} dev{e.dev_id} ch{e.chn_id}")
        else:
            entries = pipe.venc
            for e in entries:
                lst.addItem(f"{e.func} ← {e.input_name} g{e.input_group} → g{e.group} dev{e.dev_id} ch{e.chn_id} {e.width}x{e.height}")

    # ---- Hybrid Zoom ----
    def _setup_hybrid_zoom(self):
        self._hz_group = QGroupBox("Hybrid Zoom")
        hz_layout = QVBoxLayout(self._hz_group)

        self._hz_enable = QCheckBox("enable")
        hz_layout.addWidget(self._hz_enable)

        form = QFormLayout()
        self._hz_initial_sensor = QSpinBox(); self._hz_initial_sensor.setRange(0, 9)
        form.addRow("initial_sensor_id:", self._hz_initial_sensor)
        self._hz_venc_group = QSpinBox(); self._hz_venc_group.setRange(0, 99)
        self._hz_venc_group.setSpecialValueText("无")
        form.addRow("venc_group:", self._hz_venc_group)
        hz_layout.addLayout(form)

        self._hz_sensors_list = QListWidget()
        self._hz_sensors_list.setMaximumHeight(80)
        hz_layout.addWidget(self._hz_sensors_list)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("+ 添加 Sensor"); add_btn.clicked.connect(self._add_hz_sensor)
        remove_btn = QPushButton("删除"); remove_btn.clicked.connect(self._remove_hz_sensor)
        btn_row.addWidget(add_btn); btn_row.addWidget(remove_btn)
        hz_layout.addLayout(btn_row)

    def _add_hz_sensor(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("添加 Hybrid Zoom Sensor")
        layout = QFormLayout(dialog)
        sid = QSpinBox(); sid.setRange(0, 9); layout.addRow("sensor_id:", sid)
        fg = QSpinBox(); fg.setRange(0, 99); layout.addRow("fs_group:", fg)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept); buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        if dialog.exec() == QDialog.Accepted:
            self._hz_sensors.append(HybridZoomSensor(sensor_id=sid.value(), fs_group=fg.value()))
            self._refresh_hz_list()

    def _remove_hz_sensor(self):
        idx = self._hz_sensors_list.currentRow()
        if 0 <= idx < len(self._hz_sensors):
            del self._hz_sensors[idx]
            self._refresh_hz_list()

    def _refresh_hz_list(self):
        self._hz_sensors_list.clear()
        for s in self._hz_sensors:
            self._hz_sensors_list.addItem(f"sensor_id={s.sensor_id} fs_group={s.fs_group}")

    # ---- Model 双向绑定 ----
    def load_model(self, model: PipelineModel):
        self._model = model
        self._hz_sensors = list(model.hybrid_zoom.sensors)
        self._pipe_list.clear()
        # 清理旧 widget
        while self._detail_stack.count() > 0:
            w = self._detail_stack.widget(0)
            self._detail_stack.removeWidget(w)
            w.deleteLater()

        for pipe in model.pipelines:
            sensor_name = pipe.sensor.name or f"Sensor {pipe.sensor.sensor_id}"
            self._pipe_list.addItem(sensor_name)
            detail = self._create_pipe_detail(pipe)
            self._detail_stack.addWidget(detail)
            self._load_pipe_detail(detail, pipe)

        self._hz_enable.setChecked(model.hybrid_zoom.enable)
        self._hz_initial_sensor.setValue(model.hybrid_zoom.initial_sensor_id)
        if model.hybrid_zoom.venc_group is not None:
            self._hz_venc_group.setValue(model.hybrid_zoom.venc_group)
        else:
            self._hz_venc_group.setValue(0)
        self._refresh_hz_list()

        if model.pipelines:
            self._pipe_list.setCurrentRow(0)

    def save_model(self, model: PipelineModel):
        if 0 <= self._current_pipe_index < self._detail_stack.count():
            self._save_current_detail()

        model.hybrid_zoom.enable = self._hz_enable.isChecked()
        model.hybrid_zoom.initial_sensor_id = self._hz_initial_sensor.value()
        model.hybrid_zoom.venc_group = self._hz_venc_group.value() if self._hz_venc_group.value() > 0 else None
        model.hybrid_zoom.sensors = list(self._hz_sensors)

    def _load_pipe_detail(self, detail, pipe):
        sw = detail._sw
        sw["name"].setCurrentText(pipe.sensor.name)
        sw["sensor_id"].setValue(pipe.sensor.sensor_id)
        sw["rst_gpio"].setCurrentText(pipe.sensor.rst_gpio)
        if pipe.sensor.video_interface is not None:
            sw["video_interface"].setCurrentText(str(pipe.sensor.video_interface))
        else:
            sw["video_interface"].setCurrentText("")
        sw["i2c_addr"].setCurrentText(hex(pipe.sensor.i2c_addr))

        iw = detail._iw
        iw["index"].setValue(pipe.isp.index)
        iw["blc"].setValue(pipe.isp.blc)
        iw["FrmRateDayNum"].setValue(pipe.isp.FrmRateDayNum)
        iw["FrmRateDayDen"].setValue(pipe.isp.FrmRateDayDen)
        iw["FrmRateNightNum"].setValue(pipe.isp.FrmRateNightNum)
        iw["FrmRateNightDen"].setValue(pipe.isp.FrmRateNightDen)
        iw["antiflicker_50hz_num"].setValue(pipe.isp.antiflicker_50hz_num)
        iw["antiflicker_50hz_den"].setValue(pipe.isp.antiflicker_50hz_den)
        iw["antiflicker_60hz_num"].setValue(pipe.isp.antiflicker_60hz_num)
        iw["antiflicker_60hz_den"].setValue(pipe.isp.antiflicker_60hz_den)

        # 刷新条目列表
        for child in detail.findChildren(QGroupBox):
            if hasattr(child, '_lst'):
                self._refresh_entry_list(child)

    def _save_current_detail(self):
        if self._current_pipe_index < 0:
            return
        detail = self._detail_stack.currentWidget()
        if detail is None:
            return
        pipe = detail._pipe_ref

        sw = detail._sw
        pipe.sensor.name = sw["name"].currentText()
        pipe.sensor.sensor_id = sw["sensor_id"].value()
        pipe.sensor.rst_gpio = sw["rst_gpio"].currentText()
        vi_text = sw["video_interface"].currentText()
        pipe.sensor.video_interface = int(vi_text) if vi_text.strip() else None
        try:
            pipe.sensor.i2c_addr = int(sw["i2c_addr"].currentText(), 16)
        except ValueError:
            pipe.sensor.i2c_addr = 0x30

        iw = detail._iw
        pipe.isp.index = iw["index"].value()
        pipe.isp.blc = iw["blc"].value()
        pipe.isp.FrmRateDayNum = iw["FrmRateDayNum"].value()
        pipe.isp.FrmRateDayDen = iw["FrmRateDayDen"].value()
        pipe.isp.FrmRateNightNum = iw["FrmRateNightNum"].value()
        pipe.isp.FrmRateNightDen = iw["FrmRateNightDen"].value()
        pipe.isp.antiflicker_50hz_num = iw["antiflicker_50hz_num"].value()
        pipe.isp.antiflicker_50hz_den = iw["antiflicker_50hz_den"].value()
        pipe.isp.antiflicker_60hz_num = iw["antiflicker_60hz_num"].value()
        pipe.isp.antiflicker_60hz_den = iw["antiflicker_60hz_den"].value()

    def _on_pipe_selected(self, index):
        if index >= 0 and self._current_pipe_index >= 0:
            self._save_current_detail()
        self._current_pipe_index = index
        if 0 <= index < self._detail_stack.count():
            self._detail_stack.setCurrentIndex(index)

    def _add_pipe(self):
        # 自动递增 sensor_id：取已有 pipeline 中最大 sensor_id + 1
        max_sid = -1
        for p in self._model.pipelines:
            if p.sensor.sensor_id > max_sid:
                max_sid = p.sensor.sensor_id
        pipe = PipelineEntry()
        pipe.sensor.sensor_id = max_sid + 1
        self._model.pipelines.append(pipe)
        self._pipe_list.addItem(f"Sensor {pipe.sensor.sensor_id}")
        detail = self._create_pipe_detail(pipe)
        self._detail_stack.addWidget(detail)
        self._load_pipe_detail(detail, pipe)
        self._pipe_list.setCurrentRow(self._pipe_list.count() - 1)

    def _remove_pipe(self):
        idx = self._current_pipe_index
        if idx < 0 or not self._model:
            return
        self._model.pipelines.pop(idx)
        self._pipe_list.takeItem(idx)
        w = self._detail_stack.widget(idx)
        self._detail_stack.removeWidget(w)
        w.deleteLater()
        self._current_pipe_index = -1
        if self._pipe_list.count() > 0:
            self._pipe_list.setCurrentRow(0)
