#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from base import BaseNode
from dayu_ffmpeg.config import CODEC_ORDER_SCORE

class BaseCodecNode(BaseNode):
    type = 'base_code_node'
    order_score = CODEC_ORDER_SCORE

    def simple_cmd_string(self):
        return self.type

    def complex_cmd_string(self):
        return '{stream_in}{cmd}{stream_out}'.format(
                stream_in=''.join(['[{}]'.format(x) for x in self.stream_in_num]),
                cmd=self.simple_cmd_string(),
                stream_out='[{}]'.format(self.stream_out_num))


class Codec(BaseCodecNode):
    type = 'codec'

    def __init__(self, video='prores_ks', audio=None, **kwargs):
        self.video = video
        self.audio = audio
        super(Codec, self).__init__(**kwargs)

    def simple_cmd_string(self):
        self._cmd = u'-codec:v {video}'.format(video=self.video)
        if self.audio:
            self._cmd += u' -codec:a {audio}'.format(audio=self.audio)
        return self._cmd


class WriteTimecode(BaseCodecNode):
    type = 'timecode'

    def __init__(self, timecode=None, **kwargs):
        self.timecode = timecode
        super(WriteTimecode, self).__init__(**kwargs)

    def simple_cmd_string(self):
        self._cmd = u'-timecode {tc}'.format(tc=self.timecode)
        return self._cmd


class WriteReel(BaseCodecNode):
    type = 'metadata'

    def __init__(self, reel=None, **kwargs):
        self.reel = reel
        super(WriteReel, self).__init__(**kwargs)

    def simple_cmd_string(self):
        self._cmd = u'-metadata:s:v:0 reel_name={reel}'.format(reel=self.reel)
        return self._cmd


class Quality(BaseCodecNode):
    _name = 'qscale'

    def __init__(self, qscale=2, **kwargs):
        self.qscale = qscale
        super(Quality, self).__init__(**kwargs)

    def simple_cmd_string(self):
        self._cmd = u'-qscale:v {qscale}'.format(qscale=self.qscale) if self.qscale else u''
        return self._cmd


class PixelFormat(BaseCodecNode):
    type = 'pix_fmt'

    def __init__(self, pixel_format='yuv422p10le', profile=2, **kwargs):
        self.pixel_format = pixel_format
        self.profile = profile
        super(PixelFormat, self).__init__(**kwargs)

    def simple_cmd_string(self):
        self._cmd = u'{pix}{profile}'.format(
                pix='-pix_fmt {}'.format(self.pixel_format) if self.pixel_format else '',
                profile=' -profile:v {}'.format(self.profile) if self.profile else '')
        return self._cmd
