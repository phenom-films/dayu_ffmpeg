#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'
__doc__ = """
ffmpeg 拥有非常多的filter 指令，而dayu_ffmpeg 这个库不可能完全覆盖所有的指令。
因此，用户可以自行扩展，从而支持更多的指令，甚至是实现一些特定的指令。

这个示例文件会展示两种扩展指令的方式：
    * 直接使用 GenericUnaryFilterNode
    * 继承class，然后实现需要的方法

"""

from dayu_ffmpeg import *


# 方法一，直接使用GenericUnaryFilterNode
def use_generic_unary_filter_node():
    # 假设希望使用ffmpeg 中 drawgrid 这个filter
    # 那么通过查看ffmpeg 的document，可以知道我们希望需要的参数有 x, y, w, h 这几个
    command = Input('/some/input/file.mov') >> \
              GeneralUnaryFilter('drawgrid', x=0, y=0, w=100, h=50) >> \
              Output('/custom/filter/output.mov')
    print command.cmd()


# 方法二，继承BaseFilterNode class，然后自行实现需要的方法
class DrawGrid(BaseFilterNode):
    # class type 必须是唯一的
    type = 'drawgrid'

    # init 中，务必通过kwargs 的形式给出需要的参数，所有的参数都需要有默认值
    def __init__(self, x=0, y=0, w=0, h=0, **kwargs):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        super(DrawGrid, self).__init__(**kwargs)

    # 如果这个node 支持ad-hoc 模式，那么就需要实现simple_cmd_string() 这个方法
    def simple_cmd_string(self):
        self._cmd = u'drawgrid=x={x}:y={y}:w={w}:h={h}'.format(x=self.x, y=self.y, w=self.w, h=self.h)
        return self._cmd

    # 如果这个节点需要支持network 模式，那么需要实现 complex_cmd_string() 这个方法
    def complex_cmd_string(self):
        super(DrawGrid, self).complex_cmd_string()
