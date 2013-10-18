import sys, subprocess

class TerminalOperations:
  """For interacting with the terminal"""

  def __init__(self):
    self.columns, self.rows = self.screen_size()

  def output(self, text):
    sys.stdout.write(text)

  def foreground_color(self, index):
    return "\033[38;5;{}m".format(index)

  def background_color(self, index):
    return "\033[48;5;{}m".format(index)

  def clear_formatting(self):
    return "\033[m"

  def clear_screen(self):
    self.output("\033[2J")

  def screen_size(self):
    return ( int(subprocess.check_output(["tput", "cols"])), int(subprocess.check_output(["tput", "lines"])) )

