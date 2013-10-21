#!/usr/bin/env python
import sys
import subprocess
import tty
import termios

class TerminalOperations:
    """For interacting with the terminal"""

    def __init__(self):
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

    # def get_char
    #   state = `stty -g`
    #   `stty raw -echo -icanon isig`
    #   STDIN.getc.chr
    # ensure
    #   `stty #{state}`
    # end

    # another solution for single key press
    def getch(self):
        """getch() -> key character

        Read a single keypress from stdin and return the resulting character.
        Nothing is echoed to the console. This call will block if a keypress
        is not already available, but will not wait for Enter to be pressed.

        If the pressed key was a modifier key, nothing will be detected; if
        it were a special function key, it may return the first character of
        of an escape sequence, leaving additional characters in the buffer.
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

# one solution to get single key press
# import termios, fcntl, sys, os, select
# fd = sys.stdin.fileno()
# oldterm = termios.tcgetattr(fd)
# newattr = oldterm[:]
# newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
# termios.tcsetattr(fd, termios.TCSANOW, newattr)
# oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
# fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
# try:
#   while 1:
#     r, w, e = select.select([fd], [], [])
#     if r:
#       c = sys.stdin.read(1)
#       print "Got character", repr(c)
#       if c == "q":
#         break # quit
# finally:
#   termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
#   fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

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

