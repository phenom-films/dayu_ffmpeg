#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import pytest
from dayu_ffmpeg.network import *


class TestBaseNode(object):
    def test__init__(self):
        a = BaseNode(name='haha')
        assert a.name == 'haha'

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

    def test_traverse_inputs(self):
        a = BaseNode()
        b = BaseNode()
        g = Group()
        ia1 = g.create_node(InputHolder)
        ib = g.create_node(BaseNode)
        ic = g.create_node(OutputHolder)
        c = BaseNode()

        c.set_input(g)
        ic.set_input(ib)
        ib.set_input(ia1)
        g.set_input(b)
        b.set_input(a)

        assert list(c.traverse_inputs()) == [ic, ib, ia1, b, a]
        assert list(c.traverse_inputs(False)) == [g, b, a]

    def test_travse_outputs(self):
        a = BaseNode(name='a')
        g1 = Group(name='g1')
        g2 = Group(name='g2')
        ia1 = g1.create_node(InputHolder, name='ia1')
        ib1 = g1.create_node(OutputHolder, name='ib1')
        ia2 = g2.create_node(InputHolder, name='ia2')
        ib2 = g2.create_node(OutputHolder, name='ib2')
        c = BaseNode(name='c')
        d = BaseNode(name='d')

        c.set_input(g1)
        ib1.set_input(ia1)
        g1.set_input(a)
        d.set_input(g2)
        ib2.set_input(ia2)
        g2.set_input(a)

        assert list(a.traverse_outputs()) == [ia1, ib1, c, ia2, ib2, d]
        assert list(a.traverse_outputs(False)) == [g1, c, g2, d]

    def test_hierarchy(self):
        root = RootNode()
        a = root.create_node(Group)
        b = a.create_node(Group)
        c = b.create_node(BaseNode)

        assert c.hierarchy() == [b, a, root]
        assert b.hierarchy() == [a, root]
        assert a.hierarchy() == [root]
        assert root.hierarchy() == []
