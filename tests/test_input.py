#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from dayu_ffmpeg.stream import *


def test___init__():
    input = Input('/some/input/file.mov')
    assert input.filename == '/some/input/file.mov'
    assert input.start == None
    assert input.trim_in == None
    assert input.trim_out == None
    assert input.fps == None
    assert input.sequence == False
    input = Input(u'某些中文 和的 tv.mp4', start=1001, trim_in_frame=10,
                  trim_out_frame=40, fps=24.0)
    assert input.filename == u'某些中文 和的 tv.mp4'
    assert input.start == 1001
    assert input.trim_in == 10
    assert input.trim_out == 40
    assert input.fps == 24.0
    assert input.sequence == False


def test__str__():
    input = Input('/some/input/file.mov')
    assert input.__str__() == '-i \"/some/input/file.mov\"'
    input = Input('/some/input/file.mov', start=1001)
    assert input.__str__() == '-i \"/some/input/file.mov\"'
    input = Input('/some/input/file.mov', trim_in_frame=24)
    assert input.__str__() == '-ss 1.00 -i \"/some/input/file.mov\"'
    input = Input('/some/input/file.mov', trim_out_frame=24)
    assert input.trim_out == 24
    assert input.__str__() == '-i \"/some/input/file.mov\"'
    input = Input('/some/input/file.mov', fps=25.0)
    assert input.__str__() == '-r 25.0 -i \"/some/input/file.mov\"'
    input = Input('/some/input/file.mov', trim_in_frame=12, trim_out_frame=24, fps=24.0)
    assert input.__str__() == '-r 24.0 -ss 0.50 -i \"/some/input/file.mov\"'

    input = Input('/some/input/seq.%04d.exr', start=1001)
    assert input.__str__() == '-start_number 1001 -f image2 -i \"/some/input/seq.%04d.exr\"'
    input = Input('/some/input/seq.%04d.exr', trim_in_frame=24)
    assert input.__str__() == '-f image2 -ss 1.00 -i \"/some/input/seq.%04d.exr\"'
    input = Input('/some/input/seq.%04d.exr', trim_out_frame=40)
    assert input.__str__() == '-f image2 -i \"/some/input/seq.%04d.exr\"'
    input = Input('/some/input/seq.%04d.exr', fps=25)
    assert input.__str__() == '-f image2 -r 25 -i \"/some/input/seq.%04d.exr\"'
    input = Input('/some/input/seq.%04d.exr', start=1001, trim_in_frame=24, trim_out_frame=40, fps=25)
    assert input.__str__() == '-start_number 1001 -f image2 -r 25 -ss 0.96 -i \"/some/input/seq.%04d.exr\"'
    input = Input('/some/input/single_image.exr')
    assert input.__str__() == '-f image2 -i \"/some/input/single_image.exr\"'

    input = Input(u'/中文/路径 keng/测试 123.mov')
    assert input.__str__() == u'-i \"/中文/路径 keng/测试 123.mov\"'
    input = Input(r'p:\windows\path\test.jpg')
    assert input.__str__() == '-f image2 -i \"p:\\windows\\path\\test.jpg\"'
