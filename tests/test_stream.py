#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import pytest
import os
from dayu_ffmpeg.stream import *


def test_mov_stream():
    input_mov = os.sep.join((os.path.dirname(__file__), 'footage', 'media', '10s.mov'))
    output_mov = os.sep.join((os.path.dirname(__file__), 'footage', 'media', 'output.mov'))
    command = FFmpeg() >> Overwrite() >> \
              Input(input_mov) >> DrawMask(2.39) >> Scale(width=1280, height=720) >> \
              DrawTimecode() >> DrawDate() >> DrawFrames() >> \
              Codec() >> Output(output_mov)
    for x in command.run():
        print x

    assert os.path.exists(output_mov)
    os.remove(output_mov)


def test_seq_stream():
    input_mov = os.sep.join((os.path.dirname(__file__), 'footage', 'seq', 'transcode_%04d.jpg'))
    output_mov = os.sep.join((os.path.dirname(__file__), 'footage', 'media', 'output.mov'))
    command = FFmpeg() >> Overwrite() >> \
              Input(input_mov, start=1) >> DrawMask(2.39) >> Scale(width=1280, height=720) >> \
              DrawTimecode() >> DrawDate() >> DrawFrames() >> \
              Codec() >> Output(output_mov)
    for x in command.run():
        print x

    assert os.path.exists(output_mov)
    os.remove(output_mov)
