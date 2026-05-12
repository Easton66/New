"""File manager for saving/loading MediaCfg draft files."""
import json

from model.media_cfg_model import MediaCfgModel


def _json_to_model(data: dict, model=None):
    """将导出的 JSON dict 反序列化为 MediaCfgModel。"""
    if model is None:
        model = MediaCfgModel()

    # common
    if "common" in data:
        model.common.ver = data["common"].get("ver", model.common.ver)
        model.common.plat = data["common"].get("plat", model.common.plat)

    # ircut
    if "ircut" in data:
        ircut = data["ircut"]
        model.ircut.SupportIR = ircut.get("SupportIR", 1) != 0
        if "soft_sensor" in ircut:
            model.ircut.soft_sensor = ircut["soft_sensor"]
        if "soft_sensor_mask" in ircut:
            model.ircut.soft_sensor_mask = ircut["soft_sensor_mask"]
        if "d2n" in ircut:
            for k, v in ircut["d2n"].items():
                if hasattr(model.ircut.d2n, k):
                    setattr(model.ircut.d2n, k, v)
        if "n2d" in ircut:
            for k, v in ircut["n2d"].items():
                if hasattr(model.ircut.n2d, k):
                    setattr(model.ircut.n2d, k, v)

    # audio
    if "audio" in data:
        audio = data["audio"]
        for section_name, model_attr in [("ai", model.audio.ai), ("aec", model.audio.aec), ("ao", model.audio.ao)]:
            if section_name in audio:
                section = audio[section_name]
                for k, v in section.items():
                    if hasattr(model_attr, k):
                        if isinstance(getattr(model_attr, k), bool):
                            setattr(model_attr, k, v != 0)
                        else:
                            setattr(model_attr, k, v)

    # md
    if "md" in data:
        md = data["md"]
        for k in ("low", "mid", "high"):
            if k in md:
                setattr(model.md, k, md[k])

    # pipeline
    if "pipeline" in data:
        from model.media_cfg_model import (
            SensorModel, IspModel, FsEntry, YuvEntry, OsdEntry, VencEntry,
            PipelineEntry, HybridZoomModel, HybridZoomSensor,
        )
        pipe_data = data["pipeline"]
        model.pipeline.pipelines.clear()

        if "pipelines" in pipe_data:
            for pp in pipe_data["pipelines"]:
                pipe = PipelineEntry()

                if "sensor" in pp:
                    s = pp["sensor"]
                    pipe.sensor = SensorModel(
                        name=s.get("name", ""),
                        sensor_id=s.get("sensor_id", 0),
                        rst_gpio=s.get("rst_gpio", ""),
                        video_interface=s.get("video_interface"),
                        i2c_addr=s["i2c"]["addr"] if "i2c" in s else 0x30,
                    )

                if "isp" in pp:
                    i = pp["isp"]
                    af = i.get("antiflicker", {})
                    f50 = af.get("50hz", {})
                    f60 = af.get("60hz", {})
                    pipe.isp = IspModel(
                        index=i.get("index", 0),
                        blc=i["ae"]["blc"] if "ae" in i else 64,
                        FrmRateDayNum=i.get("FrmRateDayNum", 15),
                        FrmRateDayDen=i.get("FrmRateDayDen", 1),
                        FrmRateNightNum=i.get("FrmRateNightNum", 15),
                        FrmRateNightDen=i.get("FrmRateNightDen", 1),
                        antiflicker_50hz_num=f50.get("num", 25),
                        antiflicker_50hz_den=f50.get("den", 2),
                        antiflicker_60hz_num=f60.get("num", 15),
                        antiflicker_60hz_den=f60.get("den", 1),
                    )

                for fe in pp.get("fs", []):
                    pipe.fs.append(FsEntry(
                        group=fe.get("group", 0), dev_id=fe.get("dev_id", 0),
                        chn_id=fe.get("chn_id", 0), width=fe.get("width", 1920),
                        height=fe.get("height", 1080), nrvbs=fe.get("nrvbs"),
                    ))

                for ye in pp.get("yuv", []):
                    pipe.yuv.append(YuvEntry(
                        group=ye.get("group", 0), dev_id=ye.get("dev_id", 0),
                        chn_id=ye.get("chn_id", 0),
                    ))

                for oe in pp.get("osd", []):
                    inp = oe.get("input", {})
                    pipe.osd.append(OsdEntry(
                        func=oe.get("func", "ipu"),
                        input_name=inp.get("name", "fs"), input_group=inp.get("group", 0),
                        group=oe.get("group", 0), dev_id=oe.get("dev_id", 0),
                        chn_id=oe.get("chn_id", 0),
                    ))

                for ve in pp.get("venc", []):
                    inp = ve.get("input", {})
                    pipe.venc.append(VencEntry(
                        func=ve.get("func", "h26x"),
                        input_name=inp.get("name", "fs"), input_group=inp.get("group", 0),
                        group=ve.get("group", 0), dev_id=ve.get("dev_id", 0),
                        chn_id=ve.get("chn_id", 0),
                        width=ve.get("width", 1920), height=ve.get("height", 1080),
                    ))

                model.pipeline.pipelines.append(pipe)

        if "hybrid_zoom" in pipe_data:
            hz = pipe_data["hybrid_zoom"]
            model.pipeline.hybrid_zoom = HybridZoomModel(
                enable=hz.get("enable", False),
                initial_sensor_id=hz.get("initial_sensor_id", 0),
                venc_group=hz.get("venc_group"),
                sensors=[HybridZoomSensor(sensor_id=s.get("sensor_id", 0), fs_group=s.get("fs_group", 0))
                         for s in hz.get("sensors", [])],
            )

    # mapping
    if "mapping" in data:
        from model.media_cfg_model import ChannelMapping, DeviceMapping
        map_data = data["mapping"]
        model.mapping.devices.clear()

        for dev in map_data.get("devices", []):
            dm = DeviceMapping(dev_id=dev.get("dev_id", 0))
            for ch in dev.get("channels", []):
                vi = ch.get("vi", {})
                osd = ch.get("osd", {})
                venc = ch.get("venc", {})
                dm.channels.append(ChannelMapping(
                    chn_id=ch.get("chn_id", 0),
                    vi_dev_id=vi.get("dev_id", 0), vi_chn_id=vi.get("chn_id", 0),
                    osd_dev_id=osd.get("dev_id", 0), osd_chn_id=osd.get("chn_id", 0),
                    venc_dev_id=venc.get("dev_id", 0), venc_chn_id=venc.get("chn_id", 0),
                ))
            model.mapping.devices.append(dm)

    return model


