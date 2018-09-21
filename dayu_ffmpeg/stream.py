#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'
__doc__ = \
    '''
    这里是封装了一些常用的ffmpeg 操作。
    使用方法非常简单，只需要按照下面的步骤：
    1. 使用不同的参数，实例化不同的class。这些Stream 对象，可以理解为用户需要的一步操作
    2. 使用 + 运算符，连接不同的stream
    3. （如果需要，不断的重复1、2 两步）
    4. 对最终的stream，调用.cmd()。得到shell 的命令行
    5. 使用subprocessing.Popen 来启动终端，执行命令
    '''

import sys

from config import FFMPEG_DEFAULT_FONT, FFMPEG_EXEC
from base import *


class FFmpeg(GlobalStream):
    _input_count = 0
    _name = 'ffmpeg'

    def __init__(self):
        super(FFmpeg, self).__init__()
        self._value = FFMPEG_EXEC[sys.platform]

    def __str__(self):
        return self._value


class Overwrite(GlobalStream):
    _name = 'overwrite'

    def __init__(self, overwrite=True):
        super(Overwrite, self).__init__()
        self.overwrite = overwrite
        self._value = u'-y' if self.overwrite else u'-n'

    def __str__(self):
        return self._value


class Input(InputStream):
    _name = 'input'

    def __init__(self, filename, start=None, trim_in_frame=None, trim_out_frame=None, fps=None, sequence=True):
        super(Input, self).__init__()
        self.filename = filename
        self.start = start
        self.trim_in = trim_in_frame
        self.trim_out = trim_out_frame
        self.fps = fps
        self.sequence = False if filename.endswith((u'.mov', u'.mp4', u'.mkv')) else True

    def __str__(self):
        if self.sequence:
            self._value = u'{start}-f image2 ' \
                          u'{fps}{trimin} ' \
                          u'-i \"{filename}\"' \
                          u''.format(start='-start_number {} '.format(self.start) if self.start else '',
                                     fps='-r {}'.format(self.fps) if self.fps else '',
                                     trimin=' -ss {}'.format(
                                             self.trim_in / self.fps) if self.trim_in else '',
                                     filename=self.filename)
        else:
            self._value = u'{fps}{trimin}' \
                          u' -i \"{filename}\"' \
                          u''.format(fps='-r {}'.format(self.fps) if self.fps else '',
                                     trimin=' -ss {}'.format(
                                             self.trim_in / self.fps) if self.trim_in else '',
                                     filename=self.filename)
        return self._value


class Fit(UnaryFilterStream):
    '''
    一个典型的复合型操作 stream。
    用户希望将图片保持宽高比缩放到一个画框中，可能会在上下 或者左右出现"黑边"。
    这个操作，其实是由Scale + Pad 两个单一操作组合而成的。a
    '''
    _name = 'fit'

    def __init__(self, width, height):
        super(Fit, self).__init__()
        self.width = width
        self.height = height
        self._is_combine_op = True
        _scale_op = Scale(width=u'iw*min({0}/iw\\,{1}/ih)'.format(self.width, self.height),
                          height=u'ih*min({0}/iw\\,{1}/ih)'.format(self.width, self.height))
        _pad_op = Pad(w=self.width, h=self.height,
                      x=u'({0}-iw*min({0}/iw\\,{1}/ih))/2'.format(self.width, self.height),
                      y=u'({1}-ih*min({0}/iw\\,{1}/ih))/2'.format(self.width, self.height))
        self.combine_op = [_scale_op, _pad_op]


class Trim(UnaryFilterStream):
    _name = 'scale'

    def __init__(self, start=None, end=None):
        super(Trim, self).__init__()
        self.start = start
        self.end = end

    def __str__(self):
        self._value = u'{stream_in}trim=start_frame={start}:' \
                      u'end_frame={end}{stream_out}'.format(stream_in=self._stream_in,
                                                            stream_out=self._stream_out,
                                                            start=self.start,
                                                            end=self.end)
        return self._value


