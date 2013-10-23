#!/usr/bin/env python
import sys
import subprocess
# import tty
# import termios
# import select
import re

class TerminalOperations:
    """For interacting with the terminal"""

    def __init__(self):
        self._escape_sequence_regex = re.compile(r'\x1b\[[0-9;]*m')
        self.update_screen_size()

    def update_screen_size(self):
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

    def move_cursor_home(self):
        self.output("\x1B[[H")

    def move_cursor_next_line(self):
        self.output("\x1B[E")

    def length_ignoring_escapes(self, line):
        return len(line) - sum([len(i) for i in self._escape_sequence_regex.findall(line)])

    def ljust_with_escapes(self, line, columns):
        length = self.length_ignoring_escapes(line)
        if length < columns:
            line += " " * (columns - length)
        return line

    # solution for single key press - blocking
    # def getch(self):
    #     """getch() -> key character

    #     Read a single keypress from stdin and return the resulting character.
    #     Nothing is echoed to the console. This call will block if a keypress
    #     is not already available, but will not wait for Enter to be pressed.

    #     If the pressed key was a modifier key, nothing will be detected; if
    #     it were a special function key, it may return the first character of
    #     of an escape sequence, leaving additional characters in the buffer.
    #     """
    #     fd = sys.stdin.fileno()
    #     old_settings = termios.tcgetattr(fd)
    #     try:
    #         tty.setraw(fd)
    #         ch = sys.stdin.read(1)
    #     finally:
    #         termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    #     return ch

# print("\x1B]0;THIS IS A TITLE BAR DEMO...\x07")
# print("Wait for 5 seconds...")
# print("\x1B]0;\x07")

# def screen_size_using_escapes
#   state = `stty -g`
#   `stty raw -echo -icanon isig`
#   STDOUT.write "\e[18t"
#   response = c = ""
#   while c != 't'
#     c = STDIN.getbyte.chr #if STDIN.ready?
#     response += c.to_s unless c == "\e"
#   end
#   if response =~ /\[8;(.*);(.*)t/
#     rows = $1
#     cols = $2
#     return [cols, rows]
#   end
#   return []
# ensure
#   `stty #{state}`
# end

# Ruby - get single keypress
# def get_char
#   state = `stty -g`
#   `stty raw -echo -icanon isig`
#   STDIN.getc.chr
# ensure
#   `stty #{state}`
# end

