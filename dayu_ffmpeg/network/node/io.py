#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from base import BaseNode
from dayu_ffmpeg.config import SINGLE_MEDIA_FORMAT

class BaseIONode(BaseNode):
    type = 'base_io_node'

    def simple_cmd_string(self):
        return self.type

    def complex_cmd_string(self):
        return self.simple_cmd_string()

class Input(BaseIONode):
    type = 'input'
    max_input_num = 0

    def __init__(self, filename='', start=None, trim_in_frame=None, trim_out_frame=None, fps=None, **kwargs):
        self.filename = filename
        self.start = start
        self.trim_in_frame = trim_in_frame
        self.trim_out_frame = trim_out_frame
        self.fps = fps
        self.sequence = False if filename.endswith(SINGLE_MEDIA_FORMAT) else True
        super(Input, self).__init__(**kwargs)




class Output(BaseIONode):
    type = 'output'
    max_output_num = 0

    def __init__(self, filename='', fps=24, start=1001, sequence=False, duration=None, **kwargs):
        self.filename = filename
        self.fps = fps
        self.start = start
        self.sequence = sequence
        self.duration = duration
        super(Output, self).__init__(**kwargs)


if __name__ == '__main__':
    a = Input(name='hello')
    print a.__dict__
    print a.name
    print a.filename