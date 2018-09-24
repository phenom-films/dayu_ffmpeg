#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

from setuptools import setup

setup(
        name='dayu_ffmpeg',
        version='0.3',
        packages=['dayu_ffmpeg'],
        url='https://github.com/phenom-films/dayu_ffmpeg',
        license='MIT',
        author='andyguo',
        author_email='andyguo@phenom-films.com',
        description='FFmpeg python wrapper with common filter built in.',
        long_description=open('README.rst').read(),
        classifiers=[
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: Implementation',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
        ],
)