class Scale(UnaryFilterStream):
    _name = 'scale'

    def __init__(self, width=None, height=None, scale_x=None, scale_y=None):
        super(Scale, self).__init__()
        self.width = width
        self.height = height
        self.scale_x = scale_x
        self.scale_y = scale_y

    def __str__(self):
        if self.scale_x is None and self.scale_y is None:
            self._value = u'{stream_in}scale=w={width}:h={height}{stream_out}'.format(stream_in=self._stream_in,
                                                                                      stream_out=self._stream_out,
                                                                                      width=self.width,
                                                                                      height=self.height)
            return self._value
        if self.width is None and self.height is None:
            self._value = u'{stream_in}scale=w=iw*{scale_x}:h=ih*{scale_y}{stream_out}'.format(
                    stream_in=self._stream_in,
                    stream_out=self._stream_out,
                    scale_x=self.scale_x,
                    scale_y=self.scale_y)
            return self._value


class Overlay(BinaryFilterStream):
    _name = 'overlay'

    def __init__(self, fg_stream, x=0, y=0):
        super(Overlay, self).__init__()
        self._inputs[1] = fg_stream
        self.x = x
        self.y = y

    def __str__(self):
        self._value = u'{stream_in}{fg}overlay=x={x}:y={y}{stream_out}'.format(fg=self._inputs[1]._stream_out,
                                                                               stream_in=self._stream_in,
                                                                               stream_out=self._stream_out,
                                                                               x=self.x,
                                                                               y=self.y)
        return self._value


class DrawBox(UnaryFilterStream):
    _name = 'drawbox'

    def __init__(self, x='iw/4', y='ih/2', w='iw/2', h='ih/2', color='Black@0.85', thickness='fill'):
        super(DrawBox, self).__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.thickness = thickness

    def __str__(self):
        self._value = u'{stream_in}drawbox=x={x}:y={y}:w={w}:h={h}:' \
                      u'c={color}:t={thickness}{stream_out}'.format(stream_in=self._stream_in,
                                                                    stream_out=self._stream_out,
                                                                    x=self.x,
                                                                    y=self.y,
                                                                    w=self.w,
                                                                    h=self.h,
                                                                    color=self.color,
                                                                    thickness=self.thickness)
        return self._value


class DrawEveryFrame(BinaryFilterStream):
    _name = 'drawtext'

    def __init__(self, text_list, x='w/2', y='h/2', size=32, color='white', font=None,
                 box=False, box_color='black@0.5', boxborder=2,
                 shadow_x=0, shadow_y=0):
        super(DrawEveryFrame, self).__init__()
        self._is_combine_op = True
        for index, t in enumerate(text_list):
            self.combine_op.append(DrawText(t, x, y, size, color, font, box, box_color,
                                            boxborder, shadow_x, shadow_y,
                                            'eq(n\\,{})'.format(index)))


class DrawText(UnaryFilterStream):
    _name = 'drawtext'

    def __init__(self, text, x='w/2', y='h/2', size=32, color='white', font=None,
                 box=False, box_color='black@0.5', boxborder=2,
                 shadow_x=0, shadow_y=0, enable=None):
        super(DrawText, self).__init__()
        self.text = text
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.font = font if font else FFMPEG_DEFAULT_FONT[sys.platform]
        self.box = box
        self.box_color = box_color
        self.box_border = boxborder
        self.shadowx = shadow_x
        self.shadowy = shadow_y
        self.enable = enable

    def __str__(self):
        self._value = u'{stream_in}drawtext=text=\'{text}\':x={x}:' \
                      u'y={y}:fontsize={size}:' \
                      u'fontcolor={color}:shadowx={shadowx}:' \
                      u'shadowy={shadowy}' \
                      u'{font}{box}{enable}{stream_out}'.format(stream_in=self._stream_in,
                                                                stream_out=self._stream_out,
                                                                text=self.text.replace('%', r'\\\\%'),
                                                                x=self.x,
                                                                y=self.y,
                                                                size=self.size,
                                                                color=self.color,
                                                                shadowx=self.shadowx,
                                                                shadowy=self.shadowy,
                                                                font=':fontfile=\'{}\''.format(
                                                                        self.font.replace('\\', '\\\\').replace(':',
                                                                                                                '\\:')) if self.font else '',
                                                                box=':box=1:boxcolor={}:boxborder={}'.format(
                                                                        self.box_color,
                                                                        self.box_border) if self.box else '',
                                                                enable=':enable={}'.format(
                                                                        self.enable) if self.enable else '')
        return self._value


