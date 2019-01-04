#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from base import AbstractNode, BaseNode, UniqueList


class BaseGroupNode(BaseNode):
    type = 'base_group_node'
    max_input_num = 0

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


class Group(BaseGroupNode):
    type = 'group'


class RootNode(Group):
    type = 'root'

    def __setattr__(self, key, value):
        if key == 'parent' and key in self.__dict__:
            raise AttributeError('root node can\'t set parent!')
        else:
            super(RootNode, self).__setattr__(key, value)
