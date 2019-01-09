#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'
__doc__ = """
有时候，用户需要将一系列的操作打包成一个常用的操作。方便之后的使用，这时候就需要使用到packed filter。

这里的例子就是创建一个packed filter class，里面有scale 和pad 两个filter
两个fliter 联合使用，保证画面总是等比缩放，并放在1920x1080 的画幅中，露出的部分用黑色填充
"""

from dayu_ffmpeg import *


# 继承BasePackedFilterNode
class Fit(BasePackedFilterNode):
    # type 必须是唯一的
    type = 'fit'

    # init 中用kwargs 的方式给出需要的参数，并且必须有默认值
    def __init__(self, width=1920, height=1080, **kwargs):
        self.width = width
        self.height = height
        super(Fit, self).__init__(**kwargs)

    # 重载prepare 方法
    def prepare(self):
        # 总是先创建input holder、output holder 作为packed filter 的入口和出口
        i1 = self.create_node(InputHolder)
        o1 = self.create_node(OutputHolder)

        # 创建scale、Pad node
        scale_op = self.create_node(Scale(width=u'iw*min({0}/iw\\,{1}/ih)'.format(self.width, self.height),
                                          height=u'ih*min({0}/iw\\,{1}/ih)'.format(self.width, self.height)))
        pad_op = self.create_node(Pad(w=self.width,
                                      h=self.height,
                                      x=u'({0}-iw*min({0}/iw\\,{1}/ih))/2'.format(self.width, self.height),
                                      y=u'({1}-ih*min({0}/iw\\,{1}/ih))/2'.format(self.width, self.height)))
        # 开始连接
        o1.set_input(pad_op)
        pad_op.set_input(scale_op)
        scale_op.set_input(i1)
