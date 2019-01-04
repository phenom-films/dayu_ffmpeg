#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from unittest import TestCase

__author__ = 'andyguo'

import pytest
from dayu_ffmpeg.network.edge.base import TwoEndPoints



class TestTwoEndPoints(object):
    def test___setattr__(self):
        a = TwoEndPoints()
        assert a.left is None and a.right is None
        a = TwoEndPoints(1, 2)
        assert a.left == 1 and a.right == 2
        with pytest.raises(AttributeError) as error:
            a.left = 4
        assert error.type == AttributeError
        with pytest.raises(AttributeError) as error:
            a.right = None
        assert error.type == AttributeError
        with pytest.raises(KeyError) as error:
            setattr(a, 'hello', 1)
        assert error.type == KeyError
