#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

__doc__ = """
这个文件用来说明如何通过network 的模式，创建复杂的ffmpeg 指令。
这里的network 模式对应的就是ffmpeg 中的complex filter 模式，
可以把network 想象为一个黑盒，外界可以按照顺序输入多个input，并同时输出多个output。
 _________
|         |
| input 0 |\                    __________
|_________| \                  |          |
             \   _________    /| output 0 |
              \ |         |  / |__________|
 _________     \|         | /
|         |     |         |/
| input 1 |---->| network |\
|_________|     |         | \   __________
               /|         |  \ |          |
              / |         |   \| output 1 |
 _________   /  |_________|    |__________|
|         | /
| input 2 |/
|_________|

核心的处理如下：
    * 只能创建一个Root node（对应就是整个处理的模板）
    * 需要几个input、output，就在root 下创建相应数量的 InputHolder 和 OutputHolder
    * 用户最终只需要按顺序传入对应的 Input list 和 Output list 即可
    
使用network 模式虽然相对复杂，但是有很多好处：
    * 可以实现转码的模板，用户只要调用即可
    * 整个Root 可以保存为ffscript，方便之后调用（或者使用其他语言编写解析器）
    * 支持多个input 和output，这样就可以使用类似Overlay 这样的节点

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


if __name__ == '__main__':
    template_root = TranscodeTemplate(name='overlay logo, then fit in HD, finally export to mov')

    input1 = Input('some_input_file.mov')
    output1 = Output('some_output_file.mov')

    network_mode_cmd = template_root(input_list=[input1], output_list=[output1])
    print network_mode_cmd.cmd()
