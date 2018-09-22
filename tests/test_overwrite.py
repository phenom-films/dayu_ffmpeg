# !/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from unittest import TestCase

from dayu_ffmpeg.stream import *


class TestOverwrite(TestCase):
    def test___str__(self):
        self.assertEqual(Overwrite().overwrite, True)
        self.assertEqual(Overwrite(True).overwrite, True)
        self.assertEqual(Overwrite(False).overwrite, False)
        self.assertEqual(Overwrite(None).overwrite, None)
        self.assertEqual(Overwrite().__str__(), u'-y')
        self.assertEqual(Overwrite('yes').__str__(), u'-y')
        self.assertEqual(Overwrite(1).__str__(), u'-y')
        self.assertEqual(Overwrite(False).__str__(), u'-n')
        self.assertEqual(Overwrite(None).__str__(), u'-n')
        self.assertEqual(Overwrite(0).__str__(), u'-n')
