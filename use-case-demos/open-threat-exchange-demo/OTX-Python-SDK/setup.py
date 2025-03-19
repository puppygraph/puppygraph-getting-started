#!/usr/bin/env python

from setuptools import setup

setup(
    name='OTXv2',
    version='1.5.12+mytest',
    description='AlienVault OTX API (Modified)',
    author='AlienVault Team (modified by Sa Wang)',
    author_email='sa@puppygraph.com',
    py_modules=['OTXv2', 'IndicatorTypes','patch_pulse'],
    install_requires=['requests', 'python-dateutil', 'pytz']
)
