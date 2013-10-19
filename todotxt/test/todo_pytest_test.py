import pytest
from .. import todo

@pytest.fixture
def todos():
  return todo.Todo([
    "(A) Thank Mom for the meatballs @phone",
    "(B) Schedule Goodwill pickup +GarageSale @phone",
    "Post signs around the neighborhood +GarageSale",
    "@GroceryStore Eskimo pies" ])

def test_todo_init(todos):
  assert todos.items == [
    "(A) Thank Mom for the meatballs @phone",
    "(B) Schedule Goodwill pickup +GarageSale @phone",
    "Post signs around the neighborhood +GarageSale",
    "@GroceryStore Eskimo pies" ]

def test_todo_contexts(todos):
  assert "@phone" in todos.contexts("(A) Thank Mom for the meatballs @phone")

def test_todo_projects(todos):
  assert "+GarageSale" in todos.projects("(B) Schedule Goodwill pickup +GarageSale @phone")

