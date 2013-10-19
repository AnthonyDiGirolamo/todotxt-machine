import pytest
from .. import todo

@pytest.fixture
def todos():
  return todo.Todos([
    "(A) Thank Mom for the dinner @phone",
    "(B) Schedule Goodwill pickup +GarageSale @phone",
    "Unpack the guest bedroom +Unpacking due:2013-10-20",
    "2013-10-19 Post signs around the neighborhood +GarageSale",
    "@GroceryStore Eskimo pies" ])

def test_todos_init(todos):
  assert len(todos.raw_items)  == 5
  assert len(todos.todo_items) == 5

def test_todos_parse_entries(todos):
  todo = todos.todo_items[0]
  assert todo.raw      == "(A) Thank Mom for the dinner @phone"
  assert todo.contexts == ["@phone"]
  assert todo.projects == []
  assert todo.priority == "A"

  todo = todos.todo_items[1]
  assert todo.raw      == "(B) Schedule Goodwill pickup +GarageSale @phone"
  assert todo.contexts == ["@phone"]
  assert todo.projects == ["+GarageSale"]
  assert todo.priority == "B"

  todo = todos.todo_items[2]
  assert todo.raw      == "Unpack the guest bedroom +Unpacking due:2013-10-20"
  assert todo.contexts == []
  assert todo.projects == ["+Unpacking"]
  assert todo.due_date == "2013-10-20"

  todo = todos.todo_items[3]
  assert todo.raw           == "2013-10-19 Post signs around the neighborhood +GarageSale"
  assert todo.contexts      == []
  assert todo.projects      == ["+GarageSale"]
  assert todo.creation_date == "2013-10-19"

  todo = todos.todo_items[4]
  assert todo.raw      == "@GroceryStore Eskimo pies"
  assert todo.contexts == ["@GroceryStore"]
  assert todo.projects == []

def test_todos_iterable(todos):
  for todo in todos:
    assert todo.raw != ""
  for todo in todos:
    assert todo.raw != ""

def test_todos_contexts(todos):
  assert "@phone" in todos.contexts("(A) Thank Mom for the meatballs @phone")
  assert ["@home", "@phone"] == todos.contexts("Make phonecalls from home @phone @home")

def test_todos_projects(todos):
  assert "+GarageSale" in todos.projects("(B) Schedule Goodwill pickup +GarageSale @phone")
  assert ["+deck", "+portch"] == todos.projects("Finish outdoor projects +portch +deck")

def test_todos_all_contexts(todos):
  assert ["@GroceryStore", "@phone"] == todos.all_contexts()

def test_todos_all_projects(todos):
  assert ["+GarageSale", "+Unpacking"] == todos.all_projects()

def test_todos_creation_date(todos):
  assert todos.creation_date("2011-03-02 Document +TodoTxt task format") == "2011-03-02"
  assert todos.creation_date("(A) 2011-03-02 Call Mom") == "2011-03-02"
  # with pytest.raises(todo.NoCreationDateError):
  assert todos.creation_date("(A) Call Mom 2011-03-02") == ""

def test_todos_due_date(todos):
  assert todos.due_date("2011-03-02 Document +TodoTxt task format due:2013-10-25") == "2013-10-25"
  assert todos.due_date("2011-03-02 due:2013-10-25 Document +TodoTxt task format") == "2013-10-25"
  # with pytest.raises(todo.NoDueDateError):
  assert todos.priority("2011-03-02 Document +TodoTxt task format") == ""

def test_todos_priority(todos):
  assert todos.priority("(A) Priority A") == "A"
  assert todos.priority("(a) Priority A") == "a"
  # with pytest.raises(todo.NoPriorityError):
  assert todos.priority("No Priority (A)") == ""
