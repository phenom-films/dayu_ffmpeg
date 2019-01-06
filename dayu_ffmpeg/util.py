#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'


def get_safe_string(string):
    return u'{}'.format(string.replace('\\', '\\\\').replace(':', '\\:').replace('%', r'\\\\%'))
