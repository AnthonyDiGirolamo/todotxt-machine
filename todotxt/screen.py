#!/usr/bin/env python
import todotxt.terminal_operations, sys

class Screen:
  """Maintains the screen state"""

  def __init__(self, items):
    self.terminal     = todotxt.terminal_operations.TerminalOperations()
    self.items        = items
    self.selected_row = 2
    self.terminal.clear_screen()

  def update(self):
    columns = self.terminal.columns
    rows    = self.terminal.rows
    term    = self.terminal
    items   = self.items

    # Titlebar
    term.output( term.clear_formatting() )
    term.move_cursor(1, 1)
    term.output( term.background_color(62) )
    term.output( " Todos:{}  Rows:{}  Columns:{}  Selected:{}".format(len(items), rows, columns, self.selected_row).ljust(columns) )
    term.output( term.clear_formatting() )

    # Todo List
    current_item = 0
    for row in range(2, rows+1):
      if row > len(items):
        break
      term.move_cursor(row, 1)

      if self.selected_row == row:
        term.output( term.background_color(11) )
      else:
        term.output( term.clear_formatting() )

      term.output( items[current_item][:columns].strip().ljust(columns) )
      term.output( term.clear_formatting() )
      current_item += 1

    sys.stdout.flush()

  def move_selection_down(self):
    if self.selected_row < self.terminal.rows:
      self.selected_row += 1

  def move_selection_up(self):
    if self.selected_row > 2:
      self.selected_row -= 1

  def key_loop(self):
    c = ""
    while c != "q":
      c = self.terminal.getch()
      if c == "j":
        self.move_selection_down()
      elif c == "k":
        self.move_selection_up()
      self.update()

