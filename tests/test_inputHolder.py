#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import pytest
from dayu_ffmpeg.network import *


class TestInputHolder(object):
    def test_in_edges(self):
        pass

    def test_delete(self):
        g = Group()
        a = BaseNode()
        b = BaseNode()
        ia = g.create_node(InputHolder)
        ib = g.create_node(InputHolder)

        e = g.set_input(a)
        assert len(g.in_edges) == 2
        assert ia.in_edges == [e]
        assert ib.in_edges == [None]
        assert ia.input(0) == a

        e2 = g.set_input(b, 1)
        assert len(g.in_edges) == 2
        assert ia.in_edges == [e]
        assert ib.in_edges == [e2]
        assert ia.input(0) == a and ib.input(0) == b

        g.set_input(None, 0)
        assert ia.in_edges == [None]
        assert ia.link_num == 0

        ia.delete()
        assert ia not in g.inside_nodes
        assert g.max_input_num == 1 and len(g.in_edges) == 1
        assert ib.in_edges == [e2]
        assert ib.link_num == 0
        assert ib.input(0) == b
        assert a.out_edges == [[]]

        ib.delete()
        assert g.max_input_num == 0 and len(g.in_edges) == 0
        assert ib not in g.inside_nodes

if __name__ == '__main__':
    TestInputHolder().test_delete()
