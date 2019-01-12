#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from base import AbstractNode, BaseNode, UniqueList
from dayu_ffmpeg.config import GROUP_ORDER_SCORE, FILTER_ORDER_SCORE


class BaseGroupNode(BaseNode):
    type = 'base_group_node'
    max_input_num = 0
    max_output_num = 0
    order_score = GROUP_ORDER_SCORE

    def __init__(self, *args, **kwargs):
        super(BaseGroupNode, self).__init__(*args, **kwargs)
        self.out_edges = []
        self.inside_nodes = UniqueList()
        self.inside_edges = UniqueList()

    def __contains__(self, item):
        return item in self.inside_nodes

    def refresh_inputholder(self, node):
        from holder import InputHolder
        if isinstance(node, InputHolder):
            exist_inputholders = self.inputholders
            self.max_input_num = len(exist_inputholders)
            self.in_edges.append(None)
            node.link_num = self.max_input_num - 1

    def refresh_outputholder(self, node):
        from holder import OutputHolder
        if isinstance(node, OutputHolder):
            exist_outputholders = self.outputholders
            self.max_output_num = len(exist_outputholders)
            self.out_edges.append(UniqueList())
            node.link_num = self.max_output_num - 1

    @property
    def outputholders(self):
        from holder import OutputHolder
        return [n for n in self.inside_nodes if isinstance(n, OutputHolder)]

    @property
    def inputholders(self):
        from holder import InputHolder
        return [n for n in self.inside_nodes if isinstance(n, InputHolder)]

    def create_node(self, node_class, **kwargs):
        if isinstance(node_class, AbstractNode):
            node = node_class
            node_class.parent = self
        elif issubclass(node_class, AbstractNode):
            kwargs.update(parent=self)
            node = node_class(**kwargs)

        self.inside_nodes.append(node)
        self.refresh_inputholder(node)
        self.refresh_outputholder(node)
        return node

    def reset_visited(self):
        for n in self.inside_nodes:
            n.reset_visited()

    def traverse_children(self, recursive=False):
        from collections import deque
        queue = deque()
        queue.extend(self.inside_nodes)

        while queue:
            current = queue.popleft()
            yield current
            if recursive:
                if isinstance(current, BaseGroupNode):
                    queue.extendleft(current.inside_nodes[::-1])

    def to_script(self):
        result = super(BaseGroupNode, self).to_script()
        result['inside_nodes'] = self.inside_nodes.to_script()
        result['inside_edges'] = self.inside_edges.to_script()
        return result

    @classmethod
    def from_script(cls, object):
        from dayu_ffmpeg.ffscript import parse_ffscript_data
        instance = super(BaseGroupNode, cls).from_script(object)
        instance.inside_nodes = UniqueList([parse_ffscript_data(n) for n in instance.inside_nodes])
        instance.inside_edges = UniqueList([parse_ffscript_data(n) for n in instance.inside_edges])
        return instance


class Group(BaseGroupNode):
    type = 'group'


class ComplexFilterGroup(Group):
    type = 'filter_complex'
    order_score = FILTER_ORDER_SCORE


