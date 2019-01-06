#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import pytest
from dayu_ffmpeg.network import *

class TestAdHoc(object):
    def prepare_adhec(self):
        result = Input() >> Scale() >> Output()
        return result

    def test_cmd(self):
        result = self.prepare_adhec()
        print result.cmd()