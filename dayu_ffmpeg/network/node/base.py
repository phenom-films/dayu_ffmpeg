#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from uuid import uuid4


class UniqueList(list):

    def __init__(self, *args, **kwargs):
        if args:
            for x in args[0]:
                self.append(x)

    def __add__(self, other):
        self.extend(other)
        return self

    def append(self, object):
        if object not in self or object is None:
            super(UniqueList, self).append(object)

    def extend(self, iterable):
        for x in iterable:
            self.append(x)

    def insert(self, index, object):
        if object not in self or object is None:
            super(UniqueList, self).insert(index, object)

    def remove(self, object):
        if object in self:
            super(UniqueList, self).remove(object)

    def __setitem__(self, i, o):
        if o not in self or o is None:
            super(UniqueList, self).__setitem__(i, o)


class AbstractNode(object):
    type = 'abstract_node'
    max_input_num = 1
    max_output_num = 1

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

    def set_input(self, node, index=None):
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()

    def check_allow_connect(self, node, input_index, output_index):
        raise NotImplementedError()

    def to_script(self):
        raise NotImplementedError()

    def from_script(self):
        raise NotImplementedError()


class BaseNode(AbstractNode):
    type = 'base_node'
    max_input_num = 1
    max_output_num = 1

    def __init__(self, *args, **kwargs):
        super(BaseNode, self).__init__(*args, **kwargs)
        self.in_edges = UniqueList([None for _ in range(self.max_input_num)])
        self.out_edges = [UniqueList() for _ in range(self.max_output_num)]

    def __contains__(self, item):
        return False

    def check_allow_connect(self, node, input_index, output_index):
        if self is node:
            return False
        if input_index >= self.max_input_num:
            return False
        if input_index + self.max_input_num < 0:
            return False
        if node is None:
            return True

        if not isinstance(node, BaseNode):
            return False
        if output_index >= node.max_output_num:
            return False
        if output_index + node.max_output_num < 0:
            return False

        if self.parent is not node.parent:
            return False
        if set(self.in_edges).intersection(set(node.out_edges[output_index])):
            return False

        return True

    def set_input(self, node, input_index=None, output_index=None):
        from dayu_ffmpeg.network.edge.base import DirectEdge

        input_index = input_index or 0
        output_index = output_index or 0
        if self.check_allow_connect(node, input_index, output_index):
            if node is None:
                if self.in_edges[input_index] is None:
                    return None
                else:
                    self.in_edges[input_index].delete()
                    return None
            else:
                if self.in_edges[input_index] is not None:
                    self.in_edges[input_index].delete()
                new_edge = DirectEdge(node, self, output_group_index=output_index)
                self.in_edges[input_index] = new_edge
                node.out_edges[output_index].append(new_edge)
                return new_edge
        return None

    def delete(self):
        for e in self.in_edges:
            if e:
                e.delete()
        for g in self.out_edges:
            for e in g:
                if e:
                    e.delete()
        if self.parent is not None:
            self.parent.inside_nodes.remove(self)
        self.parent = None

    def input(self, index):
        index = index if index >= 0 else index + self.max_input_num
        if index >= self.max_input_num:
            return None
        edge = self.in_edges[index]
        if edge is None:
            return None
        else:
            return edge.endpoints.left

    def connected_inputs(self):
        all_edges = (e for e in self.in_edges if e)
        return [e.endpoints.left for e in all_edges if e.endpoints.left]

    def connected_outputs(self, output_group_index=None):
        output_group_index = output_group_index or 0
        all_edges = (e for e in self.out_edges[output_group_index] if e)
        return [e.endpoints.right for e in all_edges if e.endpoints.right]
