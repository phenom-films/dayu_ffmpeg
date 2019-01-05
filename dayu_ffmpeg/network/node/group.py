#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from base import AbstractNode, BaseNode, UniqueList


class BaseGroupNode(BaseNode):
    type = 'base_group_node'
    max_input_num = 0
    max_output_num = 0

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
            self.max_input_num = len(exist_inputholders) + 1
            self.in_edges.append(None)
            node.link_num = self.max_input_num - 1

    def refresh_outputholder(self, node):
        from holder import OutputHolder
        if isinstance(node, OutputHolder):
            exist_outputholders = self.outputholders
            self.max_output_num = len(exist_outputholders) + 1
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
        if issubclass(node_class, AbstractNode):
            kwargs.update(parent=self)
            node = node_class(**kwargs)
            self.refresh_inputholder(node)
            self.refresh_outputholder(node)
            self.inside_nodes.append(node)
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


class Group(BaseGroupNode):
    type = 'group'


class ComplexFilterGroup(Group):
    type = 'filter_complex'


class RootNode(Group):
    type = 'root'

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
                    raise DayuFFmpegException('{} has unconnected input')

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
        all_complex_filters = list(cf_group.traverse_children())
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
        from dayu_ffmpeg.network import Output
        all_outputs = [n for n in self.inside_nodes if isinstance(n, Output)]
        if not all_outputs:
            from dayu_ffmpeg.errors.base import DayuFFmpegException
            raise DayuFFmpegException('there is no output node, cannot generate cmd!'
                                      'please attach some output node')
        return all_outputs
