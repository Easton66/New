# -*- coding: utf-8 -*-
"""MediaCfg data model - single source of truth for all configuration."""
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class CommonModel:
    """common 模块"""
    ver: int = 0
    plat: int = 17


@dataclass
class IrcutD2N:
    """ircut 日夜切换 - 日→夜"""
    d2n_luma_th: int = 0
    d2n_iso_th: int = 2000
    low: int = 0
    th: int = 120981
    high: int = 100


@dataclass
class IrcutN2D:
    """ircut 日夜切换 - 夜→日"""
    n2d_luma_th: int = 15
    n2d_iso_th: int = 20000
    low: int = 0
    ir: int = 6741
    high: int = 1500
    bGain: int = 240
    vl: int = 0


@dataclass
class IrcutModel:
    """ircut 模块"""
    SupportIR: bool = True
    soft_sensor: Optional[int] = None
    soft_sensor_mask: Optional[int] = None
    d2n: IrcutD2N = field(default_factory=IrcutD2N)
    n2d: IrcutN2D = field(default_factory=IrcutN2D)


@dataclass
class AudioAiModel:
    """audio - 音频输入"""
    gain: int = 31
    vol: int = 60
    SampleRate: int = 8000
    NumPerFrm: int = 320
    NrLevel: int = 2
    NrEnable: bool = True
    AgcTarget: int = 1
    AgcMaxGain: int = 10
    AgcEnable: bool = True
    HsEnable: bool = False


@dataclass
class AudioAecModel:
    """audio - AEC 回声消除"""
    enable: bool = False
    SafeSuppression: int = 2
    TargetLevel: int = 3
    CompressionGain: int = 18
    FarFrm: int = 7
    NearFrm: int = 4
    DelayMs: int = 20


@dataclass
class AudioAoModel:
    """audio - 音频输出"""
    gain: int = 22
    vol: int = 60
    SampleRate: int = 8000
    NumPerFrm: int = 320
    AgcTarget: int = 1
    AgcMaxGain: int = 0
    AgcEnable: bool = True


@dataclass
class AudioModel:
    """audio 模块"""
    ai: AudioAiModel = field(default_factory=AudioAiModel)
    aec: AudioAecModel = field(default_factory=AudioAecModel)
    ao: AudioAoModel = field(default_factory=AudioAoModel)


@dataclass
class MdModel:
    """md 移动侦测模块"""
    low: int = 45
    mid: int = 35
    high: int = 25


@dataclass
class SensorModel:
    """pipeline - 单个 sensor 基础配置"""
    name: str = ""
    sensor_id: int = 0
    rst_gpio: str = ""
    video_interface: Optional[int] = None
    i2c_addr: int = 0x30  # 内部存储为 int，显示时转换十六进制


@dataclass
class IspModel:
    """pipeline - ISP 配置"""
    index: int = 0
    blc: int = 64
    FrmRateDayNum: int = 15
    FrmRateDayDen: int = 1
    FrmRateNightNum: int = 15
    FrmRateNightDen: int = 1
    antiflicker_50hz_num: int = 25
    antiflicker_50hz_den: int = 2
    antiflicker_60hz_num: int = 15
    antiflicker_60hz_den: int = 1


@dataclass
class FsEntry:
    """pipeline - 帧源条目"""
    group: int = 0
    dev_id: int = 0
    chn_id: int = 0
    width: int = 1920
    height: int = 1080
    nrvbs: Optional[int] = None


@dataclass
class YuvEntry:
    """pipeline - YUV 条目"""
    group: int = 0
    dev_id: int = 0
    chn_id: int = 0


@dataclass
class OsdEntry:
    """pipeline - OSD 条目"""
    func: str = "ipu"
    input_name: str = "fs"
    input_group: int = 0
    group: int = 0
    dev_id: int = 0
    chn_id: int = 0


@dataclass
class VencEntry:
    """pipeline - VENC 编码条目"""
    func: str = "h26x"
    input_name: str = "fs"
    input_group: int = 0
    group: int = 0
    dev_id: int = 0
    chn_id: int = 0
    width: int = 1920
    height: int = 1080


@dataclass
class PipelineEntry:
    """pipeline - 单个 pipeline（一个 sensor 对应一个 pipeline）"""
    sensor: SensorModel = field(default_factory=SensorModel)
    isp: IspModel = field(default_factory=IspModel)
    fs: List[FsEntry] = field(default_factory=list)
    yuv: List[YuvEntry] = field(default_factory=list)
    osd: List[OsdEntry] = field(default_factory=list)
    venc: List[VencEntry] = field(default_factory=list)


@dataclass
class HybridZoomSensor:
    """pipeline - hybrid_zoom 子 sensor"""
    sensor_id: int = 0
    fs_group: int = 0


@dataclass
class HybridZoomModel:
    """pipeline - 混合变焦"""
    enable: bool = False
    initial_sensor_id: int = 0
    venc_group: Optional[int] = None
    sensors: List[HybridZoomSensor] = field(default_factory=list)


@dataclass
class PipelineModel:
    """pipeline 模块"""
    pipelines: List[PipelineEntry] = field(default_factory=list)
    hybrid_zoom: HybridZoomModel = field(default_factory=HybridZoomModel)


@dataclass
class ChannelMapping:
    """mapping - 单个通道映射"""
    chn_id: int = 0
    vi_dev_id: int = 0
    vi_chn_id: int = 0
    osd_dev_id: int = 0
    osd_chn_id: int = 0
    venc_dev_id: int = 0
    venc_chn_id: int = 0


@dataclass
class DeviceMapping:
    """mapping - 单个设备"""
    dev_id: int = 0
    channels: List[ChannelMapping] = field(default_factory=list)


@dataclass
class MappingModel:
    """mapping 模块"""
    devices: List[DeviceMapping] = field(default_factory=list)


@dataclass
class MediaCfgModel:
    """MediaCfg 总模型 - 单一数据源"""
    common: CommonModel = field(default_factory=CommonModel)
    ircut: IrcutModel = field(default_factory=IrcutModel)
    audio: AudioModel = field(default_factory=AudioModel)
    md: MdModel = field(default_factory=MdModel)
    pipeline: PipelineModel = field(default_factory=PipelineModel)
    mapping: MappingModel = field(default_factory=MappingModel)
