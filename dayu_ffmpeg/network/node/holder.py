#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from base import BaseNode, UniqueList
from uuid import uuid4


class AbstractHolder(BaseNode):
    type = 'abstract_holder'


class InputHolder(AbstractHolder):
    type = 'input_holder'
    max_input_num = 0

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
        self.__dict__.update(kwargs)

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
            self.parent.in_edges = UniqueList(self.parent.in_edges[:index] + self.parent.in_edges[index + 1:])
            self.parent = None
            self.link_num = None

    def origin(self):
        node = self.input(0)
        return node.origin() if node else None


class OutputHolder(AbstractHolder):
    type = 'output_holder'
    max_output_num = 0

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
            self.parent.out_edges = self.parent.out_edges[:index] + self.parent.out_edges[index + 1:]
            self.parent = None
            self.link_num = None

    def origin(self):
        node = self.input(0)
        return node.origin() if node else None