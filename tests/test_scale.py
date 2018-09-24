#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import pytest
from dayu_ffmpeg.stream import *


def test___init__():
    pytest.raises(DayuFFmpegValueError, Scale)
    assert Scale(width=100) is not None
    assert Scale(height=50) is not None
    assert Scale(scale_x=0.5) is not None
    assert Scale(scale_y=0.5) is not None
    assert Scale(width=1920, height=1080) is not None
    assert Scale(scale_x=0.5, scale_y=0.7) is not None
    assert Scale(width=1920, height=1080, scale_x=0.5, scale_y=0.7) is not None


def test___str__():
    scale = Scale(width=1920)
    assert scale.__str__() == 'scale=w=1920:h=-1'
    scale = Scale(height=1080)
    assert scale.__str__() == 'scale=w=-1:h=1080'
    scale = Scale(width=1920, height=1080)
    assert scale.__str__() == 'scale=w=1920:h=1080'
    scale = Scale(scale_x=0.5)
    assert scale.__str__() == 'scale=w=iw*0.5:h=ih*0.5'
    scale = Scale(scale_y=2.0)
    assert scale.__str__() == 'scale=w=iw*2.0:h=ih*2.0'
    scale = Scale(scale_x=0.5, scale_y=0.7)
    assert scale.__str__() == 'scale=w=iw*0.5:h=ih*0.7'
    scale = Scale(width=1920, height=1080, scale_x=0.5, scale_y=0.7)
    assert scale.__str__() == 'scale=w=1920:h=1080'
    scale = Scale(width=1920, height=1080, scale_x=0.5, scale_y=0.7, in_color_matrix='bt709')
    assert scale.__str__() == 'scale=w=1920:h=1080:in_color_matrix=bt709'
    scale = Scale(scale_x=0.5, scale_y=0.7, in_color_matrix='bt709')
    assert scale.__str__() == 'scale=w=iw*0.5:h=ih*0.7:in_color_matrix=bt709'
