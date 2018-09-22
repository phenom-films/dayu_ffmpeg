#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from unittest import TestCase

from dayu_ffmpeg.stream import *


class TestInput(TestCase):
    def test___str__(self):
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
