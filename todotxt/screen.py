#!/usr/bin/env python
import sys

import tty
import termios
import select
import time

import todotxt.terminal_operations


class Screen:
    """Maintains the screen state"""

    def __init__(self, items):
        self.key            = ' '
        self.terminal       = todotxt.terminal_operations.TerminalOperations()
        self.columns        = self.terminal.columns
        self.rows           = self.terminal.rows
        self.top_row        = 3
        self.selected_row   = self.top_row
        self.selected_item  = 0
        self.starting_item  = 0
        self.update_items(items)
        self.original_terminal_settings = termios.tcgetattr(sys.stdin.fileno())
        self.terminal.clear_screen()

    def update_items(self, items):
        self.items = items
        self.context_list = ["All"] + items.all_contexts()
        self.project_list = ["All"] + items.all_projects()
        self.selected_context = 0
        self.selected_project = 0

    def update(self):
        term    = self.terminal
        columns = self.terminal.columns
        rows    = self.terminal.rows
        items   = self.items.todo_items

        term.update_screen_size()

        # if window resized
        if self.terminal.columns != columns or self.terminal.rows != rows:
            term.clear_screen()
            columns = self.terminal.columns
            rows    = self.terminal.rows
            self.columns = columns
            self.rows = rows

            if self.selected_row > rows:
                self.starting_item = self.selected_item - rows + self.top_row
                self.selected_row = rows

        # Titlebar
        term.output( term.clear_formatting() )
        term.move_cursor(1, 1)
        term.output( term.foreground_color(4) + term.background_color(10) )
        term.output( "Todos:{}  Key:'{}'  Rows:{}  Columns:{}  StartingItem:{} SelectedRow:{} SelectedItem:{}".format(
            len(items), ord(self.key), rows, columns, self.starting_item, self.selected_row, self.selected_item).ljust(columns)[:columns]
        )
        term.output( term.clear_formatting() )

        term.move_cursor_next_line()

        # Contexts
        term.output("Context: {}".format("".join(
            ["{} {} {}".format(term.background_color(11), c, term.clear_formatting()) if c == self.context_list[self.selected_context] else " {} ".format(c) for c in self.context_list]
        )))

        # Todo List
        current_item = self.starting_item
        for row in range(self.top_row, rows + 1):
            if current_item >= len(items):
                break
            # term.move_cursor_next_line()
            term.move_cursor(row, 1)

            if self.selected_row == row:
                term.output( term.background_color(11) )
            else:
                term.output( term.clear_formatting() )

            term.output(
                items[current_item].highlight(
                    items[current_item].raw.strip()[:columns].ljust(columns)
                )
            )
            term.output( term.clear_formatting() )
            current_item += 1

        sys.stdout.flush()

    def move_selection_down(self):
        if self.selected_item < len(self.items.todo_items) - 1:
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
        self.selected_item = len(self.items.todo_items)-1
        if len(self.items.todo_items) > self.terminal.rows:
            self.starting_item = self.selected_item - self.terminal.rows + self.top_row
        else:
            self.starting_item = 0
            self.selected_row = self.terminal.rows
            self.selected_row = self.selected_item + self.top_row

    def move_selection_top(self):
        self.selected_item = 0
        self.starting_item = 0
        self.selected_row = self.top_row

    def select_previous_context(self):
        self.selected_context -= 1
        if self.selected_context < 0:
            self.selected_context = len(self.context_list)-1

    def select_next_context(self):
        self.selected_context += 1
        if self.selected_context == len(self.context_list):
            self.selected_context = 0

    def main_loop(self):
        self.update()
        c = ""
        tty.setraw(sys.stdin.fileno())
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
                    elif c == "c":
                        self.select_next_context()
                    elif c == "C":
                        self.select_previous_context()
                    elif ord(c) == 3: # ctrl-c
                        break
                    # elif ord(c) == 127: # backspace
                    # elif ord(c) == 13: # enter
                    # elif ord(c) == 9: # tab
                    elif ord(c) == 27: # special key - read another byte
                        c = sys.stdin.read(1)
                        self.key = c
                        if ord(c) == 91: # special key - read another byte
                            c = sys.stdin.read(1)
                            self.key = c
                            if ord(c) == 65: # up
                                self.move_selection_up()
                            elif ord(c) == 66: # down
                                self.move_selection_down()
                            elif ord(c) == 53: # page up
                                self.move_selection_top()
                            elif ord(c) == 54: # page down
                                self.move_selection_bottom()
                    self.update()
            # check the screen size every 2 seconds or so instead of trapping SIGWINCH
            elif int(time.perf_counter()) % 2 == 0:
                if (self.columns, self.rows) != self.terminal.screen_size():
                    self.update()
        # End while - exit app
        self.exit()

    def exit(self):
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.original_terminal_settings)

