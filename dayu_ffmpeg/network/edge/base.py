#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from uuid import uuid4


class TwoEndPoints(object):
    def __init__(self, left=None, right=None):
        super(TwoEndPoints, self).__init__()
        self.left = left
        self.right = right

    def __setattr__(self, key, value):
        if key not in ('left', 'right'):
            raise KeyError('TwoEndPoints only has left and right attributes')
        if key in self.__dict__:
            raise AttributeError('TwoEndPoint can\'t be set new value')
        super(TwoEndPoints, self).__setattr__(key, value)


class AbstractEdge(object):
    type = 'abstract_edge'

    def __init__(self, *args, **kwargs):
        self.id = kwargs.get('id', uuid4().hex)
        self.name = None
        self.label = None
        self.selected = False
        self.metadata = None
        self.endpoints = TwoEndPoints()
        self.parent = None
        self.output_group_index = kwargs.get('output_group_index', None)

    def delete(self):
        raise NotImplementedError()

    def connect(self, left, right):
        raise NotImplementedError()


class DirectEdge(AbstractEdge):
    type = 'direct_edge'

    def __init__(self, left=None, right=None, **kwargs):
        super(DirectEdge, self).__init__(**kwargs)
        self.endpoints = TwoEndPoints(left, right)
        if left.parent is not None:
            left.parent.inside_edges.append(self)
        if left.parent is not None:
            right.parent.inside_edges.append(self)


    def delete(self):
        self.endpoints.left.out_edges[self.output_group_index].remove(self)
        if self in self.endpoints.right.in_edges:
            index = self.endpoints.right.in_edges.index(self)
            self.endpoints.right.in_edges[index] = None
        if self.endpoints.left.parent is not None:
            self.endpoints.left.parent.inside_edges.remove(self)
        if self.endpoints.right.parent is not None:
            self.endpoints.right.parent.inside_edges.remove(self)

        self.endpoints = TwoEndPoints()

    def connect(self, left, right):
        pass
