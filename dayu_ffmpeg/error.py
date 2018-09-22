#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import exceptions


class DayuFFmpegPriorityError(exceptions.ValueError):
    pass


class DayuFFmpegValueError(exceptions.ValueError):
    pass


class DayuFFmpegRenderError(exceptions.RuntimeError):
    pass
