#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import os

# 记录三个平台下，ffmpeg 的执行文件路径
FFMPEG_EXEC = {'win32' : r'Y:\td\dayu_bin\win32\ffmpeg_342\ffmpeg.exe',
               'darwin': '/Volumes/filedata/td/dayu_bin/mac/ffmpeg_342/ffmpeg',
               'linux2': 'ffmpeg'}

FFMPEG_DEFAULT_FONT = {'win32' : os.sep.join((os.path.dirname(__file__), 'static', 'tahoma.ttf')),
                       'darwin': os.sep.join((os.path.dirname(__file__), 'static', 'tahoma.ttf')),
                       'linux2': os.sep.join((os.path.dirname(__file__), 'static', 'tahoma.ttf'))}
