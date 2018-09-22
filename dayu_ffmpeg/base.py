#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'
__doc__ = \
    '''
    实现对ffmpeg 终端的简化封装。
    让用户不必输入繁杂的shell 命令，只需要按照逻辑描述出执行操作，就可以自动生成shell 的命令。

    =========== 特点 ============
    * 绝大多数的操作直接使用class 对象进行实例化即可
    * 每个操作的对象之间都可以使用 + 加法操作符进行连接，并且支持加法结合律
    * 算法内部详细记录了所有操作的树状结构
    * 完整支持 -filter_complex 的结构
    * 支持用户自行输入ffmpeg 的表达式string
    * 支持多元输入的操作，例如Overlay
    * 支持每一帧，让用户任意决定burnin 的文字内容


    ========== 简单的示例 ==========
    例如，用户希望完成下面的操作：
    1. 输入图像A
    2. 对于A，缩放到1920x1080 的分辨率下
    3. 将logo 缩放50%
    4. 将缩放后的logo 叠加到A 图像上
    5. 在上面burnin 字符
    6. 设置输出编码为 ProRes
    7. 渲染到output.mov

    如果直接写ffmpeg 的shell 指令，会非常痛苦。但是使用封装后的api，就会如下：
    op = FFMPEG() + Input(a) + Fit(1920, 1080) + Overlay( (Input(logo) + Scale(scale_x=0.5)), 100, 100 ) \
         + DrawText('message') + Codec() +  Output('output.mov')
    print op.cmd()

    '''

import collections
import os

from error import *

# ffmpeg 内部指令stack 的分布，用户无需操心
FFMPEG_CLASSIFY = {'global': [],
                   'input' : [],
                   'filter': [],
                   'codec' : [],
                   'output': []}


class FFmpegBaseStream(object):
    '''
    所有ffmpeg 操作的基类。
    这里设计的理念是将所有的操作定义为"stream"。每个Stream 都会记录如下的信息：
    * 自己的上游 stream
    * 自己的下游 stream
    * 自己的操作内容

    利用这些信息，算法会根据构建出的操作树，拼接出最终的shell 指令
    '''
    _input_count = 1
    _name = ''
    _priority = -1

    def __init__(self):
        super(FFmpegBaseStream, self).__init__()
        self._inputs = []
        self._outputs = []
        self._value = u''
        self._stream_in = u''
        self._stream_out = u''
        self._begin = None
        self._is_combine_op = False
        self.combine_op = []
        for x in range(self.__class__._input_count):
            self._inputs.append(None)

    def validate(self, stream, index):
        '''
        对连接的stream 进行验证。
        :param stream: 任何 Stream class 的对象
        :param index: 是否可以接在对应位置上
        :return:
        '''
        return index < self.__class__._input_count and isinstance(stream, FFmpegBaseStream)

    def can_set_inputs(self):
        return self.__class__._input_count > 0

    def set_input(self, stream, index):
        '''
        连接上游stream 的方法。
        :param stream: 上游Stream 对象
        :param index: int，表示需要连接到自身的某个位置上
        :return: True 表示连接成功，False 表示失败
        '''
        if self.can_set_inputs():
            if self.validate(stream, index):
                self._inputs[index] = stream
                return True

        return False

    def request(self):
        '''
        向上游stream 的请求函数。
        用来从下往上的遍历整个操作树
        :return: 自身连接的所有上游stream
        '''
        return self._inputs

    def cmd(self):
        '''
        生成shell 指令的函数。
        :return: string。内容是可以直接在终端中使用的命令行。
        '''
        reset_cmd()
        request_queue = collections.deque()
        request_queue.append(self)

        # 使用deque 模拟深度优先递归，可以解决Python 最大嵌套深度的错误
        # 这里首先是从下向上的遍历整个操作树，并把对应类型的stream 进行分类
        while request_queue:
            current = request_queue.popleft()
            if current:
                classify(current)
                request_queue.extendleft(current.request()[::-1])

        # 将所有stream 分类完成后，开始从上往下的遍历操作树。
        # 目的是生成ffmpeg 的stream 标识符
        down_stream_flag(FFMPEG_CLASSIFY['input'])

        # 最终，拼接所有的操作，返回shell 指令
        return generate_cmd()

    def __rshift__(self, other):
        '''
        重载加法操作符。
        在加法的同时，后台完成了两个stream 之间的正向、反向连接
        并且实现了 加法结合律，使得复合型stream 可以轻松的实现。
        :param other: ffmpeg Stream 对象
        :return: ffmpeg Stream 对象
        '''

        def single_add(left, right):
            if right._begin is None:
                right.set_input(left, 0)
                left._outputs.append(right)
            else:
                right._begin.set_input(left, 0)
                left._outputs.append(right._begin)
            right._begin = left._begin if left._begin else left
            return right

        if not isinstance(other, FFmpegBaseStream):
            raise DayuFFmpegValueError

        if not self.__class__._priority <= other.__class__._priority:
            raise DayuFFmpegPriorityError

        # 处理复合型stream
        if other._is_combine_op:
            temp = self
            for x in other.combine_op:
                temp = single_add(temp, x)
            return temp
        # 处理单一操作Stream
        else:
            return single_add(self, other)

    def __str__(self):
        '''
        需要继承的class 自己实现。
        这里完成的就是生成ffmpeg 对应操作的string
        :return: String
        '''
        raise NotImplementedError

    def run(self):
        import subprocess
        import re
        import time

        self.progress = {'render_frame': None, 'render_fps': None, 'render_speed': None, 'elapse_time': None}
        frame_regex = re.compile(r'^frame=\s*?(\d+)')
        fps_regex = re.compile(r'.*?fps=\s*?(\d+)')
        time_regex = re.compile(r'.*?time=\s*?(.*?)\s')
        speed_regex = re.compile(r'.*?speed=\s*?(.*?)x')

        start_time = time.time()
        _cmd = self.cmd()
        print _cmd
        shell_cmd = subprocess.Popen(_cmd,
                                     shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     universal_newlines=True)

        while True:
            if shell_cmd.poll() is not None:
                break

            message = shell_cmd.stderr.readline()
            self.progress['elapse_time'] = round(time.time() - start_time, 2)

            frame_match = frame_regex.match(message)
            fps_match = fps_regex.match(message)
            time_match = time_regex.match(message)
            speed_match = speed_regex.match(message)
            if frame_match and fps_match and time_regex and speed_regex:
                self.progress['render_frame'] = float(frame_match.group(1))
                self.progress['render_fps'] = float(fps_match.group(1))
                self.progress['render_speed'] = float(speed_match.group(1))
                yield self.progress

        if shell_cmd.returncode != 0:
            print shell_cmd.stderr.readlines()
            raise DayuFFmpegRenderError


