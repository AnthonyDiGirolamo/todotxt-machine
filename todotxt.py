#!/usr/bin/env python3

import os

from terminal_operations import TerminalOperations

term = TerminalOperations()
term.clear_screen()

for i in range(256):
  term.output(term.background_color(i) + "color " + str(i) + term.clear_formatting() + "\n")

print("Screen Size:", term.columns, "x", term.rows)
exit(0)

todotxt_file_path = os.path.expanduser("~/Dropbox/todo/todobackup.txt")
# todotxt_file_path = os.path.expanduser("~/Dropbox/todo/todobackup.")

# if os.path.exists(todotxt_file_path):
#   print("FOUND: ", todotxt_file_path)
# else:
#   print("WARNING: unable to open", repr(todotxt_file_path))
#   exit(1)

todo_items = []

try:
  with open(todotxt_file_path, "r") as todotxt_file:
    todo_items = todotxt_file.readlines()
except FileNotFoundError:
  print("WARNING: unable to open", repr(todotxt_file_path))
  exit(1)
# except:
#   print("Unexpected error:", sys.exc_info()[0])
#   raise
# else:
#   todo_items = todotxt_file.readlines()
# finally:
#   print("Done")

for index, item in enumerate(todo_items):
  print(index, item.strip())

# Other ways to read lines:
# todotxt_file = open(todotxt_file_path, 'r') # open file
# todotxt_file.read()        # read entire file
# todotxt_file.readline()    # read one line at a time
# todotxt_file.readlines()   # returns a list of strings per line
# list(todotxt_file)
# for line in todotxt_file:  # iterate over each line in a file
#   print(repr(line))
# todotxt_file.close()       # close the file

# if __name__ == "__main__":
#   import sys
#   pass
#   # fib(int(sys.argv[1]))

