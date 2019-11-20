#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'yangzhuo'


from dayu_ffmpeg import *


class PhenomSlate(RootNode):
    def prepare(self):
        main_input_holder = self.create_node(InputHolder)
        input_logo = self.create_node(Input(r"f:\workspace\DaYu\bin\ffmpeg\static\phenom_logo.png"))

        complex_filter = self.create_node(ComplexFilterGroup)
        cf_holder_2 = complex_filter.create_node(InputHolder)
        cf_holder_3 = complex_filter.create_node(InputHolder)
        complex_filter.set_input(main_input_holder, 0)
        complex_filter.set_input(input_logo, 1)

        # 将主分支输入源 与 logo 相互merge
        over_node = complex_filter.create_node(Overlay)
        over_node.set_input(cf_holder_2, 0)
        over_node.set_input(cf_holder_3, 1)

        fit_node = complex_filter.create_node(Fit(width=2048, height=858))
        fit_node.set_input(over_node)

        mask_node = complex_filter.create_node(DrawMask(float(2048) / 858))
        mask_node.set_input(fit_node)
        version_node = complex_filter.create_node(DrawText(text='this is ss_0010_v0001', x='w*0.05', y='24', size=22,
                                                           font='f:/workspace/DaYu/bin/ffmpeg/static/tahoma.ttf'))
        version_node.set_input(mask_node)

        user_node = complex_filter.create_node(DrawText(text='yangzhuo', x='w*0.85-tw', y='24', size=22,
                                                        font='test.ttf'))
        user_node.set_input(version_node)
        date_time_node = complex_filter.create_node(DrawDate(x='w*0.985-tw', y='24',
                                                             size=22, date_format='%Y-%m-%d %H:%M:%S',
                                                             font='test'))
        date_time_node.set_input(user_node)

        time_code_node = complex_filter.create_node(DrawTimecode(x=2048/2 + 10, y=858-24, size=22, color='white'))
        time_code_node.set_input(date_time_node)

        # complex node 输出
        cf_holder_out = complex_filter.create_node(OutputHolder)
        cf_holder_out.set_input(time_code_node)

        map_node = self.create_node(Map, node=complex_filter)
        map_node.set_input(complex_filter)

        codec_node = self.create_node(Codec)
        codec_node.set_input(map_node)

        custom_map = self.create_node(Map, node=input_logo, channel='a')
        custom_map.set_input(codec_node)

        codec_copy_node = self.create_node(Codec, audio='copy', video=None)
        codec_copy_node.set_input(custom_map)

        # 主分支输出
        main_output_holder = self.create_node(OutputHolder)
        main_output_holder.set_input(codec_copy_node)


if __name__ == '__main__':
    template_root = PhenomSlate(name='overlay logo, then fit in HD, finally export to mov')

    input1 = Input('d:/aa.mov')
    output1 = Output('d:/v0015.mov')

    network_mode_cmd = template_root(input_list=[input1], output_list=[output1])
    print network_mode_cmd.cmd()
