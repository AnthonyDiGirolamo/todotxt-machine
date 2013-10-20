import pytest
from .. import terminal_operations

@pytest.fixture
def term():
  return terminal_operations.TerminalOperations()

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
