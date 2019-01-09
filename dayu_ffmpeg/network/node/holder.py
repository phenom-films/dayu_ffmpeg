#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from base import BaseNode, UniqueList
from uuid import uuid4
from dayu_ffmpeg.config import INPUT_HOLDER_ORDER_SCORE, OUTPUT_HOLDER_ORDER_SCORE

class AbstractHolder(BaseNode):
    type = 'abstract_holder'
    order_score = -1

    def simple_cmd_string(self):
        return ''

    def complex_cmd_string(self):
        return self.simple_cmd_string()


class InputHolder(AbstractHolder):
    type = 'input_holder'
    max_input_num = 0
    order_score = INPUT_HOLDER_ORDER_SCORE

    def __init__(self, *args, **kwargs):
        self.id = kwargs.get('id', uuid4().hex)
        self.name = None
        self.label = None
        self.visited = None
        self.pos_x = -1.0
        self.pos_y = -1.0
        self.selected = False
        self.metadata = None
        self.parent = kwargs.get('parent', None)
        self.out_edges = [UniqueList() for _ in range(self.max_output_num)]
        self.link_num = None
        self.knobs = UniqueList()
        self.__dict__.update(kwargs)

    def validate(self):
        if self.input(0):
            return True
        return False

    @property
    def in_edges(self):
        if self.parent:
            return [self.parent.in_edges[self.link_num]]
        return UniqueList([None])

    def input(self, index):
        index = index if index >= 0 else index + len(self.in_edges)
        if index >= len(self.in_edges):
            return None
        edge = self.in_edges[index]
        if edge is None:
            return None
        else:
            return edge.endpoints.left

    def delete(self):
        if self.parent:
            self.parent.max_input_num -= 1
            all_inputholders = self.parent.inputholders
            index = all_inputholders.index(self)
            for n in all_inputholders:
                if n.link_num > index:
                    n.link_num -= 1
            for e in self.in_edges:
                if e:
                    e.delete()
            for g in self.out_edges:
                for e in g:
                    if e:
                        e.delete()
            if self.parent is not None:
                self.parent.inside_nodes.remove(self)
            del self.parent.in_edges[index]
            self.parent = None
            self.link_num = None

    def origin(self):
        node = self.input(0)
        return node.origin() if node else None

    def to_script(self):
        from copy import deepcopy
        result = deepcopy(self.__dict__)
        result['id'] = self.id
        result['type'] = self.type
        result['name'] = self.name
        result['label'] = self.label
        result['metadata'] = self.metadata
        result['pos_x'] = self.pos_x
        result['pos_y'] = self.pos_y
        result['selected'] = self.selected
        result['parent'] = self.parent.id if self.parent else None
        result['out_edges'] = [g.to_script() for g in self.out_edges]
        result['knobs'] = [k.to_script() for k in self.knobs]
        return result

    @classmethod
    def from_script(cls, object):
        from dayu_ffmpeg.ffscript import parse_ffscript_data
        instance = cls()
        instance.__dict__.update(object)
        instance.parent = parse_ffscript_data(instance.parent)
        instance.out_edges = [UniqueList([parse_ffscript_data(e) for e in g]) for g in instance.out_edges]
        instance.knobs = UniqueList([parse_ffscript_data(k) for k in instance.knobs])
        return instance


class OutputHolder(AbstractHolder):
    type = 'output_holder'
    max_output_num = 0
    order_score = OUTPUT_HOLDER_ORDER_SCORE

    def __init__(self, *args, **kwargs):
        self.id = kwargs.get('id', uuid4().hex)
        self.name = None
        self.label = None
        self.visited = None
        self.pos_x = -1.0
        self.pos_y = -1.0
        self.selected = False
        self.metadata = None
        self.parent = kwargs.get('parent', None)
        self.in_edges = UniqueList([None for _ in range(self.max_input_num)])
        self.link_num = None
        self.knobs = UniqueList()
        self.__dict__.update(kwargs)

    @property
    def out_edges(self):
        if self.parent:
            return [self.parent.out_edges[self.link_num]]
        return [UniqueList()]

    def delete(self):
        if self.parent:
            self.parent.max_output_num -= 1
            all_outputholders = self.parent.outputholders
            index = all_outputholders.index(self)
            for i, g in enumerate(self.parent.out_edges):
                if i > index:
                    for e in g:
                        e.output_group_index -= 1
            for n in all_outputholders:
                if n.link_num > index:
                    n.link_num -= 1
            for e in self.in_edges:
                if e:
                    e.delete()
            for g in self.out_edges:
                for e in g:
                    if e:
                        e.delete()
            self.parent.inside_nodes.remove(self)
            del self.parent.out_edges[index]
            self.parent = None
            self.link_num = None

    def origin(self):
        node = self.input(0)
        return node.origin() if node else None

    def to_script(self):
        from copy import deepcopy
        result = deepcopy(self.__dict__)
        result['id'] = self.id
        result['type'] = self.type
        result['name'] = self.name
        result['label'] = self.label
        result['metadata'] = self.metadata
        result['pos_x'] = self.pos_x
        result['pos_y'] = self.pos_y
        result['selected'] = self.selected
        result['parent'] = self.parent.id if self.parent else None
        result['in_edges'] = [e.to_script() if e else None for e in self.in_edges]
        result['knobs'] = [k.to_script() for k in self.knobs]
        return result

    @classmethod
    def from_script(cls, object):
        from dayu_ffmpeg.ffscript import parse_ffscript_data
        instance = cls()
        instance.__dict__.update(object)
        instance.parent = parse_ffscript_data(instance.parent)
        instance.in_edges = UniqueList([parse_ffscript_data(e) for e in instance.in_edges])
        instance.knobs = UniqueList([parse_ffscript_data(k) for k in instance.knobs])
        return instance
