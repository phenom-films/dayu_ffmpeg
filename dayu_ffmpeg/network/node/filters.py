#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from base import BaseNode
from dayu_ffmpeg.config import FILTER_ORDER_SCORE


class BaseFilterNode(BaseNode):
    type = 'base_filter_node'
    order_score = FILTER_ORDER_SCORE

    def __init__(self, *args, **kwargs):
        self.stream_in_num = []
        self.stream_out_num = None
        super(BaseFilterNode, self).__init__(*args, **kwargs)

    def simple_cmd_string(self):
        return self.type

    def complex_cmd_string(self):
        return '{stream_in}{cmd}{stream_out}'.format(
                stream_in=''.join(['[{}]'.format(x) for x in self.stream_in_num]),
                cmd=self.simple_cmd_string(),
                stream_out='[{}]'.format(self.stream_out_num))


class Scale(BaseFilterNode):
    type = 'scale'

    def __init__(self, width=1920, height=1080, relative_scale=False, **kwargs):
        self.width = width
        self.height = height
        self.relative_scale = relative_scale
        super(Scale, self).__init__(**kwargs)

    def simple_cmd_string(self):
        if self.relative_scale:
            self._cmd = u'scale=w=iw*{scale_x}:h=ih*{scale_y}'.format(scale_x=self.width,
                                                                      scale_y=self.height)
            return self._cmd
        else:
            self._cmd = u'scale=w={width}:h={height}'.format(width=self.width,
                                                             height=self.height)
            return self._cmd


class Overlay(BaseFilterNode):
    type = 'overlay'
    max_input_num = 2

    def __init__(self, x=0, y=0, **kwargs):
        self.x = x
        self.y = y
        super(Overlay, self).__init__(**kwargs)

    def simple_cmd_string(self):
        self._cmd = u'overlay=x={x}:y={y}'.format(x=self.x, y=self.y)
        return self._cmd


class DrawBox(BaseFilterNode):
    type = 'drawbox'

    def __init__(self, x='iw/4', y='ih/4', w='iw/2', h='ih/2', color='Black@0.7', thickness='fill', **kwargs):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.thickness = thickness
        super(DrawBox, self).__init__(**kwargs)

    def simple_cmd_string(self):
        self._cmd = u'drawbox=x={x}:y={y}:w={w}:h={h}:c={color}:t={thickness}'.format(
                x=self.x,
                y=self.y,
                w=self.w,
                h=self.h,
                color=self.color,
                thickness=self.thickness)
        return self._cmd


class DrawText(BaseFilterNode):
    type = 'drawtext'

    def __init__(self, text='', x='w/2', y='h/2', size=32, color='white', font=None,
                 box=False, box_color='black@0.5', boxborder=2,
                 shadow_x=0, shadow_y=0, enable=None, **kwargs):
        from dayu_ffmpeg.config import FFMPEG_DEFAULT_FONT
        import sys
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
        super(DrawText, self).__init__(**kwargs)

    def simple_cmd_string(self):
        from dayu_ffmpeg.util import get_safe_string
        self._cmd = u'drawtext=text=\'{text}\':x={x}:' \
                    u'y={y}:fontsize={size}:' \
                    u'fontcolor={color}:shadowx={shadowx}:' \
                    u'shadowy={shadowy}' \
                    u'{font}{box}{enable}'.format(
                text=get_safe_string(self.text),
                x=self.x,
                y=self.y,
                size=self.size,
                color=self.color,
                shadowx=self.shadowx,
                shadowy=self.shadowy,
                font=':fontfile=\'{}\''.format(get_safe_string(self.font)) if self.font else '',
                box=':box=1:boxcolor={}:boxborder={}'.format(self.box_color, self.box_border) if self.box else '',
                enable=':enable={}'.format(self.enable) if self.enable else '')
        return self._cmd

    def complex_cmd_string(self):
        if self.text:
            return super(DrawText, self).complex_cmd_string()
        else:
            return '{stream_in}{cmd}{stream_out}'.format(
                    stream_in=''.join(['[{}]'.format(x) for x in self.stream_in_num]),
                    cmd=Null().simple_cmd_string(),
                    stream_out='[{}]'.format(self.stream_out_num))


class DrawDate(BaseFilterNode):
    type = 'draw_date'

    def __init__(self, x='w/2', y='h/2', size=32, color='white', font=None, date_format='%{localtime:%Y-%m-%d}',
                 box=False, box_color='black@0.5', boxborder=2,
                 shadow_x=0, shadow_y=0, **kwargs):
        from dayu_ffmpeg.config import FFMPEG_DEFAULT_FONT
        import sys
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
        super(DrawDate, self).__init__(**kwargs)

    def simple_cmd_string(self):
        from dayu_ffmpeg.util import get_safe_string
        self._cmd = u'drawtext=text=\'{date_format}\':' \
                    u'x={x}:y={y}:fontsize={size}:' \
                    u'fontcolor={color}:shadowx={shadowx}:' \
                    u'shadowy={shadowy}' \
                    u'{font}{box}'.format(
                date_format=get_safe_string(self.date_format),
                x=self.x,
                y=self.y,
                size=self.size,
                color=self.color,
                shadowx=self.shadowx,
                shadowy=self.shadowy,
                font=':fontfile=\'{}\''.format(get_safe_string(self.font)) if self.font else '',
                box=':box=1:boxcolor={}:boxborder={}'.format(self.box_color, self.box_border) if self.box else '', )
        return self._cmd


