dayu_ffmpeg
===========

|pypi| |python| |build status| |github license|

dayu_ffmpeg 是针对ffmpeg 命令行的python 封装。 ffmpeg
的功能相当强大，但是复杂的终端指令往往让人无法使用。dayu_ffmpeg
正好解决了这个问题。 用户可以使用简单的 “流”
的概念搭建自己的处理方式，同时具有下面的特点：

-  通过 >> 运算符，表示stream 的操作
-  支持filter class 的结合律
-  支持ffmpeg complex filter
-  如果用户需要使用的filter 不在默认的filter class
   中，可以自行使用GenericFilter 进行调用

例如，用户希望对一个mov 素材进行下面的操作：

-  绘制2.39 的遮幅
-  缩放到1920x1080 的尺寸
-  写入内嵌reel
-  写入内嵌timecode
-  渲染输出到prores 422 的mov

如果直接使用ffmpeg，那么终端指令会是：

.. code:: shell

   "ffmpeg" -y -i "/some/input/file.mov" -filter_complex "[0]drawbox=x=-t:y=0:w=iw+t*2:h=ih:c=black:t=(ih-(iw/2.39))/2[v0],[v0]scale=w=1920:h=1080[v1]" -map [v1] -metadata:s:v:0 reel_name=reelname -timecode 11:22:11:22 -codec:v prores_ks "/some/output/file.mov"

如果使用了dayu_ffmpeg，就会非常的直观。用户将自己的需要的操作一一写入皆可：

.. code:: python

   from dayu_ffmpeg.stream input *

   result = FFmpeg() >> \
            Overwrite() >> \
            Input('/some/input/file.mov') >> \
            Drawmask(2.39) >> \
            Scale(1920, 1080) >> \
            Writereel('reelname') >> \
            Writetimecode('11:22:11:22') >> \
            Codec(video='prores_ks') >> \
            Output('/some/output/file.mov')

dayu_ffmpeg 的基本使用
======================

常用的ffmpeg filter 都声明在stream.py
中，用户可以根据自己的需要进行调用。 常见的指令格式如下：

.. code:: python

   from dayu_ffmpeg.stream input *

   command = FFmpeg()                 # 所有指令的开始，表示调用ffmpeg
   command = command >> Overwrite()    # 表示覆盖已经存在的输出文件路径
   command = command >> Input('/some/input/file.mov') # 表示输入文件
   ...       # 继续添加各种Filter Class
   command = command >> Codec()        # 指定编码
   command = command >> Output('/some/output/file.mov')    # 指定输出文件路径

   # 由于支持运算的结合律，因此上面的指令等同于
   # command = FFmpeg() >> Overwrite() >> Input() >> ... >> Codec() >> Output()

Overlay 的使用
==============

如果想要使用logo 水印，那么就需要使用Overlay 这个filter：

.. code:: python

   logo_input = Input('logo.png')

   command = FFmpeg() >> Overwrite() >> \
             Input('background.mov') >> \
             Overlay(logo_input) >> \
             Scale(width=1280, height=720) >> \
             Output('/some/output/file.mov')

使用自定义filter
================

如果默认的filter
中不存在需要使用的filter。用户可以自己调用GeneralUnaryFilter:

.. code:: python

   command = FFmpeg() >> Overwrite() >> Input('/some/input/file.mov') >> \
             GeneralUnaryFilter('drawgrid', x=0, y=0, w=100, h=50) >> \
             Output('/custom/filter/output.mov')

查看shell 指令 以及运行
=======================

用户可以查看生成的shell 指令，或者直接运行：

.. code:: python

   # 查看将要运行的终端指令
   print command.cmd()

   # 组装filter 之后，即可运行命令
   for progress in command.run():
       try:
           print progress      # 通过yield 返回渲染进度的dict，用户可以自行实现非阻塞进度条
       except DayuFFmpegRenderError as e:
           raise               # 如果指令错误，会抛出异常

.. |pypi| image:: https://img.shields.io/badge/pypi-0.3-blue.svg
   :target: https://pypi.org/project/dayu-ffmpeg/
.. |python| image:: https://img.shields.io/badge/python-2.7-blue.svg
   :target:
.. |build status| image:: https://travis-ci.org/phenom-films/dayu_ffmpeg.svg?branch=master
   :target: https://travis-ci.org/phenom-films/dayu_ffmpeg
.. |github license| image:: https://img.shields.io/github/license/mashape/apistatus.svg
   :target: https://github.com/phenom-films/dayu_ffmpeg/blob/master/license
