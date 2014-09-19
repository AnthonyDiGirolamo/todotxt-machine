# -*- coding: utf-8 -*-

"""
todotxt-machine
===============

An interactive terminal based todo.txt file editor with an
interface similar to [mutt](http://www.mutt.org/).

Requirements
------------

Python 2.7 or Python 3.3 with readline support.

Documentation
-------------

The documentation for ``todotxt-machine`` is `available on github <https://github.com/AnthonyDiGirolamo/todotxt-machine>`_.

License
-------

``todotxt-machine`` is licensed under a GPLv3 license, see ``LICENSE`` for details.
"""

from setuptools import setup, find_packages
from sys import version_info

from setuptools.command.test import test as TestCommand
import sys

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

import todotxt_machine

NAME = "todotxt-machine"

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = __doc__


setup(name=NAME,
      version=todotxt_machine.version,
      author="Anthony DiGirolamo",
      author_email="anthony.digirolamo@gmail.com",
      url="https://github.com/AnthonyDiGirolamo/todotxt-machine",
      description="An interactive terminal based todo.txt file editor with an interface similar to mutt",
      long_description=long_description,
      keywords="todotxt, todo.txt, todo, terminal, urwid, curses, console",
      packages=find_packages(exclude=["todotxt_machine/test*"]),
      include_package_data=True,
      entry_points={
          'console_scripts':
            ['todotxt-machine = todotxt_machine.cli:main']
      },
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console :: Curses",
          "Intended Audience :: End Users/Desktop",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Natural Language :: English",
          "Operating System :: POSIX :: Linux",
          "Operating System :: MacOS",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.3",
          "Topic :: Office/Business :: Scheduling",
      ],
      install_requires=['setuptools', 'docopt>=0.6.2', 'urwid>=1.2.1'],
      tests_require=['pytest'],
      cmdclass = {'test': PyTest},
      )
