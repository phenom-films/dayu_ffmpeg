#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'


from dayu_ffmpeg.network import *

if __name__ == '__main__':
    g = BaseGroupNode()
    a = g.create_node(BaseNode)
    b = g.create_node(BaseNode)
    a.set_input(b)

    print a.connected_inputs, b.connected_outputs
    a.set_input(None)
    print a.connected_inputs, b.connected_outputs
    print a.parent, b.parent
    print a in g
    print a in b