class DrawTimecode(BaseFilterNode):
    type = 'draw_timecode'

    def __init__(self, x='w/2', y='h/2', size=32, color='white', font=None, timecode='00:00:00:00', fps=24,
                 box=False, box_color='black@0.5', boxborder=2,
                 shadow_x=0, shadow_y=0, **kwargs):
        from dayu_ffmpeg.config import FFMPEG_DEFAULT_FONT
        import sys
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
        super(DrawTimecode, self).__init__(**kwargs)

    def __str__(self):
        from dayu_ffmpeg.util import get_safe_string
        self._cmd = u'drawtext=timecode=\'{timecode}\':r={fps}:x={x}:' \
                    u'y={y}:fontsize={size}:' \
                    u'fontcolor={color}:shadowx={shadowx}:' \
                    u'shadowy={shadowy}' \
                    u'{font}{box}'.format(
                timecode=get_safe_string(self.timecode),
                fps=self.fps,
                x=self.x,
                y=self.y,
                size=self.size,
                color=self.color,
                shadowx=self.shadowx,
                shadowy=self.shadowy, font=':fontfile=\'{}\''.format(get_safe_string(self.font)) if self.font else '',
                box=':box=1:boxcolor={}:boxborder={}'.format(self.box_color, self.box_border) if self.box else '')
        return self._cmd


class DrawFrames(BaseFilterNode):
    type = 'draw_frames'

    def __init__(self, text='%{n}', x='w/2', y='h/2', size=32, color='white', font=None, start=1001,
                 box=False, box_color='black@0.5', boxborder=2,
                 shadow_x=0, shadow_y=0, **kwargs):
        from dayu_ffmpeg.config import FFMPEG_DEFAULT_FONT
        import sys
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
        super(DrawFrames, self).__init__(**kwargs)

    def simple_cmd_string(self):
        from dayu_ffmpeg.util import get_safe_string
        self._cmd = u'drawtext=text=\'{number}\':start_number={start}:x={x}:' \
                    u'y={y}:fontsize={size}:' \
                    u'fontcolor={color}:shadowx={shadowx}:' \
                    u'shadowy={shadowy}' \
                    u'{font}{box}'.format(
                number=self.text,
                fontfile=get_safe_string(self.font),
                start=self.start,
                x=self.x,
                y=self.y,
                size=self.size,
                color=self.color,
                shadowx=self.shadowx,
                shadowy=self.shadowy,
                font=':fontfile=\'{}\''.format(get_safe_string(self.font)) if self.font else '',
                box=':box=1:boxcolor={}:boxborder={}'.format(self.box_color, self.box_border) if self.box else '', )
        return self._cmd


class DrawMask(BaseFilterNode):
    type = 'draw_mask'

    def __init__(self, ratio, color='black', **kwargs):
        self.ratio = ratio
        self.color = color
        super(DrawMask, self).__init__(**kwargs)

    def simple_cmd_string(self):
        self._cmd = u'drawbox=x={x}:y={y}:w={w}:h={h}:c={color}:t={thickness}{alpha}'.format(
                x='-t',
                y='0',
                w='iw+t*2',
                h='ih',
                color=self.color,
                thickness='(ih-(iw/{}))/2'.format(self.ratio),
                alpha=',format=yuv444p' if '@' in self.color else '')
        return self._cmd


class AspectRatio(BaseFilterNode):
    type = 'setsar'

    def __init__(self, sar='1', **kwargs):
        self.sar = sar
        super(AspectRatio, self).__init__(**kwargs)

    def simple_cmd_string(self):
        self._cmd = u'setsar=sar={sar}'.format(
                sar='/'.join(map(str, float(self.sar).as_integer_ratio())))
        return self._cmd


class Null(BaseFilterNode):
    type = 'null'

    def __init__(self, **kwargs):
        super(Null, self).__init__(**kwargs)

    def simple_cmd_string(self):
        self._cmd = u'null'
        return self._cmd


class Lut3d(BaseFilterNode):
    type = 'lut3d'

    def __init__(self, lut_file, **kwargs):
        self.lut = lut_file
        super(Lut3d, self).__init__(**kwargs)

    def simple_cmd_string(self):
        from dayu_ffmpeg.util import get_safe_string
        if not self.lut:
            self._cmd = u''
        else:
            self._cmd = u'lut3d=\'{lut}\''.format(
                    lut=get_safe_string(self.lut))
        return self._cmd

    def complex_cmd_string(self):
        if self.lut:
            return super(Lut3d, self).complex_cmd_string()
        else:
            return '{stream_in}{cmd}{stream_out}'.format(
                    stream_in=''.join(['[{}]'.format(x) for x in self.stream_in_num]),
                    cmd=Null().simple_cmd_string(),
                    stream_out='[{}]'.format(self.stream_out_num))


