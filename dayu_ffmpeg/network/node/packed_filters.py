#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from group import Group
from filters import *
from holder import InputHolder, OutputHolder
from dayu_ffmpeg.config import FILTER_ORDER_SCORE


class BasePackedFilterNode(Group):
    type = 'base_packed_filter_node'
    order_score = FILTER_ORDER_SCORE

    def __init__(self, *args, **kwargs):
        super(BasePackedFilterNode, self).__init__(*args, **kwargs)
        self.prepare()

    def prepare(self):
        raise NotImplementedError()


class Fit(BasePackedFilterNode):
    type = 'fit'

    def __init__(self, width=1920, height=1080, **kwargs):
        self.width = width
        self.height = height
        super(Fit, self).__init__(**kwargs)

    def prepare(self):
        i1 = self.create_node(InputHolder)
        o1 = self.create_node(OutputHolder)
        scale_op = self.create_node(Scale(width=u'iw*min({0}/iw\\,{1}/ih)'.format(self.width, self.height),
                                          height=u'ih*min({0}/iw\\,{1}/ih)'.format(self.width, self.height)))
        pad_op = self.create_node(Pad(w=self.width,
                                      h=self.height,
                                      x=u'({0}-iw*min({0}/iw\\,{1}/ih))/2'.format(self.width, self.height),
                                      y=u'({1}-ih*min({0}/iw\\,{1}/ih))/2'.format(self.width, self.height)))
        o1.set_input(pad_op)
        pad_op.set_input(scale_op)
        scale_op.set_input(i1)