class DrawDate(UnaryFilterStream):
    _name = 'drawtext'

    def __init__(self, x='w/2', y='h/2', size=32, color='white', font=None, date_format='%{localtime:%Y-%m-%d}',
                 box=False, box_color='black@0.5', boxborder=2,
                 shadow_x=0, shadow_y=0):
        super(DrawDate, self).__init__()
        self.date_format = date_format
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.font = font if font else FFMPEG_DEFAULT_FONT[sys.platform]
        self.box = box
        self.box_color = box_color
        self.box_border = boxborder
        self.shadowx = shadow_x
        self.shadowy = shadow_y

    def __str__(self):
        self._value = u'{stream_in}drawtext=text=\'{date_format}\':' \
                      u'x={x}:y={y}:fontsize={size}:' \
                      u'fontcolor={color}:shadowx={shadowx}:' \
                      u'shadowy={shadowy}' \
                      u'{font}{box}{stream_out}'.format(stream_in=self._stream_in,
                                                        stream_out=self._stream_out,
                                                        date_format=self.date_format.replace(':', '\\:'),
                                                        x=self.x,
                                                        y=self.y,
                                                        size=self.size,
                                                        color=self.color,
                                                        shadowx=self.shadowx,
                                                        shadowy=self.shadowy,
                                                        font=':fontfile=\'{}\''.format(self.font.replace('\\',
                                                                                                         '\\\\').replace(
                                                                ':', '\\:')) if self.font else '',
                                                        box=':box=1:boxcolor={}:boxborder={}'.format(
                                                                self.box_color, self.box_border) if self.box else '')
        return self._value


class DrawTimecode(UnaryFilterStream):
    _name = 'drawtext'

    def __init__(self, x='w/2', y='h/2', size=32, color='white', font=None, timecode='00:00:00:00', fps=24,
                 box=False, box_color='black@0.5', boxborder=2,
                 shadow_x=0, shadow_y=0):
        super(DrawTimecode, self).__init__()
        self.timecode = timecode
        self.fps = fps
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.font = font if font else FFMPEG_DEFAULT_FONT[sys.platform]
        self.box = box
        self.box_color = box_color
        self.box_border = boxborder
        self.shadowx = shadow_x
        self.shadowy = shadow_y

    def __str__(self):
        self._value = u'{stream_in}drawtext=timecode=\'{timecode}\':r={fps}:x={x}:' \
                      u'y={y}:fontsize={size}:' \
                      u'fontcolor={color}:shadowx={shadowx}:' \
                      u'shadowy={shadowy}' \
                      u'{font}{box}{stream_out}'.format(stream_in=self._stream_in,
                                                        stream_out=self._stream_out,
                                                        timecode=self.timecode.replace(':', '\\:'),
                                                        fps=self.fps,
                                                        x=self.x,
                                                        y=self.y,
                                                        size=self.size,
                                                        color=self.color,
                                                        shadowx=self.shadowx,
                                                        shadowy=self.shadowy,
                                                        font=':fontfile=\'{}\''.format(self.font.replace('\\',
                                                                                                         '\\\\').replace(
                                                                ':', '\\:')) if self.font else '',
                                                        box=':box=1:boxcolor={}:boxborder={}'.format(
                                                                self.box_color, self.box_border) if self.box else '')
        return self._value


