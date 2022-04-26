#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 21:08:25 2022

@author: duverne, IJClab, Orsay, duverne@protonmail.com
"""

from setuptools import setup, find_packages

requirements = ['astropy>=4.3.1',
                'reproject>=0.7.2',
                'Bottleneck>=1.3.2',
                'numpy>=1.21.2',
                'esutil==0.6.8',
                'tqdm',
                'regions>=0.5']

setup(
    author="Sergey Karpov, Pierre-Alexandre Duverne",
    author_email=['duverne@protonmail.com', 'karpov.sv@gmail.com'],
    python_requires='>=3.5',
    description="A simple tool for stacking astronomical images.",
    entry_points={'console_scripts': ['std_stack=grandma_stack.stacking:main']},
    install_requires=requirements,
    include_package_data=True,
    name='grandma-stack',
    packages=find_packages(include=['grandma-stack']),#, 'grandma-stack.*']),
    url='https://github.com/PAduverne/grandma-stack',
    version='0.1.0')