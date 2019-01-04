#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import pytest
from dayu_ffmpeg.network.node.base import BaseNode
from dayu_ffmpeg.network.node.group import Group


class TestBaseNode(object):
    def test_check_allow_connect(self):
        a = BaseNode()
        b = BaseNode()
        assert a.check_allow_connect(b, 0, 0)
        assert a.check_allow_connect(b, 1, 0) is False
        assert a.check_allow_connect(None, 0, 0)
        assert a.check_allow_connect(None, 1, 0) is False
        assert a.check_allow_connect(a, 0, 0) is False
        assert a.check_allow_connect(b, -1, 0)
        assert a.check_allow_connect(b, -2, 0) is False
        a.parent = 1
        assert a.check_allow_connect(b, 0, 0) is False

        a.set_input(b)
        assert a.check_allow_connect(b, 0, 0) is False

    def test_set_input(self):
        g = Group()
        a = g.create_node(BaseNode)
        b = g.create_node(BaseNode)

        e = a.set_input(b)
        assert e is not None and e.endpoints.left is b and e.endpoints.right is a
        assert b in a.connected_inputs() and a in b.connected_outputs()
        assert a.set_input(b) is None
        assert a in g.inside_nodes and b in g.inside_nodes
        assert e in g.inside_edges

        c = g.create_node(BaseNode)
        new_e = a.set_input(c)
        assert c in a.connected_inputs() and b not in a.connected_outputs()
        assert b.out_edges[0] == []
        assert a in c.connected_outputs()
        assert e.endpoints.left is None and e.endpoints.right is None
        assert a in g.inside_nodes and b in g.inside_nodes and c in g.inside_nodes
        assert e not in g.in_edges and new_e in g.inside_edges

        assert a.set_input(None) is None
        assert a.in_edges == [None]
        assert c.out_edges[0] == []
        assert new_e.endpoints.left is None and new_e.endpoints.right is None
        assert a in g.inside_nodes and b in g.inside_nodes and c in g.inside_nodes
        assert new_e not in g.inside_edges

    def test_delete(self):
        g = Group()
        a = g.create_node(BaseNode)
        b = g.create_node(BaseNode)
        c = g.create_node(BaseNode)
        e1 = b.set_input(a)
        e2 = c.set_input(b)

        b.delete()
        assert a in g.inside_nodes and c in g.inside_nodes and b not in g.inside_nodes
        assert g.inside_edges == []
        assert a.out_edges == [[]]
        assert c.in_edges == [None]
        assert e1.endpoints.left is None and e1.endpoints.right is None
        assert e2.endpoints.left is None and e2.endpoints.right is None

    def test_input(self):
        g = Group()
        a = g.create_node(BaseNode)
        b = g.create_node(BaseNode)
        c = g.create_node(BaseNode)
        e1 = b.set_input(a)
        e2 = c.set_input(b)

        assert a.input(0) is None
        assert b.input(0) is a
        assert c.input(0) is b
        assert a.input(1) is None

        d = BaseNode()
        d.max_input_num = 0
        assert d.input(0) is None

    def test_connected_inputs(self):
        g = Group()
        a = g.create_node(BaseNode)
        b = g.create_node(BaseNode)
        c = g.create_node(BaseNode)
        e1 = b.set_input(a)
        e2 = c.set_input(b)

        assert a.connected_inputs() == []
        assert b.connected_inputs() == [a]
        assert c.connected_inputs() == [b]

    def test_connected_outputs(self):
        g = Group()
        a = g.create_node(BaseNode)
        b = g.create_node(BaseNode)
        c = g.create_node(BaseNode)
        e1 = b.set_input(a)
        e2 = c.set_input(a)

        assert a.connected_outputs() == [b, c]
        assert b.connected_outputs() == []
        assert c.connected_outputs() == []

        b.set_input(None)
        assert a.connected_outputs() == [c]
