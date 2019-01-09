#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from uuid import uuid4


class AbstractKnob(object):
    type = 'abstract_knob'

    def __init__(self, *args, **kwargs):
        super(AbstractKnob, self).__init__(*args, **kwargs)

    def delete(self):
        raise NotImplementedError()

    @property
    def value(self):
        raise NotImplementedError()

    @value.setter
    def value(self, data):
        raise NotImplementedError()

    def to_script(self):
        raise NotImplementedError()

    @classmethod
    def from_script(cls, object):
        raise NotImplementedError()


class BaseKnob(AbstractKnob):
    type = 'base_knob'

    def __init__(self, link=None, attribute=None, parent=None, **kwargs):
        self.id = kwargs.get('id', uuid4().hex)
        self.name = None
        self.label = None
        self.link = link
        self.attribute = attribute
        self.parent = parent
        self.__dict__.update(kwargs)

    def to_script(self):
        from copy import deepcopy
        result = deepcopy(self.__dict__)
        result['id'] = self.id
        result['type'] = self.type
        result['name'] = self.name
        result['link'] = self.link.id if self.link else None
        result['attribute'] = self.attribute
        result['parent'] = self.parent.id if self.parent else None
        return result

    @classmethod
    def from_script(cls, object):
        instance = cls()
        instance.__dict__.update(object)
        return instance

    def delete(self):
        if self.parent:
            self.parent.knobs.remove(self)
        self.link = None
        self.attribute = None
        self.parent = None

    @property
    def value(self):
        if isinstance(self.link, BaseKnob):
            return self.link.value
        return getattr(self.link, self.attribute, None)

    @value.setter
    def value(self, data):
        if isinstance(self.link, BaseKnob):
            self.link.value = data
        else:
            setattr(self.link, self.attribute, data)
