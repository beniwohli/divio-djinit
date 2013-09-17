#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
from djinit import __version__


CLASSIFIERS = [
]

setup(
    name='djinit',
    version=__version__,
    description="Divio's DjangoCMS Initializer",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    author='Kim Thoenen',
    author_email='kim@smuzey.ch',
    url='https://github.com/divio/divio-djinit',
    packages=find_packages(),
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'djinit = djinit:main',
        ]
    },
)
