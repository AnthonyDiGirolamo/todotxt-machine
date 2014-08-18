#!/usr/bin/env python
# coding=utf-8
import sys
import os
import argparse
import ConfigParser
import random

from todotxt_machine.todo import Todos
from todotxt_machine.screen import Screen

def main():
    random.seed()

    # Parse command line
    command_line = argparse.ArgumentParser(
        description = 'Interactive terminal interface for todo.txt files.')
    command_line.add_argument(
        '-f', '--file',
        help    = 'path to your todo.txt file. default: read from config file',
        default = None)
    command_line.add_argument(
        '--readline-editing-mode',
        choices = ['emacs', 'vi'],
        help    = 'set readline editing-mode',
        default = 'vi')
    command_line.add_argument(
        '-c', '--config',
        help    = 'path to your todotxt-machine configuraton file default:$(default)s',
        default = '~/.todotxt-machinerc'
    )

    args = command_line.parse_args()
    todotxt_file = args.file

    # Parse config file
    cfg = ConfigParser.ConfigParser()
    cfg.read(os.path.expanduser(args.config))
    if todotxt_file is None and cfg.has_section('files') and cfg.has_option('files', 'todo'):
        todotxt_file = cfg.get('files', 'todo')

    if todotxt_file is None:
        sys.stderr.write("ERROR: No todo file specified. Either specify one as command line argument or set it in"
                         "your configuartion directory!")
        exit(1)

    # expand enviroment variables and username, get canonical path
    todotxt_file_path = os.path.realpath(os.path.expanduser(os.path.expandvars(todotxt_file)))

    print("Opening: {0}".format(todotxt_file_path))

    if os.path.isdir(todotxt_file_path):
        sys.stderr.write("ERROR: Specified todo file is a directory.")
        exit(1)

    if not os.path.exists(todotxt_file_path):
        directory = os.path.dirname(todotxt_file_path)
        if os.path.isdir(directory):
            # directory exists, but no todo.txt file - create an empty one
            open(todotxt_file_path, 'a').close()
        else:
            sys.stderr.write("ERROR: The directory: '{0}' does not exist\n".format(directory))
            sys.stderr.write("\nPlease create the directory or specify a different\n"
                             "todo.txt file using the --file option.\n")
            exit(1)

    try:
        with open(todotxt_file_path, "r") as todotxt_file:
            todos = Todos(todotxt_file.readlines(), todotxt_file_path)
    except:
        print("ERROR: unable to open {0}\nUse the --file option to specify a path to your todo.txt file".format(todotxt_file_path))
        todos = Todos([], todotxt_file_path)

    view = Screen(todos, readline_editing_mode=args.readline_editing_mode)

    view.main_loop()

    print("Writing: {0}".format(todotxt_file_path))
    view.todo.save()
    exit(0)

if __name__ == '__main__':
    main()

