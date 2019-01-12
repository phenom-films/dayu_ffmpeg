#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'
__doc__ = """
大多数情况下，只要使用network 模式预先定义好网络结构，就可以满足绝大多数的转码需求。
有些时候，用户需要临时修改一些节点的参数，这就需要用到knob 的方式来提取某些参数。

但是，还有的时候网络结构都会因为用户的输入发生改变。这种情况就需要在代码中根据用户的输入
临时修改一部分网络结构，甚至是全部的结构。
这种情况称为"动态网络结构"

例如下面：
concat 指令是将多个input 连接成为一个完整的output。
我们的网络结构在用户确定input 数量之前是无法固定下来的。
这时候就可以在实例化网络的时候，让用户传入参数，然后根据这个参数来动态生成网络结构。
"""

from dayu_ffmpeg import *


class DynamicNetworkTemplate(RootNode):

    def __init__(self, input_num, **kwargs):
        self.input_num = input_num
        super(DynamicNetworkTemplate, self).__init__(**kwargs)

    def prepare(self):
        concat_list = []

        self.cf = self.create_node(ComplexFilterGroup())

        for i in range(self.input_num):
            i1 = self.create_node(InputHolder)
            ic1 = self.cf.create_node(InputHolder)
            self.cf.set_input(i1, i)
            scale = self.cf.create_node(Scale())
            scale.set_input(ic1)
            concat_list.append(scale)

        concat = self.cf.create_node(Concat(number_of_inputs=self.input_num))
        for i, node in enumerate(concat_list):
            concat.set_input(node, i)

        oc1 = self.cf.create_node(OutputHolder)
        oc1.set_input(concat)

        o2 = self.create_node(OutputHolder)
        o2.set_input(self.cf)


if __name__ == '__main__':
    input_list = [Input('aaa.mov'), Input('bbb.mob'), Input('ccc.mov')]
    output_list = [Output('ooo.mov')]

    nn = DynamicNetworkTemplate(len(input_list))
    result = nn(input_list=input_list, output_list=output_list)
    print result.cmd()
