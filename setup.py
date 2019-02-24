#!/usr/bin/env python3
from setuptools import setup, find_packages

VERSION='0.0.2'

setup(
    name='quikey',
    version=VERSION,
    packages=find_packages(),
    author='bostrt',
    entry_points = {
        'console_scripts': [
            'quikey=quikey.quikey:cli',
            'qkdaemon=quikey.qkdaemon:cli'
            ]
    },
    description='A keyboard macro tool.',
    license='',
    url='https://github.com/bostrt/quikey',
    install_requires=[
        'click', 
        'colored',
        'python-daemon',
        'inotify-simple',
        'tinydb',
        'pynput',
        'terminaltables',
        'xdg',
        'humanize'
        ]
)
