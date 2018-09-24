# !/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from dayu_ffmpeg.stream import *


def test___str__():
    assert Overwrite().overwrite == True
    assert Overwrite(True).overwrite == True
    assert Overwrite(False).overwrite == False
    assert Overwrite(None).overwrite == None
    assert Overwrite().__str__() == u'-y'
    assert Overwrite('yes').__str__() == u'-y'
    assert Overwrite(1).__str__() == u'-y'
    assert Overwrite(False).__str__() == u'-n'
    assert Overwrite(None).__str__() == u'-n'
    assert Overwrite(0).__str__() == u'-n'