class DrawFrames(UnaryFilterStream):
    _name = 'drawtext'

    def __init__(self, text='%{n}', x='w/2', y='h/2', size=32, color='white', font=None, start=1001,
                 box=False, box_color='black@0.5', boxborder=2,
                 shadow_x=0, shadow_y=0):
        super(DrawFrames, self).__init__()
        self.text = text
        self.start = start
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.font = font if font else FFMPEG_DEFAULT_FONT[sys.platform]
        self.box = box
        self.box_color = box_color
        self.box_border = boxborder
        self.shadowx = shadow_x
        self.shadowy = shadow_y

    def __str__(self):
        self._value = u'{stream_in}drawtext=text=\'{number}\':start_number={start}:x={x}:' \
                      u'y={y}:fontsize={size}:' \
                      u'fontcolor={color}:shadowx={shadowx}:' \
                      u'shadowy={shadowy}' \
                      u'{font}{box}{stream_out}'.format(stream_in=self._stream_in,
                                                        stream_out=self._stream_out,
                                                        number=self.text,
                                                        fontfile=self.font.replace('\\', '\\\\').replace(':', '\\:'),
                                                        start=self.start,
                                                        x=self.x,
                                                        y=self.y,
                                                        size=self.size,
                                                        color=self.color,
                                                        shadowx=self.shadowx,
                                                        shadowy=self.shadowy,
                                                        font=':fontfile=\'{}\''.format(self.font.replace('\\',
                                                                                                         '\\\\').replace(
                                                                ':', '\\:')) if self.font else '',
                                                        box=':box=1:boxcolor={}:boxborder={}'.format(
                                                                self.box_color, self.box_border) if self.box else '')
        return self._value


class DrawMask(UnaryFilterStream):
    _name = 'drawbox'

    def __init__(self, ratio, color='black'):
        super(DrawMask, self).__init__()
        self.ratio = ratio
        self.color = color

    def __str__(self):
        self._value = u'{stream_in}drawbox=x={x}:y={y}:w={w}:h={h}:' \
                      u'c={color}:t={thickness}{alpha}{stream_out}'.format(stream_in=self._stream_in,
                                                                           stream_out=self._stream_out,
                                                                           x='-t',
                                                                           y='0',
                                                                           w='iw+t*2',
                                                                           h='ih',
                                                                           color=self.color,
                                                                           thickness='(ih-(iw/{}))/2'.format(
                                                                                   self.ratio),
                                                                           alpha=',format=yuv444p' if '@' in self.color else '')
        return self._value


class AspectRatio(UnaryFilterStream):
    _name = 'setsar'

    def __init__(self, sar='1'):
        super(AspectRatio, self).__init__()
        self.sar = sar

    def __str__(self):
        self._value = u'{stream_in}setsar=sar={sar}' \
                      u'{stream_out}'.format(stream_in=self._stream_in,
                                             stream_out=self._stream_out,
                                             sar='/'.join(map(str, float(self.sar).as_integer_ratio())))
        return self._value


class Lut3d(UnaryFilterStream):
    _name = 'lut3d'

    def __init__(self, lut_file):
        super(Lut3d, self).__init__()
        self.lut = lut_file

    def __str__(self):
        if not self.lut:
            self._value = u''
        else:
            self._value = u'{stream_in}lut3d=\'{lut}\'{stream_out}'.format(stream_in=self._stream_in,
                                                                           stream_out=self._stream_out,
                                                                           lut=self.lut.replace('\\', '/').replace(':',
                                                                                                                   '\\:'))
        return self._value


class Pad(UnaryFilterStream):
    _name = 'pad'

    def __init__(self, w=10, h=10, x='(ow-iw)/2', y='(oh-ih)/2', color='black'):
        super(Pad, self).__init__()
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.color = color

    def __str__(self):
        self._value = u'{stream_in}pad=w={w}:h={h}:x={x}:y={y}:' \
                      u'color={color}{stream_out}'.format(stream_in=self._stream_in,
                                                          stream_out=self._stream_out,
                                                          w=self.w,
                                                          h=self.h,
                                                          x=self.x,
                                                          y=self.y,
                                                          color=self.color)
        return self._value


