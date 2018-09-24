#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import pytest
from dayu_ffmpeg.stream import *


def test___str__():
    drawbox = DrawBox()
    assert drawbox.__str__() == 'drawbox=x=iw/4:y=ih/4:w=iw/2:h=ih/2:c=Black@0.7:t=fill'
    drawbox = DrawBox(replace=1)
    assert drawbox.__str__() == 'drawbox=x=iw/4:y=ih/4:w=iw/2:h=ih/2:c=Black@0.7:t=fill:replace=1'