class GlobalStream(FFmpegBaseStream):
    '''
    ffmpeg 中的全局类型Stream 的基类
    '''
    _priority = 10
    _input_count = 1


class InputStream(FFmpegBaseStream):
    '''
    ffmpeg 中输入素材类型 stream 的基类
    '''
    _priority = 20
    _input_count = 1


class FilterStream(FFmpegBaseStream):
    '''
    filter 的基类
    '''
    _priority = 30


class UnaryFilterStream(FilterStream):
    '''
    一元操作filter 的基类（只有一个输入）
    '''
    _input_count = 1


class BinaryFilterStream(FilterStream):
    '''
    二元操作filter 的基类（有两个输入）
    '''
    _input_count = 2
    _priority = 30


class CodecStream(FFmpegBaseStream):
    '''
    编码设置类型 Stream 的基类
    '''
    _input_count = 1
    _priority = 40


class OutputStream(FFmpegBaseStream):
    '''
    输出文件类型Stream 的基类
    '''
    _input_count = 1
    _priority = 50


def reset_cmd():
    '''
    清空内部用来记录ffmpeg 指令的分类情况。用户不应该直接调用这个函数！
    :return:
    '''
    for key in FFMPEG_CLASSIFY:
        FFMPEG_CLASSIFY[key] = []


def classify(obj):
    '''
    对stream 进行分类。用户不应该直接调用这个函数！
    :param obj: Stream 对象
    :return: a
    '''
    if isinstance(obj, GlobalStream):
        FFMPEG_CLASSIFY['global'].insert(0, obj)
        return
    if isinstance(obj, InputStream):
        FFMPEG_CLASSIFY['input'].insert(0, obj)
        return
    if isinstance(obj, FilterStream):
        FFMPEG_CLASSIFY['filter'].insert(0, obj)
        return
    if isinstance(obj, CodecStream):
        FFMPEG_CLASSIFY['codec'].insert(0, obj)
        return
    if isinstance(obj, OutputStream):
        FFMPEG_CLASSIFY['output'].insert(0, obj)
        return


def down_stream_flag(stream_list):
    '''
    从上而下的遍历操作树。目的是给每一个操作生成stream 的输入、输出标识
    方便在生成shell 指令的时候得到正确的图像操作堆栈关系。
    :param stream_list: list of stream 操作
    :return:
    '''
    # 利用链表，实现模拟的深度优先遍历，可以避免出现超过python 最大递归深度的错误。
    down_queue = collections.deque(stream_list)
    while down_queue:
        x = down_queue.popleft()
        if isinstance(x, InputStream):
            x._stream_out = '[{}]'.format(FFMPEG_CLASSIFY['input'].index(x))
        elif isinstance(x, FilterStream):
            x._stream_out = '[v{}]'.format(FFMPEG_CLASSIFY['filter'].index(x))
        for y in x._outputs:
            y._stream_in = x._stream_out

        down_queue.extendleft(x._outputs)


def generate_cmd():
    '''
    实际拼接所有的操作指令，生成最终的shell 指令。
    :return:
    '''
    global_cmd = u' '.join((x.__str__() for x in FFMPEG_CLASSIFY['global']))
    input_cmd = u' '.join((x.__str__() for x in FFMPEG_CLASSIFY['input']))
    if FFMPEG_CLASSIFY['filter']:
        filter_cmd = '-filter_complex \"{filters}\" -map [v{final}]'.format(
                filters=','.join(map(str, FFMPEG_CLASSIFY['filter'])),
                final=len(FFMPEG_CLASSIFY['filter']) - 1)
    else:
        filter_cmd = ''
    codec_cmd = u' '.join((x.__str__() for x in FFMPEG_CLASSIFY['codec']))
    input_in_list = [x.trim_in for x in FFMPEG_CLASSIFY['input'] if x.trim_in]
    input_out_list = [x.trim_out for x in FFMPEG_CLASSIFY['input'] if x.trim_out]
    output_in = min(input_in_list if input_in_list else [0])
    output_out = max(input_out_list if input_out_list else [None])

    if output_out:
        for x in FFMPEG_CLASSIFY['output']:
            x.duration = (output_out - output_in) / x.fps

    output_cmd = u' '.join((x.__str__() for x in FFMPEG_CLASSIFY['output']))
    return u' '.join((global_cmd, input_cmd, filter_cmd, codec_cmd, output_cmd))
