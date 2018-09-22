#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from unittest import TestCase

from dayu_ffmpeg.stream import *


class TestFFmpeg(TestCase):
    def test___init__(self):
        self.assertIsNotNone(FFmpeg())
        self.assertIsNotNone(FFmpeg('ffmpeg'))
        self.assertIsNotNone(FFmpeg('ffmpeg'))
        self.assertRaises(DayuFFmpegValueError, FFmpeg, [])
        self.assertRaises(DayuFFmpegValueError, FFmpeg, (1, 2, 3))
        self.assertRaises(DayuFFmpegValueError, FFmpeg, {1: 1})
        self.assertRaises(DayuFFmpegValueError, FFmpeg, FFmpeg())


    def test___str__(self):
        self.assertEqual(FFmpeg().__str__(), FFMPEG_EXEC[sys.platform].join(['\"', '\"']))
        self.assertEqual(FFmpeg('some/ffmpeg').__str__(), '\"some/ffmpeg\"')


