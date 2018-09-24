#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from dayu_ffmpeg.stream import *


def test___init__():
    overlay = Overlay(Input('/some/overlay/logo.mov'))
    assert overlay.x == 0
    assert overlay.y == 0


def test___str__():
    overlay = Overlay(Input('/some/overlay/logo.mov'))
    assert overlay.__str__() == 'overlay=x=0:y=0'
