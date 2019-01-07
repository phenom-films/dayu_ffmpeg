#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

__doc__ = """
这个文件是用来说明最简单的 ad-hoc 模式
在ad-hoc 模式下，用户不需要创建任何network，只需要将操作以线性的方式连接在一起即可。

但是ad-hoc 也有一些限制：
    * 只能实现串行的操作
    * 只能有一个Input 和一个Output，并且中间所有的node 都只能拥有一个input 和一个output
    * 不能使用Holder 类型的node
    * 通过ad-hoc 模式创建的指令，不能保存为ffscript
"""

from dayu_ffmpeg import *


def simple_ad_hoc_cmd():
    input_files = 'some_input_file.mov'
    output_files = 'output_file.mov'

    ad_hoc_cmd = Input(input_files) >> Scale(1920, 1080) >> DrawMask(2.39) >> Codec() >> Output(output_files)
    print ad_hoc_cmd.cmd()


if __name__ == '__main__':
    simple_ad_hoc_cmd()
