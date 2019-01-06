#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import pytest
import os
from dayu_ffmpeg.network import *
from dayu_ffmpeg.ffscript import *


class Test_ffscript(object):
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
        self.root.add_knob(BaseKnob(link=self.i2, attribute='filename'))

    def test_save_script(self):
        self.prepare_network()
        path = os.sep.join((os.path.dirname(__file__), 'ffscript.txt'))
        try:
            save_script(self.root, path)
        except Exception as e:
            print e
            pytest.fail()

    def test_open_script(self):
        self.test_save_script()
        path = os.sep.join((os.path.dirname(__file__), 'ffscript.txt'))
        try:
            root = open_script(path)
            root.set_input(self.i1)
            root.cmd()
        except Exception as e:
            print e
            pytest.fail()
