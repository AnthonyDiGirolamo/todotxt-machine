#!/usr/bin/env python3
import sys, subprocess

class TerminalOperations:
  """For interacting with the terminal"""

  def __init__(self):
    self.columns, self.rows = self.screen_size()

  def output(self, text):
    sys.stdout.write(text)

  def foreground_color(self, index):
    return "\x1B[38;5;{}m".format(index)

  def background_color(self, index):
    return "\x1B[48;5;{}m".format(index)

  def clear_formatting(self):
    return "\x1B[m"

  def clear_screen(self):
    self.output("\x1B[2J")

  def screen_size(self):
    return ( int(subprocess.check_output(["tput", "cols"])), int(subprocess.check_output(["tput", "lines"])) )

  def move_cursor(self, row, column):
    self.output("\x1B[{};{}H".format(row, column))

# print("\x1B]0;THIS IS A TITLE BAR DEMO...\x07")
# print("Wait for 5 seconds...")
# print("\x1B]0;\x07")

