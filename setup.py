#!/usr/bin/env python3
from setuptools import setup, find_packages
setup(
    name='quikey',
    version='0.0.1',
    packages=find_packages(),
    author='Robert Bost',
    entry_points = {
        'console_scripts': ['quikey=quikey.quikey:cli']
    },
    description='A keyboard macro tool.',
    url='https://github.com/bostrt/quikey',
    install_requires=[
        'click', 
        'colored',
        'configparser',
        'inotify-simple',
        'peewee',
        'pynput',
        'terminaltables',
        'xdg',
        'humanize'
        ]
)
