#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from base import BaseNode


class BaseFilterNode(BaseNode):
    type = 'base_filter_node'

    def __init__(self, *args, **kwargs):
        self.stream_in_num = []
        self.stream_out_num = None
        super(BaseFilterNode, self).__init__(*args, **kwargs)

    def simple_cmd_string(self):
        return self.type

    def complex_cmd_string(self):
        return '{stream_in}{cmd}{stream_out}'.format(
                stream_in=''.join(['[{}]'.format(x) for x in self.stream_in_num]),
                cmd=self.simple_cmd_string(),
                stream_out='[{}]'.format(self.stream_out_num))


class Scale(BaseFilterNode):
    type = 'scale'

    def __init__(self, width=1920, height=1080, relative_scale=False, **kwargs):
        self.width = width
        self.height = height
        self.relative_scale = relative_scale
        super(Scale, self).__init__(**kwargs)

    def simple_cmd_string(self):
        if self.relative_scale:
            self._cmd = u'scale=w=iw*{scale_x}:h=ih*{scale_y}'.format(scale_x=self.width,
                                                                      scale_y=self.height)
            return self._cmd
        else:
            self._cmd = u'scale=w={width}:h=i{height}'.format(width=self.width,
                                                              height=self.height)
            return self._cmd


class Overlay(BaseFilterNode):
    type = 'overlay'
    max_input_num = 2

    def __init__(self, x=0, y=0, **kwargs):
        self.x = x
        self.y = y
        super(Overlay, self).__init__(**kwargs)

    def simple_cmd_string(self):
        self._cmd = u'overlay=x={x}:y={y}'.format(x=self.x, y=self.y)
        return self._cmd