class GeneralUnaryFilter(UnaryFilterStream):
    _name = 'generic'

    def __init__(self, filter_name, **kwargs):
        super(GeneralUnaryFilter, self).__init__()
        self.param = kwargs
        self.filter_name = filter_name

    def __str__(self):
        temp = ['{}={}'.format(key, value) for key, value in self.param.items()]
        self._value = u'{stream_in}{filter}={args}{stream_out}'.format(stream_in=self._stream_in,
                                                                       stream_out=self._stream_out,
                                                                       filter=self.filter_name,
                                                                       args=':'.join(temp))
        return self._value


class Codec(CodecStream):
    _name = 'codec'

    def __init__(self, video='prores_ks', audio=None):
        super(Codec, self).__init__()
        self.video = video
        self.audio = audio

    def __str__(self):
        self._value = u'-codec:v {video}'.format(video=self.video)
        if self.audio:
            self._value += u' -codec:a {audio}'.format(audio=self.audio)
        return self._value


class WriteTimecode(CodecStream):
    _name = 'timecode'

    def __init__(self, timecode=None):
        super(WriteTimecode, self).__init__()
        self.timecode = timecode

    def __str__(self):
        self._value = u'-timecode {tc}'.format(tc=self.timecode)
        return self._value


class WriteReel(CodecStream):
    _name = 'metadata'

    def __init__(self, reel=None):
        super(WriteReel, self).__init__()
        self.reel = reel

    def __str__(self):
        self._value = u'-metadata:s:v:0 reel_name={reel}'.format(reel=self.reel)
        return self._value


class Quality(CodecStream):
    _name = 'qscale'

    def __init__(self, qscale=2):
        super(Quality, self).__init__()
        self.qscale = qscale

    def __str__(self):
        self._value = u'-qscale:v {qscale}'.format(qscale=self.qscale) if self.qscale else u''
        return self._value


class Frames(CodecStream):
    _name = 'vframes'

    def __init__(self, frame_count):
        super(Frames, self).__init__()
        self.frame_count = frame_count

    def __str__(self):
        self._value = u'-frames:v {frame}'.format(frame=self.frame_count)
        return self._value


class PixelFormat(CodecStream):
    _name = 'pix_fmt'

    def __init__(self, pixel_format='yuv422p10le', profile=2):
        super(PixelFormat, self).__init__()
        self.pixel_format = pixel_format
        self.profile = profile

    def __str__(self):
        self._value = u'{pix}{profile}'.format(pix='-pix_fmt {}'.format(self.pixel_format) if self.pixel_format else '',
                                               profile=' -profile:v {}'.format(self.profile) if self.profile else '')
        return self._value


class Output(OutputStream):
    _name = 'output'

    def __init__(self, filename, fps=24, start=1001, sequence=False, duration=None):
        super(Output, self).__init__()
        self.filename = filename
        self.fps = fps
        self.start = start
        self.sequence = sequence
        self.duration = duration

    def __str__(self):
        self._value = u'{duration}' \
                      u'-r {fps} {start}\"{filename}\"'.format(filename=self.filename,
                                                               fps=self.fps,
                                                               start='-start_number {} '.format(
                                                                       self.start) if self.sequence else '',
                                                               duration='-t {} '.format(
                                                                       self.duration) if self.duration else '')
        return self._value


if __name__ == '__main__':
    path = u'/Users/andyguo/Downloads/ep19_episode  中文 _4_180904.mp4'
    path2 = '/Users/andyguo/Desktop/%03d.png'

    result = FFmpeg() >> Overwrite() >> \
             Input(path, sequence=False, fps=25, trim_in_frame=100, trim_out_frame=200) >> \
             Scale(1920, 1080) >> \
             WriteTimecode('11:22:11:22') >> \
             Codec(video='prores_ks') >> \
             PixelFormat(pixel_format='yuva444p10le', profile='4444') >> \
             WriteReel('owkeh') >> \
             Output('/Users/andyguo/Desktop/111.mov', fps=25.0)
    print result.cmd()

    prev = None
    for x in result.run():
        print prev is x
        prev = x

    print 'finish!!'

