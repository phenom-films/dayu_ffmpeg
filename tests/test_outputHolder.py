#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import pytest
from dayu_ffmpeg.network import *


class TestOutputHolder(object):
    def test_out_edges(self):
        a = BaseNode()
        g = Group()

        assert g.max_output_num == 0
        assert a.set_input(g) is None
        assert a.in_edges == [None]
        assert g.out_edges == []

        oa = g.create_node(OutputHolder)
        assert g.max_output_num == 1
        assert g.out_edges == [[]]

        e = a.set_input(g)
        assert oa.out_edges == [[e]]
        assert g.out_edges == [[e]]
        assert a.input(0) == g

    def test_delete(self):
        a = BaseNode()
        b = BaseNode()
        g = Group()

        oa = g.create_node(OutputHolder)
        e = a.set_input(g)
        ob = g.create_node(OutputHolder)
        e2 = b.set_input(g, output_index=1)

        assert g.max_output_num == 2
        assert e.output_group_index == 0
        assert e2.output_group_index == 1
        assert g.out_edges == [[e], [e2]]

        oa.delete()
        assert g.max_output_num == 1
        assert e.output_group_index == None
        assert e2.output_group_index == 0
        assert g.out_edges == [[e2]]
        assert ob.link_num == 0
        assert a.in_edges == [None]
        assert b.in_edges == [e2]