def save_to_file(model: MediaCfgModel, filepath: str) -> None:
    """保存草稿到 JSON 文件。"""
    data = _model_to_dict(model)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_from_file(filepath: str) -> MediaCfgModel:
    """从 JSON 文件加载草稿。"""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return _json_to_model(data)


_DEFAULT_MEDIACFG = {
    "common": {"ver": 0, "plat": 17, "platform": "ingenic"},
    "ircut": {
        "SupportIR": 1,
        "soft_sensor_mask": 1,
        "d2n": {"d2n_luma_th": 0, "d2n_iso_th": 450, "low": 0, "th": 120981, "high": 100},
        "n2d": {"n2d_luma_th": 15, "n2d_iso_th": 3800, "low": 0, "ir": 7000, "high": 1500, "bGain": 202, "vl": 0},
    },
    "audio": {
        "ai": {"gain": 29, "vol": 60, "SampleRate": 8000, "NumPerFrm": 320, "NrLevel": 3, "NrEnable": 1, "AgcTarget": 2, "AgcMaxGain": 20, "AgcEnable": 1, "HsEnable": 0},
        "aec": {"enable": 0, "SafeSuppression": 2, "TargetLevel": 2, "CompressionGain": 20, "FarFrm": 7, "NearFrm": 4, "DelayMs": 20},
        "ao": {"gain": 24, "vol": 60, "SampleRate": 8000, "NumPerFrm": 320, "AgcTarget": 1, "AgcMaxGain": 0, "AgcEnable": 1},
    },
    "md": {"low": 45, "mid": 35, "high": 25},
    "pipeline": {
        "pipelines": [
            {
                "sensor": {"name": "mis40c1", "sensor_id": 0, "rst_gpio": "GPIO_PA(20)", "video_interface": 0, "i2c": {"addr": 48}},
                "isp": {"index": 0, "ae": {"blc": 19}, "FrmRateDayNum": 15, "FrmRateDayDen": 1, "FrmRateNightNum": 10, "FrmRateNightDen": 1, "antiflicker": {"50hz": {"num": 25, "den": 2}, "60hz": {"num": 15, "den": 1}}},
                "fs": [
                    {"group": 0, "dev_id": 0, "chn_id": 0, "width": 2976, "height": 1696},
                    {"group": 1, "dev_id": 0, "chn_id": 1, "width": 640, "height": 360, "nrvbs": 2},
                ],
                "osd": [
                    {"func": "ipu", "input": {"name": "fs", "group": 1}, "group": 1, "dev_id": 0, "chn_id": 1},
                ],
                "venc": [
                    {"func": "h26x", "input": {"name": "fs", "group": 0}, "group": 0, "dev_id": 0, "chn_id": 0, "width": 2976, "height": 1696},
                    {"func": "h26x", "input": {"name": "osd", "group": 1}, "group": 1, "dev_id": 0, "chn_id": 1, "width": 640, "height": 360},
                ],
            }
        ]
    },
    "mapping": {
        "devices": [
            {
                "dev_id": 0,
                "channels": [
                    {"chn_id": 0, "vi": {"dev_id": 0, "chn_id": 0}, "osd": {"dev_id": 0, "chn_id": 0}, "venc": {"dev_id": 0, "chn_id": 0}},
                    {"chn_id": 1, "vi": {"dev_id": 0, "chn_id": 1}, "osd": {"dev_id": 0, "chn_id": 1}, "venc": {"dev_id": 0, "chn_id": 1}},
                ],
            }
        ]
    },
}


def load_default_model() -> MediaCfgModel:
    """加载内置默认配置模板。"""
    import copy
    return _json_to_model(copy.deepcopy(_DEFAULT_MEDIACFG))


def _model_to_dict(model: MediaCfgModel) -> dict:
    """将 Model 转换为可保存的 dict（复用导出逻辑）。"""
    from core.json_exporter import _build_export_dict
    return _build_export_dict(model)
