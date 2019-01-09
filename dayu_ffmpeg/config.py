#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import os

# 记录三个平台下，ffmpeg 的执行文件路径
FFMPEG_EXEC = {'win32' : os.sep.join((os.path.dirname(__file__), 'static', 'bin', 'win32', 'ffmpeg.exe')),
               'darwin': os.sep.join((os.path.dirname(__file__), 'static', 'bin', 'darwin', 'ffmpeg')),
               'linux2': os.sep.join((os.path.dirname(__file__), 'static', 'bin', 'linux2', 'ffmpeg'))}

FFMPEG_DEFAULT_FONT = {
    'win32' : os.sep.join((os.path.dirname(__file__), 'static', 'font', 'SourceHanSansK-Regular.ttf')),
    'darwin': os.sep.join((os.path.dirname(__file__), 'static', 'font', 'SourceHanSansK-Regular.ttf')),
    'linux2': os.sep.join((os.path.dirname(__file__), 'static', 'font', 'SourceHanSansK-Regular.ttf'))}

SINGLE_MEDIA_FORMAT = (u'.mov', u'.mp4', u'.mkv')

GLOBAL_ORDER_SCORE = 10
INPUT_ORDER_SCORE = 20
INPUT_HOLDER_ORDER_SCORE = 21
FILTER_ORDER_SCORE = 30
CODEC_ORDER_SCORE = 40
OUTPUT_HOLDER_ORDER_SCORE = 99
OUTPUT_ORDER_SCORE = 100
GROUP_ORDER_SCORE = 0
