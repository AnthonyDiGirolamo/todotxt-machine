#!/usr/bin/env python
# coding=utf-8
import sys
# import os
import subprocess
import tty
import termios
import re
# import curses
import fcntl
import struct

class TerminalOperations:
    """For interacting with the terminal"""

    _escape_sequence_regex = re.compile(r'\x1b\[[0-9;]*m')
    _screen_size_regex     = re.compile(r'\[8;(.*);(.*)t')

    @staticmethod
    def foreground_color(index):
        return "\x1B[38;5;{0}m".format(index)

    @staticmethod
    def background_color(index):
        return "\x1B[48;5;{0}m".format(index)

    @staticmethod
    def clear_formatting():
        return "\x1B[m"

    def __init__(self, use_tput=False):
        # self.window = curses.initscr()
        self.update_screen_size(use_tput)

    def update_screen_size(self, use_tput=False):
        self.columns, self.rows = self.screen_size(use_tput)

    def output(self, text):
        sys.stdout.write(text)

    def hide_cursor(self):
        # subprocess.check_output(["tput", "civis"])
        self.output('\x1b[?25l')

    def show_cursor(self):
        # subprocess.check_output(["tput", "cnorm"])
        self.output('\x1b[34h\x1b[?25h')

    def clear_screen(self):
        self.output("\x1B[2J")

    def screen_size(self, use_tput=False):
        # Method: Usint tput
        if use_tput:
            return ( int(subprocess.check_output(["tput", "cols"])), int(subprocess.check_output(["tput", "lines"])) )
        else:
            # this is how urwid does it in raw_terminal display mode
            buf = fcntl.ioctl(0, termios.TIOCGWINSZ, ' '*4)
            y, x = struct.unpack('hh', buf)
            return x, y

        # Query the terminal directly in bash:
        # stty -echo; echo -en "\033[18t"; read -d t size; stty echo; size=${size/#??/}; echo $size

        # Method: querying the terminal directly with escape sequences
        # the following breaks if the terminal does not have this capability, ie if TERM=screen*
        # response = ""
        # c        = ""
        # if set_terminal_raw:
        #     original_stdin_settings = termios.tcgetattr(sys.stdin.fileno())
        #     tty.setraw(sys.stdin.fileno())
        # sys.stdout.write("\x1B[18t")
        # try:
        #     while c != "t":
        #         c = sys.stdin.read(1)
        #         response += c
        # finally:
        #     if set_terminal_raw:
        #         termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, original_stdin_settings)
        # response = response.split(";")
        # rows     = int(response[-2])
        # columns  = int(response[-1][0:-1])
        # return (columns, rows)

        # Method using curses module
        # return self.window.getmaxyx()


    def move_cursor(self, row, column):
        self.output("\x1B[{0};{1}H".format(row, column))

    def move_cursor_home(self):
        self.output("\x1B[[H")

    def move_cursor_next_line(self):
        self.output("\x1B[E")

    @staticmethod
    def length_ignoring_escapes(line):
        return len(line) - sum([len(i) for i in TerminalOperations._escape_sequence_regex.findall(line)])

    @staticmethod
    def ljust_with_escapes(line, columns, string_length=0):
        length = TerminalOperations.length_ignoring_escapes(line) if string_length == 0 else string_length
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

