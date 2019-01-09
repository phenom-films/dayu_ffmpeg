#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from base import BaseNode
from dayu_ffmpeg.config import GLOBAL_ORDER_SCORE


class BaseGlobalNode(BaseNode):
    type = 'base_global_node'
    order_score = GLOBAL_ORDER_SCORE

    def simple_cmd_string(self):
        return self._cmd

    def complex_cmd_string(self):
        return self.simple_cmd_string()


class FFMPEG(BaseGlobalNode):
    type = 'ffmpeg'
    max_input_num = 0

    def __init__(self, exec_path=None, **kwargs):
        from dayu_ffmpeg.config import FFMPEG_EXEC
        import sys
        self.exec_path = exec_path if exec_path else FFMPEG_EXEC[sys.platform]
        super(FFMPEG, self).__init__(**kwargs)

    def simple_cmd_string(self):
        self._cmd = self.exec_path
        return super(FFMPEG, self).simple_cmd_string()


class Overwrite(BaseGlobalNode):
    type = 'overwrite'

    def __init__(self, overwrite=True, **kwargs):
        self.overwrite = overwrite
        super(Overwrite, self).__init__(**kwargs)

    def simple_cmd_string(self):
        self._cmd = u'-y' if self.overwrite else u'-n'
        return super(Overwrite, self).simple_cmd_string()
