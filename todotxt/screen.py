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
        self.sigint         = False
        self.refresh_screen = False

        self.terminal       = todotxt.terminal_operations.TerminalOperations()
        self.items          = items
        self.top_row        = 2
        self.selected_row   = self.top_row
        self.selected_item  = 0
        self.starting_item  = 0
        self.original_terminal_settings = termios.tcgetattr(sys.stdin.fileno())
        self.terminal.clear_screen()

    def update_items(self, items):
        self.items = items

    def update(self):
        term    = self.terminal
        columns = self.terminal.columns
        rows    = self.terminal.rows
        items   = self.items

        term.update_screen_size()
        # if window resized
        if self.terminal.columns != columns or self.terminal.rows != rows:
            term.clear_screen()
            columns = self.terminal.columns
            rows    = self.terminal.rows

            if self.selected_row > rows:
                self.starting_item = self.selected_item - rows + 2
                self.selected_row = rows

        # Titlebar
        term.output( term.clear_formatting() )
        term.move_cursor(1, 1)
        term.output( term.foreground_color(4) + term.background_color(10) )
        term.output( "Todos:{}  Rows:{}  Columns:{}  StartingItem:{} SelectedRow:{} SelectedItem:{}".format(
            len(items), rows, columns, self.starting_item, self.selected_row, self.selected_item).ljust(columns) )
        term.output( term.clear_formatting() )

        # Todo List
        current_item = self.starting_item
        for row in range(2, rows + 1):
            if current_item >= len(items):
                break
            # term.move_cursor_next_line()
            term.move_cursor(row, 1)

            if self.selected_row == row:
                term.output( term.background_color(11) )
            else:
                term.output( term.clear_formatting() )

            term.output(
                # items[current_item][:].strip().ljust(columns)
                term.ljust_with_escapes(items[current_item].strip(), columns)
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

    def main_loop(self):
        self.update()
        c = ""
        tty.setraw(sys.stdin.fileno())
        while c != "q":
            # if timeout is 0 cpu is 100% pegged
            # if 0.1 then SIGWINCH interrupts the system call
            if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
                c = sys.stdin.read(1)
                if c != "":
                    if c == "j":
                        self.move_selection_down()
                    elif c == "k":
                        self.move_selection_up()
                    self.update()
            # refresh the screen every 2 seconds or so
            # instead of trapping SIGWINCH
            elif int(time.perf_counter()) % 2 == 0:
                self.update()
            # elif self.refresh_screen == True:
            #     self.refresh_screen = False
            #     self.terminal.clear_screen()
            #     self.update()
            # elif self.sigint == True:
            #     self.exit()
        # End while
        self.exit()

    def exit(self):
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.original_terminal_settings)

