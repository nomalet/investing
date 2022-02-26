#!/usr/bin/env python
"""
Setup script for investor
=================================================

Call from command line as::

    python setup.py --help

to see the options available.
"""
import os

from pkg_resources import parse_requirements, parse_version
from setuptools import setup
from setuptools.config import read_configuration

config = read_configuration("setup.cfg")
# See https://pypi.org/classifiers/
classifiers = config["metadata"]["classifiers"]
classifiers.append(development_status)
kwargs = {"install_requires": install_requires, "version": __version__, "classifiers": classifiers}


if cmdclass is not None:
    kwargs["cmdclass"] = cmdclass

setup(**kwargs)
