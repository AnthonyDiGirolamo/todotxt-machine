#!/usr/bin/env python
from todotxt.todo import Todo
from todotxt.terminal_operations import TerminalOperations
from todotxt.completer import Completer

import sys
import tty
import termios
import select
import time
import readline
import textwrap
import random

if sys.version_info.major >= 3:
    getinput = input
    # perf_counter = time.perf_counter
elif sys.version_info.major < 3:
    getinput = raw_input
    # perf_counter = time.time

class Screen:
    """Maintains the screen state"""

    colors = {
        "normal":   {
            "fg": Todo.colors["foreground"],
            "bg": TerminalOperations.background_color(234)
        },
        "header":   {
            "bg": TerminalOperations.background_color(235),
            "fg": TerminalOperations.foreground_color(81)
        },
        "selected": {
            "bg": TerminalOperations.background_color(238)
        },
    }

    def __init__(self, todo):
        random.seed()
        self.key            = ' '
        self.terminal       = TerminalOperations()
        self.columns        = self.terminal.columns
        self.rows           = self.terminal.rows
        self.top_row        = 4
        self.selected_row   = self.top_row
        self.selected_item  = 0
        self.starting_item  = 0
        self.todo           = todo
        self.sorting_names  = ["Unsorted", "Ascending ", "Descending"]
        self.sorting        = 0
        self.update_todos(todo)
        self.original_terminal_settings = termios.tcgetattr(sys.stdin.fileno())
        self.terminal.clear_screen()

    def update_todos(self, todo):
        self.todo           = todo
        self.items          = self.todo.todo_items
        self.context_list = ["All"] + todo.all_contexts()
        self.project_list = ["All"] + todo.all_projects()
        self.selected_context = 0
        self.last_context = 0
        self.selected_project = 0
        self.last_project = 0

    def update(self):
        term = self.terminal
        columns = self.terminal.columns
        rows = self.terminal.rows

        term.update_screen_size(set_terminal_raw=False)

        # if window resized
        if self.terminal.columns != columns or self.terminal.rows != rows:
            columns = self.terminal.columns
            rows    = self.terminal.rows
            self.columns = columns
            self.rows = rows

            if self.selected_row > rows:
                self.starting_item = self.selected_item - rows + self.top_row
                self.selected_row = rows

        # if context changed
        if self.selected_context != self.last_context:
            self.last_context = self.selected_context
            self.move_selection_top()
        # if project changed
        if self.selected_project != self.last_project:
            self.last_project = self.selected_project
            self.move_selection_top()

        # load items
        if self.selected_context == 0 and self.selected_project == 0:
            self.items = self.todo.todo_items
        elif self.selected_project != 0 and self.selected_context != 0:
            self.items = self.todo.filter_context_and_project(self.context_list[self.selected_context], self.project_list[self.selected_project])
        elif self.selected_project != 0:
            self.items = self.todo.filter_project(self.project_list[self.selected_project])
        elif self.selected_context != 0:
            self.items = self.todo.filter_context(self.context_list[self.selected_context])

        # Titlebar
        term.output( term.clear_formatting() )
        term.move_cursor(1, 1)
        term.output( Screen.colors["header"]["fg"] + Screen.colors["header"]["bg"] )
        term.output( "Todos:{}  Sort: {}  Key:'{}'  Rows:{}  Columns:{}  StartingItem:{} SelectedRow:{} SelectedItem:{}".format(
                len(self.items),
                self.sorting_names[self.sorting],
                ord(self.key),
                self.terminal.rows,
                self.terminal.columns,
                self.starting_item,
                self.selected_row,
                self.selected_item
            ).ljust(columns)[:columns]
        )

        term.move_cursor(2, 1)
        term.output( Screen.colors["header"]["fg"] + Screen.colors["header"]["bg"] )
        term.output(" "*columns)
        term.move_cursor(2, 1)

        # Contexts
        term.output("Context: {}".format("".join(
            ["{} {} {}".format(
                Todo.colors["context"]+Screen.colors["selected"]["bg"], c, Screen.colors["header"]["fg"]+Screen.colors["header"]["bg"]) if c == self.context_list[self.selected_context] else " {} ".format(c) for c in self.context_list]
        )))

        term.move_cursor(3, 1)
        term.output( Screen.colors["header"]["fg"] + Screen.colors["header"]["bg"])
        term.output(" "*columns)
        term.move_cursor(3, 1)

        # Projects
        term.output( Screen.colors["header"]["fg"] + Screen.colors["header"]["bg"] )
        term.output("Project: {}".format("".join(
            ["{} {} {}".format(
                Todo.colors["project"]+Screen.colors["selected"]["bg"], p, Screen.colors["header"]["fg"]+Screen.colors["header"]["bg"]) if p == self.project_list[self.selected_project] else " {} ".format(p) for p in self.project_list]
        )))

        # Todo List
        if len(self.items) > 0:
            current_item = self.starting_item
            for row in range(self.top_row, rows + 1):
                # term.move_cursor_next_line()
                term.move_cursor(row, 1)

                if current_item >= len(self.items):
                    term.output( Screen.colors["normal"]["bg"] )
                    term.output(" "*columns)
                else:
                    if self.selected_row == row:
                        term.output( Screen.colors["selected"]["bg"] )
                    else:
                        term.output( term.clear_formatting()+Screen.colors["normal"]["bg"] )

                    term.output(
                        self.items[current_item].highlight(
                            self.items[current_item].raw.strip()[:columns].ljust(columns)
                        )
                    )
                    term.output( term.clear_formatting() )
                    current_item += 1
        else:
            for row in range(self.top_row, rows + 1):
                term.move_cursor(row, 1)
                term.output( Screen.colors["normal"]["fg"]+Screen.colors["normal"]["bg"] )
                term.output(" "*columns)
            term.move_cursor(self.top_row, 1)

            quote_width = int(self.terminal.columns * 0.60)
            quote_margin = int((self.terminal.columns - quote_width)/2)
            quote, author = self.todo.quote().split(' -- ')

            lines = []
            for line in textwrap.wrap(quote, width=quote_width):
                lines.append( " "*quote_margin + line.strip().ljust(quote_width) + " "*quote_margin )
            lines.append(" "*columns )
            for index, line in enumerate(textwrap.wrap("-- "+author, width=quote_width)):
                if index == 0:
                    l = line.strip().rjust(quote_width)
                else:
                    l = line.strip().ljust(quote_width)
                lines.append( " "*quote_margin + l + " "*quote_margin )

            for i in range(int((self.terminal.rows - 4 - len(lines))/2)):
                term.move_cursor_next_line()
            term.output( Screen.colors["normal"]["fg"]+Screen.colors["normal"]["bg"] )
            for index, line in enumerate(lines):
                term.output(line)
                term.move_cursor_next_line()

        sys.stdout.flush()

    def move_selection_down(self):
        if self.selected_item < len(self.items) - 1:
            if self.selected_row < self.terminal.rows:
                self.selected_row += 1
                self.selected_item += 1
            elif self.selected_row == self.terminal.rows:
                self.starting_item += 1
                self.selected_item += 1


    def move_selection_up(self):
        if self.selected_item > 0:
            if self.selected_row > self.top_row:
                self.selected_row -= 1
                self.selected_item -= 1
            elif self.selected_row == self.top_row:
                if self.starting_item > 0:
                    self.starting_item -= 1
                    self.selected_item -= 1

    def move_selection_bottom(self):
        item_count = len(self.items)
        self.selected_item = item_count - 1
        if item_count > self.terminal.rows:
            self.starting_item = self.selected_item - self.terminal.rows + self.top_row
            self.selected_row = self.terminal.rows
        else:
            self.starting_item = 0
            self.selected_row = self.terminal.rows
            self.selected_row = self.selected_item + self.top_row

    def move_selection_top(self):
        self.selected_item = 0
        self.starting_item = 0
        self.selected_row = self.top_row

    def select_previous_context(self):
        self.last_context = self.selected_context
        self.selected_context -= 1
        if self.selected_context < 0:
            self.selected_context = len(self.context_list)-1

    def select_next_context(self):
        self.last_context = self.selected_context
        self.selected_context += 1
        if self.selected_context == len(self.context_list):
            self.selected_context = 0

    def select_previous_project(self):
        self.last_project = self.selected_project
        self.selected_project -= 1
        if self.selected_project < 0:
            self.selected_project = len(self.project_list)-1

    def select_next_project(self):
        self.last_project = self.selected_project
        self.selected_project += 1
        if self.selected_project == len(self.project_list):
            self.selected_project = 0

    def main_loop(self):
        self.set_raw_input()
        self.update()
        c = ""
        while c != "q":
            # if we have new input
            # if timeout is 0 cpu is 100% pegged
            # if 0.1 then SIGWINCH interrupts the system call
            if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
                c = sys.stdin.read(1)
                self.key = c
                if c != "":
                    if c == "j":
                        self.move_selection_down()
                    elif c == "k":
                        self.move_selection_up()
                    elif c == "g":
                        self.move_selection_top()
                    elif c == "G":
                        self.move_selection_bottom()
                    elif c == "p":
                        self.select_next_project()
                    elif c == "P":
                        self.select_previous_project()
                    elif c == "c":
                        self.select_next_context()
                    elif c == "C":
                        self.select_previous_context()
                    elif c == "s":
                        if self.sorting == 0:
                            self.todo.sorted()
                            self.sorting = 1
                        elif self.sorting == 1:
                            self.todo.sorted_reverse()
                            self.sorting = 2
                        elif self.sorting == 2:
                            self.todo.sorted_raw()
                            self.sorting = 0
                    elif c == "x":
                        i = self.items[self.selected_item].raw_index
                        if self.todo[i].is_complete():
                            self.todo[i].incomplete()
                        else:
                            self.todo[i].complete()
                    elif c == 'A' or c == 'e' or ord(c) == 13: # enter
                        self.edit_item()
                    elif c == 'n':
                        self.edit_item(new='append')
                    elif c == 'O':
                        self.edit_item(new='insert_before')
                    elif c == 'o':
                        self.edit_item(new='insert_after')
                    elif c == 'D':
                        self.delete_item()
                    elif ord(c) == 3: # ctrl-c
                        break
                    # elif ord(c) == 127: # backspace
                    # elif ord(c) == 9: # tab
                    elif ord(c) == 27: # special key - read another byte
                        c = sys.stdin.read(1)
                        self.key = c
                        if ord(c) == 91: # special key - read another byte
                            c = sys.stdin.read(1)
                            self.key = c
                            if ord(c) == 65: # up
                                # self.key = 'up'
                                self.move_selection_up()
                            elif ord(c) == 66: # down
                                # self.key = 'down'
                                self.move_selection_down()
                            elif ord(c) == 53: # page up
                                # self.key = 'pageup'
                                self.move_selection_top()
                            elif ord(c) == 54: # page down
                                # self.key = 'pagedown'
                                self.move_selection_bottom()
                    self.update()
            # check the screen size every 2 seconds or so instead of trapping SIGWINCH
            elif int(time.time()) % 2 == 0:
                if (self.columns, self.rows) != self.terminal.screen_size(set_terminal_raw=False):
                    self.update()
        # End while - exit app
        self.exit()

    def set_raw_input(self):
        self.terminal.hide_cursor()
        tty.setraw(sys.stdin.fileno())

    def restore_normal_input(self):
        self.terminal.show_cursor()
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.original_terminal_settings)

    def delete_item(self):
        raw_index = self.items[self.selected_item].raw_index
        self.todo.delete(raw_index)
        if self.selected_item == len(self.items):
            self.move_selection_up()

    def edit_item(self, new=False):
        self.restore_normal_input()

        if new == 'append':
            new_todo_line = "New Todo"
            pass
        elif new == 'insert_before' or new == 'insert_after':
            if len(self.todo) > 0:
                raw_index = self.items[self.selected_item].raw_index
                if new == 'insert_after':
                    raw_index += 1
            else:
                raw_index = 0

            # if new == 'insert_after':
            # elif new == 'insert_before':
            new_todo_line = "New Todo"
        else:
            raw_index = self.items[self.selected_item].raw_index
            new_todo_line = self.items[self.selected_item].raw.strip()
            readline.set_startup_hook(lambda: readline.insert_text(new_todo_line))

        # Display editing prompt
        self.terminal.output(Screen.colors["header"]["fg"]+Screen.colors["header"]["bg"])
        self.terminal.move_cursor(self.selected_row-1, 1)
        self.terminal.output(" "*self.terminal.columns)
        self.terminal.move_cursor(self.selected_row-1, 1)
        self.terminal.output("Editing: {}".format(new_todo_line))

        for r in range(self.selected_row, self.terminal.rows):
            self.terminal.move_cursor(r, 1)
            self.terminal.output( Screen.colors["normal"]["fg"]+Screen.colors["normal"]["bg"] )
            self.terminal.output(" "*self.terminal.columns)
        self.terminal.move_cursor(self.selected_row, 1)

        # setup readline
        readline.parse_and_bind('set editing-mode vi')
        completer = Completer(self.context_list + self.project_list)
        # we want to autocomplete tokens with @ and + symbols so we remove them from # the current readline delims
        delims = readline.get_completer_delims().replace("@","").replace("+","")
        readline.set_completer_delims(delims)
        readline.set_completer(completer.complete)
        readline.parse_and_bind('tab: complete')

        try:
            new_todo_line = getinput()
            # new_todo_line = input()
        finally:
            readline.set_startup_hook(None)

        self.set_raw_input()

        if new == 'append':
            self.todo.append(new_todo_line)
            self.move_selection_bottom()
        elif new == 'insert_before' or new == 'insert_after':
            self.todo.insert(raw_index, new_todo_line)
        else:
            self.todo[raw_index].update(new_todo_line)

    def exit(self):
        self.restore_normal_input()
        self.terminal.output("\n")

