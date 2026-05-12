"""Export MediaCfgModel to JSON."""
import json

from model.media_cfg_model import MediaCfgModel


def _build_export_dict(model: MediaCfgModel) -> dict:
    """将 MediaCfgModel 转换为 MediaCfg JSON 格式的 dict。"""
    result = {}

    # common
    result["common"] = {
        "ver": model.common.ver,
        "plat": model.common.plat,
    }

    # ircut
    ircut = {"SupportIR": 1 if model.ircut.SupportIR else 0}
    if model.ircut.soft_sensor is not None:
        ircut["soft_sensor"] = model.ircut.soft_sensor
    if model.ircut.soft_sensor_mask is not None:
        ircut["soft_sensor_mask"] = model.ircut.soft_sensor_mask
    ircut["d2n"] = {
        "d2n_luma_th": model.ircut.d2n.d2n_luma_th,
        "d2n_iso_th": model.ircut.d2n.d2n_iso_th,
        "low": model.ircut.d2n.low,
        "th": model.ircut.d2n.th,
        "high": model.ircut.d2n.high,
    }
    ircut["n2d"] = {
        "n2d_luma_th": model.ircut.n2d.n2d_luma_th,
        "n2d_iso_th": model.ircut.n2d.n2d_iso_th,
        "low": model.ircut.n2d.low,
        "ir": model.ircut.n2d.ir,
        "high": model.ircut.n2d.high,
        "bGain": model.ircut.n2d.bGain,
        "vl": model.ircut.n2d.vl,
    }
    result["ircut"] = ircut

    # audio
    audio = {
        "ai": {
            "gain": model.audio.ai.gain,
            "vol": model.audio.ai.vol,
            "SampleRate": model.audio.ai.SampleRate,
            "NumPerFrm": model.audio.ai.NumPerFrm,
            "NrLevel": model.audio.ai.NrLevel,
            "NrEnable": 1 if model.audio.ai.NrEnable else 0,
            "AgcTarget": model.audio.ai.AgcTarget,
            "AgcMaxGain": model.audio.ai.AgcMaxGain,
            "AgcEnable": 1 if model.audio.ai.AgcEnable else 0,
            "HsEnable": 1 if model.audio.ai.HsEnable else 0,
        },
        "aec": {
            "enable": 1 if model.audio.aec.enable else 0,
            "SafeSuppression": model.audio.aec.SafeSuppression,
            "TargetLevel": model.audio.aec.TargetLevel,
            "CompressionGain": model.audio.aec.CompressionGain,
            "FarFrm": model.audio.aec.FarFrm,
            "NearFrm": model.audio.aec.NearFrm,
            "DelayMs": model.audio.aec.DelayMs,
        },
        "ao": {
            "gain": model.audio.ao.gain,
            "vol": model.audio.ao.vol,
            "SampleRate": model.audio.ao.SampleRate,
            "NumPerFrm": model.audio.ao.NumPerFrm,
            "AgcTarget": model.audio.ao.AgcTarget,
            "AgcMaxGain": model.audio.ao.AgcMaxGain,
            "AgcEnable": 1 if model.audio.ao.AgcEnable else 0,
        },
    }
    result["audio"] = audio

    # md
    result["md"] = {
        "low": model.md.low,
        "mid": model.md.mid,
        "high": model.md.high,
    }

    # pipeline
    pipelines = []
    for pipe in model.pipeline.pipelines:
        p = {}
        # sensor
        sensor = {
            "name": pipe.sensor.name,
            "sensor_id": pipe.sensor.sensor_id,
            "rst_gpio": pipe.sensor.rst_gpio,
            "i2c": {"addr": pipe.sensor.i2c_addr},
        }
        if pipe.sensor.video_interface is not None:
            sensor["video_interface"] = pipe.sensor.video_interface
        p["sensor"] = sensor

        # isp
        isp = {
            "index": pipe.isp.index,
            "ae": {"blc": pipe.isp.blc},
            "FrmRateDayNum": pipe.isp.FrmRateDayNum,
            "FrmRateDayDen": pipe.isp.FrmRateDayDen,
            "FrmRateNightNum": pipe.isp.FrmRateNightNum,
            "FrmRateNightDen": pipe.isp.FrmRateNightDen,
            "antiflicker": {
                "50hz": {"num": pipe.isp.antiflicker_50hz_num, "den": pipe.isp.antiflicker_50hz_den},
                "60hz": {"num": pipe.isp.antiflicker_60hz_num, "den": pipe.isp.antiflicker_60hz_den},
            },
        }
        p["isp"] = isp

        # fs
        fs_list = []
        for fs in pipe.fs:
            entry = {"group": fs.group, "dev_id": fs.dev_id, "chn_id": fs.chn_id,
                     "width": fs.width, "height": fs.height}
            if fs.nrvbs is not None:
                entry["nrvbs"] = fs.nrvbs
            fs_list.append(entry)
        p["fs"] = fs_list

        # yuv
        if pipe.yuv:
            yuv_list = []
            for yv in pipe.yuv:
                yuv_list.append({"group": yv.group, "dev_id": yv.dev_id, "chn_id": yv.chn_id})
            p["yuv"] = yuv_list

        # osd
        osd_list = []
        for od in pipe.osd:
            osd_list.append({
                "func": od.func,
                "input": {"name": od.input_name, "group": od.input_group},
                "group": od.group, "dev_id": od.dev_id, "chn_id": od.chn_id,
            })
        p["osd"] = osd_list

        # venc
        venc_list = []
        for ve in pipe.venc:
            venc_list.append({
                "func": ve.func,
                "input": {"name": ve.input_name, "group": ve.input_group},
                "group": ve.group, "dev_id": ve.dev_id, "chn_id": ve.chn_id,
                "width": ve.width, "height": ve.height,
            })
        p["venc"] = venc_list

        pipelines.append(p)

    # hybrid_zoom
    hz = model.pipeline.hybrid_zoom
    hz_sensors = []
    for s in hz.sensors:
        hz_sensors.append({"sensor_id": s.sensor_id, "fs_group": s.fs_group})

    hybrid_zoom = {"enable": hz.enable}
    if hz.initial_sensor_id is not None:
        hybrid_zoom["initial_sensor_id"] = hz.initial_sensor_id
    if hz.venc_group is not None:
        hybrid_zoom["venc_group"] = hz.venc_group
    if hz_sensors:
        hybrid_zoom["sensors"] = hz_sensors

    result["pipeline"] = {
        "pipelines": pipelines,
        "hybrid_zoom": hybrid_zoom,
    }

    # mapping
    devices = []
    for dev in model.mapping.devices:
        channels = []
        for ch in dev.channels:
            channels.append({
                "chn_id": ch.chn_id,
                "vi": {"dev_id": ch.vi_dev_id, "chn_id": ch.vi_chn_id},
                "osd": {"dev_id": ch.osd_dev_id, "chn_id": ch.osd_chn_id},
                "venc": {"dev_id": ch.venc_dev_id, "chn_id": ch.venc_chn_id},
            })
        devices.append({"dev_id": dev.dev_id, "channels": channels})
    result["mapping"] = {"devices": devices}

    return result


def export_to_json(model: MediaCfgModel, indent: int = 4) -> str:
    """导出为 JSON 字符串。"""
    data = _build_export_dict(model)
    return json.dumps(data, indent=indent, ensure_ascii=False)


def export_to_file(model: MediaCfgModel, filepath: str) -> None:
    """导出到文件。"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(export_to_json(model))


def export_to_clipboard(model: MediaCfgModel) -> None:
    """导出到系统剪贴板。"""
    from PySide6.QtWidgets import QApplication
    json_str = export_to_json(model)
    QApplication.clipboard().setText(json_str)
