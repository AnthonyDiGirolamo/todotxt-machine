import pytest
from .. import todo

@pytest.fixture
def todos():
  return todo.Todo([
    "(A) Thank Mom for the meatballs @phone",
    "(B) Schedule Goodwill pickup +GarageSale @phone",
    "Unpack the guest bedroom +Unpacking",
    "Post signs around the neighborhood +GarageSale",
    "@GroceryStore Eskimo pies" ])

def test_todo_init(todos):
  assert len(todos.items) == 5

def test_todo_contexts(todos):
  assert "@phone" in todos.contexts("(A) Thank Mom for the meatballs @phone")
  assert ["@home", "@phone"] == todos.contexts("Make phonecalls from home @phone @home")

def test_todo_projects(todos):
  assert "+GarageSale" in todos.projects("(B) Schedule Goodwill pickup +GarageSale @phone")
  assert ["+deck", "+portch"] == todos.projects("Finish outdoor projects +portch +deck")

def test_todo_all_contexts(todos):
  assert ["@GroceryStore", "@phone"] == todos.all_contexts()

def test_todo_all_projects(todos):
  assert ["+GarageSale", "+Unpacking"] == todos.all_projects()

def test_todo_creation_date(todos):
  assert todos.creation_date("2011-03-02 Document +TodoTxt task format") == "2011-03-02"
  assert todos.creation_date("(A) 2011-03-02 Call Mom") == "2011-03-02"
  with pytest.raises(todo.NoCreationDateError):
    assert todos.creation_date("(A) Call Mom 2011-03-02")

def test_todo_due_date(todos):
  assert todos.due_date("2011-03-02 Document +TodoTxt task format due:2013-10-25") == "2013-10-25"
  assert todos.due_date("2011-03-02 due:2013-10-25 Document +TodoTxt task format") == "2013-10-25"
