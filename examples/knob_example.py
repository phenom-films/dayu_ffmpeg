#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'
__doc__ = """
通过定义network，可以实现复杂的网络转码结构（模板）。
但是有网络内的节点参数有很多只有在运行的时候才能够知道，或者是需要用户根据需要进行二次设置。
这种情况下，仅仅靠network 就无法实现要求了。

因此，我们通过使用knob，将network 内部的某些node 中参数提取到network 上，
这样就为用户提供了不改变转码结构，而仅仅改变一些参数的可能性。

下面的例子就是，将固定的Input 节点的filename 属性通过knob 提取到Root node 上
这样，用户就可以自行修改所使用水印图片的路径。
"""

from dayu_ffmpeg import *


class TranscodeTemplate(RootNode):
    def prepare(self):
        ih1 = self.create_node(InputHolder)
        i2 = self.create_node(Input('some_logo.png'))

        cf = self.create_node(ComplexFilterGroup)
        ih2 = cf.create_node(InputHolder)
        ih3 = cf.create_node(InputHolder)
        cf.set_input(ih1, 0)
        cf.set_input(i2, 1)
        over = cf.create_node(Overlay)
        over.set_input(ih2, 0)
        over.set_input(ih3, 1)
        fit = cf.create_node(Fit())
        fit.set_input(over)
        oh1 = cf.create_node(OutputHolder)
        oh1.set_input(fit)

        oh2 = self.create_node(OutputHolder)
        oh2.set_input(cf)

        # 添加knob，提取i2 这个Input Node 的filename 属性
        self.add_knob(BaseKnob(name='logo_file_name', link=i2, attribute='filename'))


if __name__ == '__main__':
    template_root = TranscodeTemplate(name='overlay logo, then fit in HD, finally export to mov')

    input1 = Input('some_input_file.mov')
    output1 = Output('some_output_file.mov')

    network_mode_cmd = template_root(input_list=[input1], output_list=[output1])
    # 通过 knob 修改属性
    network_mode_cmd.knobs.get('logo_file_name').value = 'new_logo.png'
    # 水印图片的路径变成了 new_logo.png
    print network_mode_cmd.cmd()


