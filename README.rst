dayu_ffmpeg
===========

|pypi| |python| |build status| |github license|

dayu_ffmpeg 是针对ffmpeg 命令行的python 封装。 ffmpeg
的功能相当强大，但是复杂的终端指令往往让人无法使用。dayu_ffmpeg
正好解决了这个问题。 用户可以使用简单的 “流”
的概念搭建自己的处理方式，同时具有下面的特点：

-  通过 >> 运算符，表示stream 的操作
-  拥有ad-hoc 和network 两种操作模式
-  支持ffmpeg complex filter
-  如果用户需要使用的filter 不在默认的filter class 中，可以自行扩展
-  可以将Root Node 保存为ffscipt 的json
   格式，方便保存硬盘文件或者是网络通信

ad-hoc 模式
===========

在ad-hoc 模式下，用户可以直接使用节点进行串行操作。
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

   from dayu_ffmpeg input *

   result = Input('/some/input/file.mov') >> \
            Drawmask(2.39) >> \
            Scale(1920, 1080) >> \
            Writereel('reelname') >> \
            Writetimecode('11:22:11:22') >> \
            Codec(video='prores_ks') >> \
            Output('/some/output/file.mov')

需要注意的是，在ad-hoc 模式下，只能够支持串行的操作。
也就是说所有的节点都只能拥有一个输入和一个输出。
如果想要使用更加复杂的转码，请使用network 模式

network 模式
============

netowrk 模式会比ad-hoc
复杂一点，但是可以实现更加复杂的转码结构。并且一旦TD 写好了一个network，
那么后续的用户在使用上就非常的简单，相当于提供了一个 “转码模板”。

.. code:: python

   from dayu_ffmpeg import *

   class TranscodeTemplate(RootNode):
       def prepare(self):
           # 用户只需要重载prepare() 函数，在这里组织好网络结构
           # 留好InputHolder 或者OutputHolder 作为 "接口"
           ih1 = self.create_node(InputHolder)
           i2 = self.create_node(Input('some_logo.png'))

           cf = self.create_node(ComplexFilterGroup)
           ih2 = cf.create_node(InputHolder)
           ih3 = cf.create_node(InputHolder)
           cf.set_input(ih1, 0)
           cf.set_input(i2, 1)
           over = cf.create_node(Overlay)
           over.set_input(ih2, 0)
           over.set_input(ih3, 1)
           fit = cf.create_node(Fit())
           fit.set_input(over)
           oh1 = cf.create_node(OutputHolder)
           oh1.set_input(fit)

           oh2 = self.create_node(OutputHolder)
           oh2.set_input(cf)


   if __name__ == '__main__':
       # 实例化转码的网络
       template_root = TranscodeTemplate(name='overlay logo, then fit in HD, finally export to mov')

       # 创建输入、输出
       input1 = Input('some_input_file.mov')
       output1 = Output('some_output_file.mov')

       # 用户直接调用，就完成了整个转码，相当于调用"模板"
       network_mode_cmd = template_root(input_list=[input1], output_list=[output1])
       print network_mode_cmd.cmd()

使用自定义filter
================

如果默认的filter
中不存在需要使用的filter。用户可以有下面的几种方法自行扩展:

-  调用GeneralUnaryFilter
-  继承BaseFilterNode class，自行实现
-  继承BasePackedFilterNode, 将多种filter 进行打包，形成新的一个filter

调用GeneralUnaryFilter：

.. code:: python

   command = Input('/some/input/file.mov') >> \
             GeneralUnaryFilter('drawgrid', x=0, y=0, w=100, h=50) >> \
             Output('/custom/filter/output.mov')

继承BaseFilterNode class，自行实现：

.. code:: python

   class Null(BaseFilterNode):
       # 设置特定的type，要保证唯一性
       type = 'some_ffmpeg_filter_name'

       # 重载init，实现自己的参数
       def __init__(self, **kwargs):
           super(Null, self).__init__(**kwargs)

       # 重载 simple_cmd_string，返回对应的ffmpeg 指令string
       def simple_cmd_string(self):
           self._cmd = u'null'
           return self._cmd

继承BasePackedFilterNode, 将多种filter 进行打包，形成新的一个filter。
可以参看 Fit 这个class 的实现方式。

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
       except Exception as e:
           raise               # 如果指令错误，会抛出异常

ffscript 的保存和读取
=====================

ffscript 是dayu_ffmpeg 对于network 结构的一种json
表现形式，可以认为是“工程文件”。 如果想要把组成的network
保存到硬盘上，或是通过网络通信进行传递，就会使用到。

保存ffscript：

.. code:: python

   from dayu_ffmpeg.ffscript import save_script, open_script

   # 保存
   save_script(netowrk_node_instance, '/some/script/path.json')

   # 读取
   transcode_template = open_script('/some/script/path.json')

.. |pypi| image:: https://img.shields.io/badge/pypi-0.5-blue.svg
   :target: https://pypi.org/project/dayu-ffmpeg/
.. |python| image:: https://img.shields.io/badge/python-2.7-blue.svg
   :target: 
.. |build status| image:: https://travis-ci.org/phenom-films/dayu_ffmpeg.svg?branch=master
   :target: https://travis-ci.org/phenom-films/dayu_ffmpeg
.. |github license| image:: https://img.shields.io/github/license/mashape/apistatus.svg
   :target: https://github.com/phenom-films/dayu_ffmpeg/blob/master/license