class Pad(BaseFilterNode):
    type = 'pad'

    def __init__(self, w=10, h=10, x='(ow-iw)/2', y='(oh-ih)/2', color='black', **kwargs):
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.color = color
        super(Pad, self).__init__(**kwargs)

    def simple_cmd_string(self):
        self._cmd = u'pad=w={w}:h={h}:x={x}:y={y}:color={color}'.format(
                w=self.w,
                h=self.h,
                x=self.x,
                y=self.y,
                color=self.color)
        return self._cmd


class GeneralUnaryFilter(BaseFilterNode):
    type = 'generic'

    def __init__(self, ffmpeg_filter_name, **kwargs):
        super(GeneralUnaryFilter, self).__init__(**kwargs)
        self.filter_kwargs = kwargs
        self.ffmpeg_filter_name = ffmpeg_filter_name

    def simple_cmd_string(self):
        self._cmd = u'{filter}{kwargs}'.format(
                filter=self.ffmpeg_filter_name,
                kwargs=u'={}'.format(
                        u':'.join((u'{}={}'.format(k, v) for k, v in
                                   self.filter_kwargs.items()))) if self.filter_kwargs else u'')
        return self._cmd


class DrawSubtitle(BaseFilterNode):
    type = 'subtitles'

    def __init__(self, subtilte_file=None, use_python_list=False,
                 font_name=None, font_folder=None, size=12, color=0xffffff,
                 back_color=0x000000, outline=0,
                 h_alignment='center', v_alignment='bottom', l_margin=20, r_margin=20, v_margin=20, **kwargs):
        self.subtitle_file = subtilte_file
        self.use_python_list = use_python_list
        self.font_name = font_name
        self.font_folder = font_folder
        self.size = size
        self.color = color
        self.back_color = back_color
        self.outline = outline
        self.h_alignment = h_alignment
        self.v_alignment = v_alignment
        self.l_margin = l_margin
        self.r_margin = r_margin
        self.v_margin = v_margin
        super(DrawSubtitle, self).__init__(**kwargs)

    def simple_cmd_string(self):
        from dayu_ffmpeg.util import get_safe_string
        h_dict = {'left': 1, 'center': 2, 'right': 3}
        v_dict = {'bottom': 0, 'top': 4, 'center': 8}

        if not self.subtitle_file:
            self._cmd = u'null'
            return self._cmd

        if self.use_python_list:
            self._generate_srt_file()

        self._cmd = u'subtitles=\'{sub_file}\'{font_folder}:' \
                    u'force_style=\'Fontsize={size},Alignment={alignment},PrimaryColour={color},' \
                    u'BackColour={bg_color},Outline={outline},' \
                    u'MarginL={lmargin},MarginR={rmargin},MarginV={vmargin}' \
                    u'{fontname}\''.format(
                sub_file=get_safe_string(self.subtitle_file),
                font_folder=u':fontsdir=\'{}\''.format(
                        get_safe_string(self.font_folder)) if self.font_folder else '',
                size=self.size,
                alignment=h_dict.get(self.h_alignment, 2) + v_dict.get(self.v_alignment, 0),
                color=self.color,
                bg_color=self.back_color,
                outline=self.outline,
                lmargin=self.l_margin,
                rmargin=self.r_margin,
                vmargin=self.v_margin,
                fontname=u',Fontname={}'.format(self.font_name) if self.font_name else '')
        return self._cmd

    def _generate_srt_file(self):
        import tempfile
        from dayu_timecode import DayuTimeCode
        temp_srt = tempfile.NamedTemporaryFile().name + '.srt'
        srt_string = u'\n\n'.join([u'{count}\n'
                                   u'{start} --> {end}\n'
                                   u'{sub}'.format(count=index + 1,
                                                   start=DayuTimeCode(max(0.0, index - 0.1)).timecode(
                                                           'SRT_TIMECODE'),
                                                   end=DayuTimeCode(index + 0.5).timecode('SRT_TIMECODE'),
                                                   sub=x.strip())
                                   for index, x in enumerate(self.subtitle_file)
                                   ])
        with open(temp_srt, 'w') as srt_file:
            srt_file.write(srt_string.encode('utf-8'))
        self.subtitle_file = temp_srt


class Concat(BaseFilterNode):
    type = 'concat'
    max_input_num = 2

    def __init__(self, number_of_inputs=2, video_streams=1, audio_streams=0, **kwargs):
        self.number_of_inputs = number_of_inputs
        self.video_streams = video_streams
        self.audio_streams = audio_streams
        self.max_input_num = number_of_inputs
        super(Concat, self).__init__(**kwargs)

    def simple_cmd_string(self):
        self._cmd = u'concat=n={n}:v={v}:a={a}'.format(n=self.number_of_inputs,
                                                       v=self.video_streams,
                                                       a=self.audio_streams)
        return self._cmd
