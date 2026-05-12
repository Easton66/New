"""Auto-generate Mapping from Pipeline configuration."""
from collections import OrderedDict

from model.media_cfg_model import PipelineModel, MappingModel, DeviceMapping, ChannelMapping


def generate_mapping(pipeline: PipelineModel) -> MappingModel:
    """从所有 pipeline 的 VENC 列表自动生成 Mapping。

    规则：
    - 每个 VENC 的 {dev_id, chn_id} 对应一个 Channel
    - VI/OSD 的 {dev_id, chn_id} 取自 VENC 输入源
    """
    dev_channels = {}

    for pipe in pipeline.pipelines:
        for venc in pipe.venc:
            dev_id = venc.dev_id
            chn_id = venc.chn_id
            # VI 和 OSD 的 dev_id/chn_id 取自 input 源
            input_dev_id = dev_id
            input_chn_id = chn_id
            if venc.input_name == "fs":
                for fs in pipe.fs:
                    if fs.group == venc.input_group:
                        input_dev_id = fs.dev_id
                        input_chn_id = fs.chn_id
                        break
            elif venc.input_name == "osd":
                for osd in pipe.osd:
                    if osd.group == venc.input_group:
                        input_dev_id = osd.dev_id
                        input_chn_id = osd.chn_id
                        break

            if dev_id not in dev_channels:
                dev_channels[dev_id] = []
            dev_channels[dev_id].append((chn_id, input_dev_id, input_chn_id))

    # 构建 MappingModel
    mapping = MappingModel()
    for dev_id in sorted(dev_channels.keys()):
        dm = DeviceMapping(dev_id=dev_id)
        channels = dev_channels[dev_id]
        for chn_id, input_dev, input_chn in channels:
            dm.channels.append(ChannelMapping(
                chn_id=chn_id,
                vi_dev_id=input_dev, vi_chn_id=input_chn,
                osd_dev_id=input_dev, osd_chn_id=input_chn,
                venc_dev_id=dev_id, venc_chn_id=chn_id,
            ))
        mapping.devices.append(dm)

    return mapping
