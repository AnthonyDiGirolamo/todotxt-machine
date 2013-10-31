#!/usr/bin/env python
# coding=utf-8
import sys
import os
import argparse

import random
random.seed()

from todotxt import *
# import pprint
# pp = pprint.PrettyPrinter(indent=4).pprint

# Default todo.txt file
todotxt_file = '~/Dropbox/todo/todo.txt'

# Parse command line
command_line = argparse.ArgumentParser(
    description = 'Interactive terminal interface for todo.txt files.')
command_line.add_argument(
    '-f', '--file',
    help    = 'path to your todo.txt file default:{}'.format(todotxt_file),
    default = todotxt_file)
command_line.add_argument(
    '--readline-editing-mode',
    choices = ['emacs', 'vi'],
    help    = 'set readline editing-mode',
    default = 'vi')

args = command_line.parse_args()

todotxt_file_path = os.path.expanduser(args.file)

print("Opening: {}".format(todotxt_file_path))

if os.path.exists(todotxt_file_path):
    pass
else:
    directory = os.path.dirname(todotxt_file_path)
    if os.path.exists(directory):
        pass
    else:
        sys.stderr.write("ERROR: The directory: '{}' does not exist\n".format(directory))
        sys.stderr.write("\nPlease create the directory or specify a different\n"
                         "todo.txt file using the --file option.\n")
        exit(1)

try:
    with open(todotxt_file_path, "r") as todotxt_file:
        todos = todo.Todos(todotxt_file.readlines(), todotxt_file_path)
    # Other ways to read lines:
    # todotxt_file = open(todotxt_file_path, 'r') # open file
    # todotxt_file.read()        # read entire file
    # todotxt_file.readline()    # read one line at a time
    # todotxt_file.readlines()   # returns a list of strings per line
    # list(todotxt_file)
    # for line in todotxt_file:  # iterate over each line in a file
    #   print(repr(line))
    # todotxt_file.close()       # close the file
except FileNotFoundError:
    print("ERROR: unable to open {}\nUse the --file option to specify a path to your todo.txt file".format(todotxt_file_path))
    todos = todo.Todos([])

# except:
#   print("Unexpected error:", sys.exc_info()[0])
#   raise
# else:
#   todo_items = todotxt_file.readlines()
# finally:
#   print("Done")

# ipdb.set_trace()

view = screen.Screen(todos, readline_editing_mode=args.readline_editing_mode)

# signal.siginterrupt(signal.SIGWINCH, False)
# def resize_terminal(signum, frame):
#     view.refresh_screen = True
# def handle_sigint(signum, frame):
#     view.sigint = True
# signal.signal(signal.SIGWINCH, resize_terminal)
# signal.signal(signal.SIGINT, handle_sigint)
# this doesn't seem to work
# signal.siginterrupt(signal.SIGWINCH, False)
view.main_loop()

print("Writing: {}".format(todotxt_file_path))
view.todo.save()

# urwid
# class ItemWidget (urwid.WidgetWrap):

#     def __init__ (self, id, description):
#         self.id = id
#         self.content = description
#         self.item = urwid.AttrWrap(urwid.Text("{}: {}".format(self.id, description), wrap='clip'), 'body', 'selected'),

#         w = urwid.Columns(self.item)
#         self.__super.__init__(w)

#     def selectable (self):
#         return True

#     def keypress(self, size, key):
#         return key

# def main ():

#     palette = [
#         # Name of the display attribute, typically a string
#         # Foreground color and settings for 16-color (normal) mode
#         # Background color for normal mode
#         # Settings for monochrome mode (optional)
#         # Foreground color and settings for 88 and 256-color modes (optional)
#         # Background color for 88 and 256-color modes (optional)
#         ('body'     , ''            , ''           ) ,
#         ('selected' , 'light green' , 'brown' )      ,
#         ('editing'  , 'dark cyan'   , 'light green' )      ,
#         ('head'     , 'light blue'  , 'light green') ,
#     ]

#     def keystroke (input):
#         if input in ('q', 'Q'):
#             raise urwid.ExitMainLoop()

#         if input is 'enter':
#             focus = listbox.get_focus()[0]
#             view.set_header(urwid.AttrWrap(urwid.Text('selected: {}'.format(focus.content), wrap='clip'), 'head'))

#     items = []
#     for i, todo in enumerate(todos.raw_items):
#         items.append( ItemWidget(i, todo.strip()) )

#     header = urwid.AttrMap(urwid.Text('{} Todos '.format(len(todos.raw_items)), wrap='clip'), 'head')
#     listbox = urwid.ListBox(urwid.SimpleListWalker(items))
#     view = urwid.Frame(urwid.AttrWrap(listbox, 'body'), header=header)
#     loop = urwid.MainLoop(view, palette, unhandled_input=keystroke)
#     loop.run()

# if __name__ == '__main__':
#     main()