class RootNode(Group):
    type = 'root'

    def __init__(self, *args, **kwargs):
        super(RootNode, self).__init__(*args, **kwargs)
        self.prepare()

    def prepare(self):
        pass

    def __call__(self, input_list=None, output_list=None):
        from dayu_ffmpeg.errors.base import DayuFFmpegException
        if self.max_input_num == 0 and self.max_output_num == 0:
            raise DayuFFmpegException('this Root node has no inputholder and outputholder, '
                                      'maybe be a self-contain network, '
                                      'use .run() instead.')

        if len(input_list) < self.max_input_num or len(output_list) < self.max_output_num:
            raise DayuFFmpegException('this Root node has {} inputs and {} outputs, '
                                      'but only provide {} inputs and {} outputs'.format(self.max_input_num,
                                                                                         self.max_output_num,
                                                                                         len(input_list),
                                                                                         len(output_list)))
        for index in range(self.max_input_num):
            self.set_input(input_list[index], index)
        for index in range(self.max_output_num):
            output_list[index].set_input(self, output_index=index)

        return self

    def cmd(self):
        from globals import FFMPEG, Overwrite
        self.reset_visited()
        all_outputs = self._find_all_outputs()
        self._ensure_all_nodes_are_connected(all_outputs)
        all_inputs = self._find_all_inputs(all_outputs)
        all_complex_filters = [n for n in self._find_all_complex_filters() if n.visited]
        all_bound_nodes = self._find_all_bound(all_complex_filters, all_outputs)
        self._set_all_node_stream_in_num(all_outputs)
        all_global_nodes = [FFMPEG(), Overwrite()]

        global_cmd = self._generate_global_cmd(all_global_nodes)
        input_cmd = self._generate_input_cmd(all_inputs)
        complex_filter_cmd = self._generate_complex_filter_cmd(all_complex_filters)
        output_cmd = self._generate_output_cmd(all_bound_nodes)

        return ' '.join([global_cmd, input_cmd, complex_filter_cmd, output_cmd])

    def _generate_output_cmd(self, all_bound_nodes):
        output_cmd_list = []
        for o in all_bound_nodes:
            temp = '-map {stream} '.format(stream=''.join(['[{}]'.format(x) for x in o[0].stream_in_num]))
            temp += ' '.join([n.complex_cmd_string() for n in o])
            output_cmd_list.append(temp)
        output_cmd = ' '.join(output_cmd_list)
        return output_cmd

    def _generate_complex_filter_cmd(self, all_complex_filters):
        from holder import AbstractHolder
        useful_filters = [n for n in all_complex_filters if not isinstance(n, AbstractHolder)]
        complex_filter_cmd = '-filter_complex \"{cmd}\"'.format(
                cmd=';'.join([n.complex_cmd_string() for n in useful_filters]))
        return complex_filter_cmd

    def _generate_input_cmd(self, all_inputs):
        return ' '.join([n.complex_cmd_string() for n in all_inputs])

    def _generate_global_cmd(self, all_global_nodes):
        global_cmd = ' '.join([n.complex_cmd_string() for n in all_global_nodes])
        return global_cmd

    def _set_all_node_stream_in_num(self, all_outputs):
        for o in all_outputs:
            o.set_stream_in_num()
            for n in o.traverse_inputs():
                n.set_stream_in_num()

    def _ensure_all_nodes_are_connected(self, all_outputs):
        for o in all_outputs:
            for n in o.traverse_inputs():
                if n.validate() is False:
                    from dayu_ffmpeg.errors.base import DayuFFmpegException
                    raise DayuFFmpegException('{} has unconnected input'.format(n))

    def _find_all_bound(self, all_complex_filters, all_outputs):
        all_bound_node = []
        for o in all_outputs:
            previous = o
            for n in o.traverse_inputs():
                if n in all_complex_filters and previous not in all_complex_filters and n.visited:
                    all_bound_node.append([previous] + list(previous.traverse_outputs()))
                    break
                previous = n
        return all_bound_node

    def _find_all_complex_filters(self):
        cf_group = next((n for n in self.inside_nodes if isinstance(n, ComplexFilterGroup)), None)
        if not cf_group:
            from dayu_ffmpeg.errors.base import DayuFFmpegException
            raise DayuFFmpegException('root should have one and only one complex filter group!')
        all_complex_filters = list(cf_group.traverse_children(recursive=True))
        return all_complex_filters

    def _find_all_inputs(self, all_outputs):
        from dayu_ffmpeg.network import Input
        all_inputs = []
        for o in all_outputs:
            for n in o.traverse_inputs():
                n.set_stream_out_num()
                n.visited = True
                if isinstance(n, Input):
                    n.stream_out_num = len(all_inputs)
                    all_inputs.append(n)

        return all_inputs

    def _find_all_outputs(self):
        from dayu_ffmpeg.network import Output, OutputHolder
        from dayu_ffmpeg.errors.base import DayuFFmpegException
        if self.max_output_num == 0:
            all_outputs = [n for n in self.inside_nodes if isinstance(n, Output)]
            if not all_outputs:
                raise DayuFFmpegException('there is no output node, cannot generate cmd! '
                                          'please attach some output node')
        else:
            all_outputs = []
            for n in self.inside_nodes:
                if isinstance(n, Output):
                    all_outputs.append(n)
                if isinstance(n, OutputHolder):
                    out = next((o for o in n.traverse_outputs() if isinstance(o, Output)), None)
                    if not out:
                        raise DayuFFmpegException('an OutputHolder not connect to a Output node, '
                                                  'please make sure every OutputHolder is connected.')
                    all_outputs.append(out)

        return all_outputs

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
