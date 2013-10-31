# -*- coding: utf-8 -*-

"""
todotxt-machine
===============

An interactive terminal based todo.txt file editor with an
interface similar to [mutt](http://www.mutt.org/).

Requirements
------------

Python 2.7.5 or Python 3.3.2 with readline support.

Documentation
-------------

The documentation for ``todotxt-machine`` is `available on github <https://github.com/AnthonyDiGirolamo/todotxt-machine>`_.

License
-------

``todotxt-machine`` is licensed under a GPLv3 license, see ``LICENSE`` for details.
"""

from setuptools import setup, find_packages
from sys import version_info

import todotxt_machine

NAME = "todotxt-machine"

REQUIREMENTS = [
    # "argparse",
    # "fcntl",
    # "os",
    # "pprint",
    # "random",
    # "re",
    # "readline",
    # "select",
    # "struct",
    # "subprocess",
    # "sys",
    # "termios",
    # "textwrap",
    # "time",
    # "tty",
]

TEST_REQUIREMENTS = list(REQUIREMENTS)
TEST_REQUIREMENTS.extend(["pytest"])

try:
    long_description = open("README.md").read()
except IOError:
    long_description = __doc__


setup(name=NAME,
      version=todotxt_machine.version,
      author="Anthony DiGirolamo",
      author_email="anthony.digirolamo@gmail.com",
      url="https://github.com/AnthonyDiGirolamo/todotxt-machine",
      description="An interactive terminal based todo.txt file editor with an interface similar to mutt",
      long_description=long_description,
      keywords="todotxt, todo.txt, todo, terminal, curses, console",
      packages=find_packages(exclude=["todotxt_machine/test*"]),
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
          "Topic :: Communications",
      ],
      install_requires=REQUIREMENTS,
      tests_require=TEST_REQUIREMENTS)

