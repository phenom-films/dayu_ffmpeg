#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from unittest import TestCase

from dayu_ffmpeg.stream import *


class TestInput(TestCase):
    def test___init__(self):
        input = Input('/some/input/file.mov')
        self.assertEqual(input.filename, '/some/input/file.mov')
        self.assertEqual(input.start, None)
        self.assertEqual(input.trim_in, None)
        self.assertEqual(input.trim_out, None)
        self.assertEqual(input.fps, None)
        self.assertEqual(input.sequence, False)
        input = Input(u'某些中文 和的 tv.mp4', start=1001, trim_in_frame=10,
                      trim_out_frame=40, fps=24.0)
        self.assertEqual(input.filename, u'某些中文 和的 tv.mp4')
        self.assertEqual(input.start, 1001)
        self.assertEqual(input.trim_in, 10)
        self.assertEqual(input.trim_out, 40)
        self.assertEqual(input.fps, 24.0)
        self.assertEqual(input.sequence, False)

    def test__str__(self):
        input = Input('/some/input/file.mov')
        self.assertEqual(input.__str__(), '-i \"/some/input/file.mov\"')
        input = Input('/some/input/file.mov', start=1001)
        self.assertEqual(input.__str__(), '-i \"/some/input/file.mov\"')
        input = Input('/some/input/file.mov', trim_in_frame=24)
        self.assertEqual(input.__str__(), '-ss 1.00 -i \"/some/input/file.mov\"')
        input = Input('/some/input/file.mov', trim_out_frame=24)
        self.assertEqual(input.trim_out, 24)
        self.assertEqual(input.__str__(), '-i \"/some/input/file.mov\"')
        input = Input('/some/input/file.mov', fps=25.0)
        self.assertEqual(input.__str__(), '-r 25.0 -i \"/some/input/file.mov\"')
        input = Input('/some/input/file.mov', trim_in_frame=12, trim_out_frame=24, fps=24.0)
        self.assertEqual(input.__str__(), '-r 24.0 -ss 0.50 -i \"/some/input/file.mov\"')

        input = Input('/some/input/seq.%04d.exr', start=1001)
        self.assertEqual(input.__str__(), '-start_number 1001 -f image2 -i \"/some/input/seq.%04d.exr\"')
        input = Input('/some/input/seq.%04d.exr', trim_in_frame=24)
        self.assertEqual(input.__str__(), '-f image2 -ss 1.00 -i \"/some/input/seq.%04d.exr\"')
        input = Input('/some/input/seq.%04d.exr', trim_out_frame=40)
        self.assertEqual(input.__str__(), '-f image2 -i \"/some/input/seq.%04d.exr\"')
        input = Input('/some/input/seq.%04d.exr', fps=25)
        self.assertEqual(input.__str__(), '-f image2 -r 25 -i \"/some/input/seq.%04d.exr\"')
        input = Input('/some/input/seq.%04d.exr', start=1001, trim_in_frame=24, trim_out_frame=40, fps=25)
        self.assertEqual(input.__str__(), '-start_number 1001 -f image2 -r 25 -ss 0.96 -i \"/some/input/seq.%04d.exr\"')
        input = Input('/some/input/single_image.exr')
        self.assertEqual(input.__str__(), '-f image2 -i \"/some/input/single_image.exr\"')

        input = Input(u'/中文/路径 keng/测试 123.mov')
        self.assertEqual(input.__str__(), u'-i \"/中文/路径 keng/测试 123.mov\"')
        input = Input(r'p:\windows\path\test.jpg')
        self.assertEqual(input.__str__(), '-f image2 -i \"p:\\windows\\path\\test.jpg\"')
