#!/usr/bin/env python
import os
# import sys
# import signal
import urwid

from todotxt import *

# import pprint
# pp = pprint.PrettyPrinter(indent=2).pprint

todotxt_file_path = os.path.expanduser("~/Dropbox/todo/todobackup.txt")
# todotxt_file_path = os.path.expanduser("~/Documents/Dropbox/todo/todobackup.txt")

# if os.path.exists(todotxt_file_path):
#   print("FOUND: ", todotxt_file_path)
# else:
#   print("WARNING: unable to open", repr(todotxt_file_path))
#   exit(1)

try:
    with open(todotxt_file_path, "r") as todotxt_file:
        todos = todo.Todos(todotxt_file.readlines())
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
    print("WARNING: unable to open", repr(todotxt_file_path))
    exit(1)
# except:
#   print("Unexpected error:", sys.exc_info()[0])
#   raise
# else:
#   todo_items = todotxt_file.readlines()
# finally:
#   print("Done")

# view = screen.Screen(todos.raw_items)
# def resize_terminal(signum, frame):
#     view.refresh_screen = True
# def handle_sigint(signum, frame):
#     view.sigint = True
# signal.signal(signal.SIGWINCH, resize_terminal)
# signal.signal(signal.SIGINT, handle_sigint)
# # this doesn't seem to work
# signal.siginterrupt(signal.SIGWINCH, False)
# view.main_loop()

import random

class ItemWidget (urwid.WidgetWrap):

    def __init__ (self, id, description):
        self.id = id
        self.content = 'item %s: %s...' % (str(id), description[:25])
        self.item = [
            ('fixed', 15, urwid.Padding(urwid.AttrWrap(
                urwid.Text('item %s' % str(id)), 'body', 'focus'), left=2)),
            urwid.AttrWrap(urwid.Text('%s' % description), 'body', 'focus'),
        ]
        w = urwid.Columns(self.item)
        self.__super.__init__(w)

    def selectable (self):
        return True

    def keypress(self, size, key):
        return key

def main ():

    palette = [
        ('body','dark cyan', '', 'standout'),
        ('focus','dark red', '', 'standout'),
        ('head','light red', 'black'),
        ]

    lorem = [
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
        'Sed sollicitudin, nulla id viverra pulvinar.',
        'Cras a magna sit amet felis fringilla lobortis.',
    ]

    def keystroke (input):
        if input in ('q', 'Q'):
            raise urwid.ExitMainLoop()

        if input is 'enter':
            focus = listbox.get_focus()[0].content
            view.set_header(urwid.AttrWrap(urwid.Text(
                'selected: %s' % str(focus)), 'head'))

    items = []
    for i in range(100):
        items.append(ItemWidget(i, random.choice(lorem)))

    header = urwid.AttrMap(urwid.Text('selected:'), 'head')
    listbox = urwid.ListBox(urwid.SimpleListWalker(items))
    view = urwid.Frame(urwid.AttrWrap(listbox, 'body'), header=header)
    loop = urwid.MainLoop(view, palette, unhandled_input=keystroke)
    loop.run()

if __name__ == '__main__':
    main()

