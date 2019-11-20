#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'


def get_safe_string(string):
    return u'{}'.format(string.replace('\\', '\\\\').replace(':', '\\:').replace('%', r'\\\\%'))


def get_or_default_font(font_name):
    import os
    font_name = font_name if str(font_name).endswith('.ttf') else '{}.ttf'.format(font_name)
    font_path = os.sep.join((os.path.dirname(__file__), 'static', 'font', font_name))
    if os.path.exists(font_path):
        return font_path
    else:
        from dayu_ffmpeg.config import FFMPEG_DEFAULT_FONT
        import sys
        return FFMPEG_DEFAULT_FONT[sys.platform]
