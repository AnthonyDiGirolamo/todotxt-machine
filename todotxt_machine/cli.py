#!/usr/bin/env python
# coding=utf-8

"""todotxt-machine

Usage:
  todotxt-machine
  todotxt-machine [--file FILE] [--config FILE] [--readline-editing-mode=(vi|emacs)]
  todotxt-machine (-h | --help)
  todotxt-machine --version

Options:
  -f FILE --file=FILE                 Path to your todo.txt file
  -c FILE --config=FILE               Path to your todotxt-machine configuraton file [default: ~/.todotxt-machinerc]
  --readline-editing-mode=(vi|emacs)  Set readline editing mode [default: vi]
  -h --help                           Show this screen.
  --version                           Show version.
"""

import sys
import os
import argparse
import random

# Import the correct version of configparser
if sys.version_info[0] >= 3:
    import configparser
    config_parser_module = configparser
elif sys.version_info[0] < 3:
    import ConfigParser
    config_parser_module = ConfigParser

from docopt import docopt

import todotxt_machine
from todotxt_machine.todo import Todos
from todotxt_machine.screen import Screen
from todotxt_machine.urwid_ui import UrwidUI

def exit_with_error(message):
    sys.stderr.write(message.strip(' \n')+'\n')
    print(__doc__.split('\n\n')[1])
    exit(1)

def main():
    random.seed()

    # Parse command line
    arguments = docopt(__doc__, version=todotxt_machine.version)

    if arguments['--readline-editing-mode'] not in ['vi', 'emacs']:
        exit_with_error("--readline-editing-mode must be set to either vi or emacs\n")

    todotxt_file = arguments['--file']

    # Parse config file
    cfg = config_parser_module.ConfigParser()
    cfg.read(os.path.expanduser(arguments['--config']))

    if todotxt_file is None and cfg.has_section('files') and cfg.has_option('files', 'todo'):
        todotxt_file = cfg.get('files', 'todo')

    if todotxt_file is None:
        exit_with_error("ERROR: No todo file specified. Either specify one using the --file option or set it in your configuration file ({0}).".format(arguments['--config']))

    # expand enviroment variables and username, get canonical path
    todotxt_file_path = os.path.realpath(os.path.expanduser(os.path.expandvars(todotxt_file)))

    print("Opening: {0}".format(todotxt_file_path))

    if os.path.isdir(todotxt_file_path):
        exit_with_error("ERROR: Specified todo file is a directory.")

    if not os.path.exists(todotxt_file_path):
        directory = os.path.dirname(todotxt_file_path)
        if os.path.isdir(directory):
            # directory exists, but no todo.txt file - create an empty one
            open(todotxt_file_path, 'a').close()
        else:
            exit_with_error("ERROR: The directory: '{0}' does not exist\n\nPlease create the directory or specify a different\ntodo.txt file using the --file option.".format(directory))

    try:
        with open(todotxt_file_path, "r") as todotxt_file:
            todos = Todos(todotxt_file.readlines(), todotxt_file_path)
    except:
        print("ERROR: unable to open {0}\nUse the --file option to specify a path to your todo.txt file\n".format(todotxt_file_path))
        todos = Todos([], todotxt_file_path)

    # view = Screen(todos, readline_editing_mode=arguments['--readline-editing-mode'])
    # view.main_loop()

    view = UrwidUI(todos)
    view.main()

    print("Writing: {0}".format(todotxt_file_path))
    view.todo.save()
    exit(0)

if __name__ == '__main__':
    main()
