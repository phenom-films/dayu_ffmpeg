#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from base import BaseNode
from dayu_ffmpeg.config import SINGLE_MEDIA_FORMAT, INPUT_ORDER_SCORE, OUTPUT_ORDER_SCORE


class BaseIONode(BaseNode):
    type = 'base_io_node'
    order_score = -1

    def simple_cmd_string(self):
        return self.type

    def complex_cmd_string(self):
        return self.simple_cmd_string()


class Input(BaseIONode):
    type = 'input'
    max_input_num = 0
    order_score = INPUT_ORDER_SCORE

    def __init__(self, filename='', start=None, trim_in_frame=None, trim_out_frame=None, fps=None, **kwargs):
        self.filename = filename
        self.start = start
        self.trim_in_frame = trim_in_frame
        self.trim_out_frame = trim_out_frame
        self.fps = fps
        self.sequence = False if filename.endswith(SINGLE_MEDIA_FORMAT) else True
        super(Input, self).__init__(**kwargs)

    def simple_cmd_string(self):
        if self.sequence:
            self._cmd = u'{start}-f image2 ' \
                        u'{fps}{trimin}' \
                        u'-i \"{filename}\"' \
                        u''.format(start='-start_number {} '.format(self.start) if self.start else '',
                                   fps='-r {} '.format(self.fps) if self.fps else '',
                                   trimin='-ss {:.02f} '.format(
                                           self.trim_in_frame / float(
                                                   self.fps if self.fps else 24.0)) if self.trim_out_frame else '',
                                   filename=self.filename)
        else:
            self._cmd = u'{fps}{trimin}' \
                        u'-i \"{filename}\"' \
                        u''.format(fps='-r {} '.format(self.fps) if self.fps else '',
                                   trimin='-ss {:.02f} '.format(
                                           self.trim_in_frame / float(
                                                   self.fps if self.fps else 24.0)) if self.trim_out_frame else '',
                                   filename=self.filename)
        return self._cmd


class Output(BaseIONode):
    type = 'output'
    max_output_num = 0
    order_score = OUTPUT_ORDER_SCORE

    def __init__(self, filename='', fps=24, start=1001, sequence=False, duration=None, **kwargs):
        self.filename = filename
        self.fps = fps
        self.start = start
        self.sequence = sequence
        self.duration = duration
        super(Output, self).__init__(**kwargs)

    def simple_cmd_string(self):
        self._cmd = u'{duration}' \
                    u'-r {fps} {start}\"{filename}\"'.format(filename=self.filename,
                                                             fps=self.fps,
                                                             start='-start_number {} '.format(
                                                                     self.start) if self.sequence else '',
                                                             duration='-t {} '.format(
                                                                     self.duration) if self.duration else '')
        return self._cmd

    def cmd(self):
        self._ensure_ad_hoc()

        all_nodes = list(self.traverse_inputs())[::-1] + [self]
        global_cmd = self._generate_global_cmd()
        input_cmd = self._generate_input_cmd(all_nodes)
        filter_cmd = self._generate_filter_cmd(all_nodes)
        output_cmd = self._generate_output_cmd(all_nodes)

        return ' '.join([global_cmd, input_cmd, filter_cmd, output_cmd])

    def _generate_global_cmd(self):
        from globals import FFMPEG, Overwrite
        global_nodes = [FFMPEG(), Overwrite()]
        cmd = ' '.join(n.simple_cmd_string() for n in global_nodes)
        return cmd

    def _generate_output_cmd(self, all_nodes):
        from codec import BaseCodecNode
        output_nodes = [n for n in all_nodes if isinstance(n, (Output, BaseCodecNode))]
        cmd = ' '.join(n.simple_cmd_string() for n in output_nodes)
        return cmd

    def _generate_filter_cmd(self, all_nodes):
        from filters import BaseFilterNode
        filter_nodes = [n for n in all_nodes if isinstance(n, BaseFilterNode)]
        cmd = '-vf \"{cmd}\"'.format(cmd=','.join(n.simple_cmd_string() for n in filter_nodes))
        return cmd

    def _generate_input_cmd(self, all_nodes):
        input_nodes = [n for n in all_nodes if isinstance(n, Input)]
        cmd = ' '.join([n.simple_cmd_string() for n in input_nodes])
        return cmd

    def _ensure_ad_hoc(self):
        from dayu_ffmpeg.errors.base import DayuFFmpegException
        for n in self.traverse_inputs():
            if n.max_input_num > 1:
                raise DayuFFmpegException('{} input count is not 1, not supported in ad-hoc mode'.format(n))
            if self.validate() is False:
                raise DayuFFmpegException('{} is not validate, may missing input'.format(n))

    def run(self):
        import subprocess
        import re
        import time

        self.progress = {'render_frame': None, 'render_fps': None, 'render_speed': None, 'elapse_time': None}
        frame_regex = re.compile(r'^frame=\s*?(\d+)')
        fps_regex = re.compile(r'.*?fps=\s*?(\d+)')
        time_regex = re.compile(r'.*?time=\s*?(.*?)\s')
        speed_regex = re.compile(r'.*?speed=\s*?(.*?)x')

        start_time = time.time()
        _cmd = self.cmd()
        print _cmd
        shell_cmd = subprocess.Popen(_cmd,
                                     shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     universal_newlines=True)

        while True:
            if shell_cmd.poll() is not None:
                break

            message = shell_cmd.stderr.readline()
            self.progress['elapse_time'] = round(time.time() - start_time, 2)

            frame_match = frame_regex.match(message)
            fps_match = fps_regex.match(message)
            time_match = time_regex.match(message)
            speed_match = speed_regex.match(message)
            if frame_match and fps_match and time_regex and speed_regex:
                self.progress['render_frame'] = float(frame_match.group(1))
                self.progress['render_fps'] = float(fps_match.group(1))
                self.progress['render_speed'] = float(speed_match.group(1))
                yield self.progress

        if shell_cmd.returncode != 0:
            from dayu_ffmpeg.errors.base import DayuFFmpegException
            raise DayuFFmpegException('transcode failed: {}'.format(shell_cmd.stderr.readlines()))
