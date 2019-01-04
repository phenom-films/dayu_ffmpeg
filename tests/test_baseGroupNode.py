#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import pytest
from dayu_ffmpeg.network import *


class TestBaseGroupNode(object):
    def test_refresh_inputholder(self):
        pass

    def test_refresh_outputholder(self):
        pass

    def test_outputholders(self):
        pass

    def test_inputholders(self):
        pass

    def test_create_node(self):
        g = BaseGroupNode()
        a = g.create_node(InputHolder)
        assert g.max_input_num == 1
        assert a in g.inside_nodes
        assert a.link_num == 0
        assert a.parent is g

        b = g.create_node(InputHolder)
        assert g.max_input_num == 2
        assert b in g.inside_nodes
        assert b.link_num == 1
        assert b.parent is g
