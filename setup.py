#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.md').read()

requirements = open('requirements.txt').read().split('\n')

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='larus',
    version='0.1.0',
    description='Larus is a simplified Gunicorn clone',
    long_description=readme,
    author='wong2',
    author_email='wonderfuly@gmail.com',
    url='https://github.com/wong2/larus',
    packages=[
        'larus',
    ],
    package_dir={'larus':
                 'larus'},
    include_package_data=True,
    install_requires=requirements,
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
