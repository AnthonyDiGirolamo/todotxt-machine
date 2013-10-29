#!/usr/bin/env python
import sys

import tty
import termios
import readline
import select
import time

from todotxt.todo import Todo
from todotxt.terminal_operations import TerminalOperations

class Screen:
    """Maintains the screen state"""

    colors = {
        "normal":   {
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

        # if context changed
        if self.selected_context != self.last_context:
            self.last_context = self.selected_context
            self.move_selection_top()
            term.clear_screen()
        # if project changed
        if self.selected_project != self.last_project:
            self.last_project = self.selected_project
            self.move_selection_top()
            term.clear_screen()

        if self.selected_context == 0 and self.selected_project == 0:
            self.items = self.todo.todo_items
        elif self.selected_project != 0 and self.selected_context != 0:
            self.items = self.todo.filter_context_and_project(self.context_list[self.selected_context], self.project_list[self.selected_project])
        elif self.selected_project != 0:
            self.items = self.todo.filter_project(self.project_list[self.selected_project])
        elif self.selected_context != 0:
            self.items = self.todo.filter_context(self.context_list[self.selected_context])

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
        term.output( Screen.colors["header"]["fg"] + Screen.colors["header"]["bg"] )
        term.output( "Todos:{}  Sort: {}  Key:'{}'  Rows:{}  Columns:{}  StartingItem:{} SelectedRow:{} SelectedItem:{}".format(
            len(self.items), self.sorting_names[self.sorting], ord(self.key), rows, columns, self.starting_item, self.selected_row, self.selected_item).ljust(columns)[:columns]
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
                if current_item >= len(self.items):
                    break
                # term.move_cursor_next_line()
                term.move_cursor(row, 1)

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
                    elif c == 'o' or c == 'n':
                        self.edit_item(new='append')
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
            elif int(time.clock()) % 2 == 0:
                if (self.columns, self.rows) != self.terminal.screen_size():
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
        self.move_selection_up()
        self.terminal.clear_screen()

    def edit_item(self, new=False):
        self.terminal.move_cursor_next_line()
        self.restore_normal_input()

        if new:
            pass
        else:
            raw_index = self.items[self.selected_item].raw_index
            new_todo_line = self.items[self.selected_item].raw.strip()
            readline.set_startup_hook(lambda: readline.insert_text(new_todo_line))

        readline.parse_and_bind('set editing-mode vi')
        readline.parse_and_bind('set keymap vi-command')

        try:
            # new_todo_line = raw_input()
            new_todo_line = input()
        finally:
            readline.set_startup_hook(None)

        self.set_raw_input()
        self.terminal.clear_screen()

        if new == 'append':
            self.todo.append(new_todo_line)
        else:
            self.todo[raw_index].update(new_todo_line)

    def exit(self):
        self.restore_normal_input()

