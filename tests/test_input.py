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
