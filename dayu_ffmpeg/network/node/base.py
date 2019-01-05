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

    def to_script(self):
        return [x.to_script() if x else None for x in self]


class AbstractNode(object):
    type = 'abstract_node'
    max_input_num = 1
    max_output_num = 1

    def __init__(self, *args, **kwargs):
        self.id = kwargs.get('id', uuid4().hex)
        self.name = None
        self.label = None
        self._cmd = None
        self.visited = None
        self.pos_x = -1.0
        self.pos_y = -1.0
        self.selected = False
        self.metadata = {}
        self.parent = kwargs.get('parent', None)

    def set_input(self, node, index=None):
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()

    def check_allow_connect(self, node, input_index, output_index):
        raise NotImplementedError()

    def to_script(self):
        raise NotImplementedError()

    @classmethod
    def from_script(cls, object):
        raise NotImplementedError()


class BaseNode(AbstractNode):
    type = 'base_node'
    max_input_num = 1
    max_output_num = 1

    def __init__(self, *args, **kwargs):
        super(BaseNode, self).__init__(*args, **kwargs)
        self.in_edges = UniqueList([None for _ in range(self.max_input_num)])
        self.out_edges = [UniqueList() for _ in range(self.max_output_num)]
        self.stream_in_num = []
        self.stream_out_num = None
        self.__dict__.update(**kwargs)

    def __contains__(self, item):
        return False

    def __rshift__(self, other):
        from dayu_ffmpeg.network import AbstractHolder, BaseGroupNode
        from dayu_ffmpeg.errors.base import DayuFFmpegException
        if not isinstance(other, BaseNode):
            raise DayuFFmpegException('{} not a BaseNode!'.format(other))
        if isinstance(other, (AbstractHolder, BaseGroupNode)):
            raise DayuFFmpegException('{} not support in ad-hoc mode, use complex mode instead!'.format(other))
        if self.max_output_num != 1:
            raise DayuFFmpegException('{}\'s output num is not 1, '
                                      'so not support in ad-hoc mode, use complex mode instead!'.format(self))
        if other.max_input_num != 1:
            raise DayuFFmpegException('{}\'s input num is not 1, '
                                      'so not support in ad-hoc mode, use complex mode instead!'.format(other))

        other.set_input(self)
        return other

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

    def set_output(self, node, output_index=None, input_index=None):
        node.set_input(self, input_index, output_index)

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

    def connected_in_edges(self):
        return [e for e in self.in_edges if e]

    def connected_out_edges(self, output_group_index=None):
        output_group_index = output_group_index or 0
        return [e for e in self.out_edges[output_group_index] if e]

    def traverse_inputs(self, recursive=True):
        from collections import deque
        from dayu_ffmpeg.network import BaseGroupNode

        queue = deque()
        queue.extend(self.connected_in_edges())
        while queue:
            item = queue.popleft()
            if isinstance(item, BaseNode):
                yield item
                queue.extendleft(item.connected_in_edges()[::-1])
                continue
            node = item.endpoints.left
            if isinstance(node, BaseGroupNode):
                if recursive:
                    queue.appendleft(node.outputholders[item.output_group_index])
                else:
                    yield node
                    queue.extendleft(node.connected_in_edges()[::-1])
            else:
                yield node
                queue.extendleft(node.connected_in_edges()[::-1])

    def traverse_outputs(self, recursive=True):
        from collections import deque
        from itertools import chain
        from dayu_ffmpeg.network import BaseGroupNode

        queue = deque()
        queue.extend(chain(*self.out_edges))

        while queue:
            item = queue.popleft()
            if not item:
                continue
            if isinstance(item, BaseNode) and not isinstance(item, BaseGroupNode):
                yield item
                queue.extendleft(list(chain(*item.out_edges))[::-1])
                continue

            e = item
            node = e.endpoints.right
            if isinstance(node, BaseGroupNode):
                if recursive:
                    index = node.in_edges.index(e)
                    queue.appendleft(node.inputholders[index])
                else:
                    yield node
                    queue.extendleft(list(chain(*node.out_edges))[::-1])
            else:
                yield node
                queue.extendleft(list(chain(*node.out_edges))[::-1])

    def validate(self):
        if self.max_input_num == 0:
            return True
        if self.max_input_num > 0 and len(self.connected_inputs()) == self.max_input_num:
            return True
        return False

    def reset_visited(self):
        self.visited = False

    def origin(self):
        return self

    def set_stream_in_num(self):
        from group import BaseGroupNode
        self.stream_in_num = []
        if self.max_input_num > 0 and self.connected_in_edges():
            for e in self.connected_in_edges():
                n = e.endpoints.left
                if isinstance(n, BaseGroupNode):
                    n = n.outputholders[e.output_group_index]
                self.stream_in_num.append(n.origin().stream_out_num)

    def set_stream_out_num(self):
        self.stream_out_num = self.origin().id

    def hierarchy(self):
        result = []
        current = self.parent
        while current:
            result.append(current)
            current = current.parent

        return result

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
        result['in_edges'] = [e.to_script() for e in self.in_edges]
        result['out_edges'] = [g.to_script() for g in self.out_edges]
        return result

    @classmethod
    def from_script(cls, object):
        instance = cls()
        instance.__dict__.update(object)
        return instance
