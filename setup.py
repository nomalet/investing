#!/usr/bin/env python
"""
Setup script for investing
=================================================

Call from command line as::

    python setup.py --help

to see the options available.
"""
from setuptools import setup
from setuptools.config import read_configuration

config = read_configuration("setup.cfg")
kwargs = config["metadata"]

setup(**kwargs)
