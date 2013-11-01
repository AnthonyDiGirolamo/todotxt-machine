#!/usr/bin/env python
# coding=utf-8
import sys
import os
import argparse
import random

from todotxt_machine.todo import Todos
from todotxt_machine.screen import Screen

def main():
    random.seed()

    # Default todo.txt file
    todotxt_file = '~/Dropbox/todo/todo.txt'

    # Parse command line
    command_line = argparse.ArgumentParser(
        description = 'Interactive terminal interface for todo.txt files.')
    command_line.add_argument(
        '-f', '--file',
        help    = 'path to your todo.txt file default:{0}'.format(todotxt_file),
        default = todotxt_file)
    command_line.add_argument(
        '--readline-editing-mode',
        choices = ['emacs', 'vi'],
        help    = 'set readline editing-mode',
        default = 'vi')

    args = command_line.parse_args()

    todotxt_file_path = os.path.expanduser(args.file)

    print("Opening: {0}".format(todotxt_file_path))

    if os.path.exists(todotxt_file_path):
        pass
    else:
        directory = os.path.dirname(os.path.realpath(todotxt_file_path))
        if os.path.exists(directory):
            pass
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
        todos = todo.Todos([], todotxt_file_path)

    view = Screen(todos, readline_editing_mode=args.readline_editing_mode)

    view.main_loop()

    print("Writing: {0}".format(todotxt_file_path))
    view.todo.save()
    exit(0)

if __name__ == '__main__':
    main()

