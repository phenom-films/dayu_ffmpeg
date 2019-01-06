#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import pytest
from dayu_ffmpeg.network import *


class TestRootNode(object):
    def prepare_network(self):
        self.i1 = Input()
        self.root = RootNode()
        self.ih1 = self.root.create_node(InputHolder)
        self.root.set_input(self.i1)
        self.i2 = self.root.create_node(Input)
        self.cf = self.root.create_node(ComplexFilterGroup)
        self.ih2 = self.cf.create_node(InputHolder)
        self.ih3 = self.cf.create_node(InputHolder)
        self.cf.set_input(self.ih1, 0)
        self.cf.set_input(self.i2, 1)
        self.over = self.cf.create_node(Overlay)
        self.over.set_input(self.ih2, 0)
        self.over.set_input(self.ih3, 1)
        self.oh1 = self.cf.create_node(OutputHolder)
        self.oh1.set_input(self.over)
        self.o1 = self.root.create_node(Output)
        self.o1.set_input(self.cf)

    def test_cmd(self):
        from pprint import pprint
        self.prepare_network()
        # print self.root.cmd()
        pprint(self.root.to_script())

    def test__find_all_inputs(self):
        self.prepare_network()
        assert self.root._find_all_inputs(self.root._find_all_outputs()) == [self.i1, self.i2]

    def test__find_all_outputs(self):
        self.prepare_network()
        assert self.root._find_all_outputs() == [self.o1]
