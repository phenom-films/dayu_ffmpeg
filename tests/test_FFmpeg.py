#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import pytest
from dayu_ffmpeg.stream import *


def test___init__():
    assert FFmpeg() is not None
    assert FFmpeg('ffmpeg') is not None
    assert FFmpeg('ffmpeg') is not None
    pytest.raises(DayuFFmpegValueError, FFmpeg, [])
    pytest.raises(DayuFFmpegValueError, FFmpeg, (1, 2, 3))
    pytest.raises(DayuFFmpegValueError, FFmpeg, {1: 1})
    pytest.raises(DayuFFmpegValueError, FFmpeg, FFmpeg())

    assert FFmpeg().__str__() == FFMPEG_EXEC[sys.platform].join(['\"', '\"'])
    assert FFmpeg('some/ffmpeg').__str__() == '\"some/ffmpeg\"'
    assert FFmpeg(u'中文').__str__() == u'\"中文\"'
