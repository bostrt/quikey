#!/usr/bin/env python3
from setuptools import setup, find_packages
from quikey.version import __version__

# NOTE: Update the __version__ flag in quikey/version.py for release.

setup(
    name='quikey',
    version=__version__,
    packages=find_packages(),
    author='bostrt',
    entry_points = {
        'console_scripts': [
            'qk=quikey.quikey:cli',
            'quikey-daemon=quikey.qkdaemon:cli'
            ]
    },
    description='A keyboard macro tool.',
    license='',
    url='https://github.com/bostrt/quikey',
    install_requires=[
        'click', 
        'python-daemon',
        'inotify-simple',
        'tinydb',
        'pynput',
        'terminaltables',
        'pyxdg',
        'humanize',
        'pick',
        'filelock'
        ]
)
