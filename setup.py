#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='larus',
    version='0.2.1',
    description='Larus is a simplified Gunicorn clone',
    author='wong2',
    author_email='wonderfuly@gmail.com',
    url='https://github.com/wong2/larus',
    packages=[
        'larus',
    ],
    package_dir={'larus':
                 'larus'},
    include_package_data=True,
    install_requires=[
        'http-parser',
        'click',
    ],
    license="BSD",
    zip_safe=False,
    keywords='larus,gunicorn,wsgi',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
        'console_scripts': [
            'larus=larus.scripts.manage:main',
        ]
    }
)
