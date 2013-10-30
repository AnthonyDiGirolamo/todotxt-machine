#!/usr/bin/env python
# coding=utf-8
import pytest
from .. import terminal_operations

@pytest.fixture
def term():
  return terminal_operations.TerminalOperations(use_tput=True)

def test_terminal_operations_init(term):
  assert type(term.rows) == int
  assert type(term.columns) == int
  assert term.rows > 0
  assert term.columns > 0

def test_terminal_operations_foreground_color(term):
  for i in range(0, 256):
    assert term.foreground_color(i) == "\x1B[38;5;{}m".format(i)

def test_terminal_operations_move_cursor(term, capsys):
  for i in range(0, 5):
    term.move_cursor(i, i)
    term.output("X")
  out, error = capsys.readouterr()
  assert out == "\x1B[0;0HX\x1B[1;1HX\x1B[2;2HX\x1B[3;3HX\x1B[4;4HX"

def test_terminal_operations_length_ignoring_escapes(term):
    assert len("(A) 2013-10-25 This is a +Very @cool test") == term.length_ignoring_escapes("\x1b[m(A) \x1b[38;5;2m2013-10-25\x1b[38;5;13m This is a \x1b[38;5;4m+Very\x1b[38;5;13m \x1b[38;5;1m@cool\x1b[38;5;13m test")

def test_terminal_operations_ljust_with_escapes(term):
    test_string = "(A) 2013-10-25 This is a +Very @cool test"
    test_string_with_escapes = "\x1b[m(A) \x1b[38;5;2m2013-10-25\x1b[38;5;13m This is a \x1b[38;5;4m+Very\x1b[38;5;13m \x1b[38;5;1m@cool\x1b[38;5;13m test"
    assert len(test_string.ljust(80)) - len(test_string) == len(term.ljust_with_escapes(test_string_with_escapes, 80)) - len(test_string_with_escapes)
