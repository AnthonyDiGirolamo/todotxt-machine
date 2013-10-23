import pytest
from .. import todo

import pprint
pp = pprint.PrettyPrinter(indent=2).pprint

@pytest.fixture
def todos():
    return todo.Todos([
        "(A) Thank Mom for the dinner @phone",
        "(B) Schedule Goodwill pickup +GarageSale @phone",
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale",
        "x 2013-10-01 @GroceryStore Eskimo pies" ])

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
    assert todo.raw            == "x 2013-10-01 @GroceryStore Eskimo pies"
    assert todo.contexts       == ["@GroceryStore"]
    assert todo.projects       == []
    assert todo.completed_date == "2013-10-01"

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
    assert todos.creation_date("2011-03-03 2011-03-02 Document +TodoTxt task format") == "2011-03-03"
    assert todos.creation_date("(A) 2011-03-02 Call Mom") == "2011-03-02"
    # with pytest.raises(todo.NoCreationDateError):
    assert todos.creation_date("(A) Call Mom 2011-03-02") == ""

def test_todos_due_date(todos):
    assert todos.due_date("2011-03-02 Document +TodoTxt task format due:2013-10-25") == "2013-10-25"
    assert todos.due_date("2011-03-02 due:2013-10-25 Document +TodoTxt task format") == "2013-10-25"
    # with pytest.raises(todo.NoDueDateError):
    assert todos.due_date("2011-03-02 Document +TodoTxt task format") == ""

def test_todos_priority(todos):
    assert todos.priority("(A) Priority A") == "A"
    assert todos.priority("(Z) Priority Z") == "Z"
    assert todos.priority("(a) No Priority") == ""
    # with pytest.raises(todo.NoPriorityError):
    assert todos.priority("No Priority (A)") == ""
    assert todos.priority("(A)No Priority") == ""
    assert todos.priority("(A)->No Priority") == ""

def test_todos_completed(todos):
    assert todos.completed("x 2011-03-03 Call Mom)")        == "2011-03-03"
    assert todos.completed("xylophone lesson")              == False
    assert todos.completed("X 2012-01-01 Make resolutions") == False
    assert todos.completed("x (A) Find ticket prices")      == False

def test_todos_sorted(todos):
    todos.raw_items = [
        "(B) Schedule Goodwill pickup +GarageSale @phone",
        "(A) Thank Mom for the dinner @phone",
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale",
        "x 2013-10-01 @GroceryStore Eskimo pies" ]
    todos.parse_raw_entries()
    assert [todo.raw_index for todo in todos.todo_items] == [0, 1, 2, 3, 4]

    todos.sorted()
    assert [todo.raw for todo in todos.todo_items] == [
        "(A) Thank Mom for the dinner @phone",
        "(B) Schedule Goodwill pickup +GarageSale @phone",
        "2013-10-19 Post signs around the neighborhood +GarageSale",
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "x 2013-10-01 @GroceryStore Eskimo pies" ]
    assert [todo.raw_index for todo in todos.todo_items] == [1, 0, 3, 2, 4]

    todos.sorted_raw()
    assert [todo.raw for todo in todos.todo_items] == [
        "(B) Schedule Goodwill pickup +GarageSale @phone",
        "(A) Thank Mom for the dinner @phone",
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale",
        "x 2013-10-01 @GroceryStore Eskimo pies" ]
    assert [todo.raw_index for todo in todos.todo_items] == [0, 1, 2, 3, 4]

def test_todos_sorted_reverese(todos):
    todos.sorted_reverse()
    assert [todo.raw for todo in todos.todo_items] == [
        "x 2013-10-01 @GroceryStore Eskimo pies",
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale",
        "(B) Schedule Goodwill pickup +GarageSale @phone",
        "(A) Thank Mom for the dinner @phone" ]
    assert [todo.raw_index for todo in todos.todo_items] == [4, 2, 3, 1, 0]

def test_todos_filter_context(todos):
    assert [t.raw for t in todos.filter_context("@phone")] == [
        "(A) Thank Mom for the dinner @phone",
        "(B) Schedule Goodwill pickup +GarageSale @phone"]
    assert [t.raw for t in todos.filter_context("@GroceryStore")] == [
        "x 2013-10-01 @GroceryStore Eskimo pies" ]

def test_todos_filter_project(todos):
    assert [t.raw for t in todos.filter_project("+GarageSale")] == [
        "(B) Schedule Goodwill pickup +GarageSale @phone",
        "2013-10-19 Post signs around the neighborhood +GarageSale" ]
    assert [t.raw for t in todos.filter_project("+Unpacking")] == [
        "Unpack the guest bedroom +Unpacking due:2013-10-20" ]

def test_todos_highlight(todos):
    todos.raw_items = ["(A) 2013-10-25 This is a +Very @cool test"]
    todos.parse_raw_entries()
    assert "\x1b[m" + todos.todo_items[0].colored == "\x1b[m" + "(A) \x1b[38;5;2m2013-10-25\x1b[38;5;13m This is a \x1b[38;5;4m+Very\x1b[38;5;13m \x1b[38;5;1m@cool\x1b[38;5;13m test"

