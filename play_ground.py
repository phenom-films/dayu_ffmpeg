#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from dayu_ffmpeg.network import *
from dayu_ffmpeg.ffscript import *

if __name__ == '__main__':
    from dayu_ffmpeg.network import *

    i1 = Input('/Users/andyguo/Documents/github/dayu_ffmpeg/tests/footage/seq/transcode_%04d.jpg', start=1)
    root = RootNode()
    ih1 = root.create_node(InputHolder)
    root.set_input(i1)
    i2 = root.create_node(Input('logo'))
    cf = root.create_node(ComplexFilterGroup)
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
    o1 = root.create_node(Output('/Users/andyguo/Documents/github/dayu_ffmpeg/tests/footage/media/output.mov'))
    o1.set_input(cf)

    knob = root.add_knob(BaseKnob(link=i2, attribute='filename'))
    print knob.value
    knob.value = '/Users/andyguo/Desktop/Screen Shot 2019-01-07 at 10.30.05 PM.png'

    from pprint import pprint

    print root.cmd()
    # print fit.stream_in_num, fit.stream_out_num
    # print o1.in_edges[0].endpoints.left
    # print o1, o1.stream_in_num, o1.stream_out_num
    # for n in o1.traverse_inputs():
    #     print n, n.stream_in_num, n.stream_out_num

    pprint(root.to_script())
    save_script(root, '/Users/andyguo/Desktop/basic.txt')
    #
    # # pprint(ALL_SUBCLASSES)
    root2 = open_script('/Users/andyguo/Desktop/basic.txt')
    root2.set_input(i1)
    # print root2.knobs[0].parent
    # print root2.knobs[0].link
    # root2.knobs[0].value = 'another_logo'
    # pprint(root.__dict__)
    print root2.cmd()
