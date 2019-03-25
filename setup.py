#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from setuptools import setup

setup(
        name='dayu_ffmpeg',
        version='0.5.1',
        packages=['dayu_ffmpeg', 'dayu_ffmpeg.network', 'dayu_ffmpeg.errors', 'dayu_ffmpeg.network.edge',
                  'dayu_ffmpeg.network.knob', 'dayu_ffmpeg.network.node'],
        include_package_data=True,
        url='https://github.com/phenom-films/dayu_ffmpeg',
        license='MIT',
        author='andyguo',
        author_email='andyguo@phenom-films.com',
        description='FFmpeg python wrapper for human, with common filters built in.',
        long_description=open('README.rst').read(),
        classifiers=[
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: Implementation',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
        ],
)
