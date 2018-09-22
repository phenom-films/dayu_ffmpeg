#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from unittest import TestCase

from dayu_ffmpeg.stream import *


class TestScale(TestCase):
    def test___init__(self):
        self.assertRaises(DayuFFmpegValueError, Scale)
        self.assertIsNotNone(Scale(width=100))
        self.assertIsNotNone(Scale(height=50))
        self.assertIsNotNone(Scale(scale_x=0.5))
        self.assertIsNotNone(Scale(scale_y=0.5))
        self.assertIsNotNone(Scale(width=1920, height=1080))
        self.assertIsNotNone(Scale(scale_x=0.5, scale_y=0.7))
        self.assertIsNotNone(Scale(width=1920, height=1080, scale_x=0.5, scale_y=0.7))

    def test___str__(self):
        scale = Scale(width=1920)
        self.assertEqual(scale.__str__(), 'scale=w=1920:h=-1')
        scale = Scale(height=1080)
        self.assertEqual(scale.__str__(), 'scale=w=-1:h=1080')
        scale = Scale(width=1920, height=1080)
        self.assertEqual(scale.__str__(), 'scale=w=1920:h=1080')
        scale = Scale(scale_x=0.5)
        self.assertEqual(scale.__str__(), 'scale=w=iw*0.5:h=ih*0.5')
        scale = Scale(scale_y=2.0)
        self.assertEqual(scale.__str__(), 'scale=w=iw*2.0:h=ih*2.0')
        scale = Scale(scale_x=0.5, scale_y=0.7)
        self.assertEqual(scale.__str__(), 'scale=w=iw*0.5:h=ih*0.7')
        scale = Scale(width=1920, height=1080, scale_x=0.5, scale_y=0.7)
        self.assertEqual(scale.__str__(), 'scale=w=1920:h=1080')
        scale = Scale(width=1920, height=1080, scale_x=0.5, scale_y=0.7, in_color_matrix='bt709')
        self.assertEqual(scale.__str__(), 'scale=w=1920:h=1080:in_color_matrix=bt709')
        scale = Scale(scale_x=0.5, scale_y=0.7, in_color_matrix='bt709')
        self.assertEqual(scale.__str__(), 'scale=w=iw*0.5:h=ih*0.7:in_color_matrix=bt709')
