#!/usr/bin/env python
# coding=utf-8
import pytest
from datetime import date
from .. import todo

import pprint
pp = pprint.PrettyPrinter(indent=4).pprint

@pytest.fixture
def todos():
    return todo.Todos([
        "(A) Thank Mom for the dinner @phone",
        "(B) Schedule Goodwill pickup +GarageSale @phone",
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale",
        "x 2013-10-01 @GroceryStore Eskimo pies" ], './todo.txt')

@pytest.fixture
def today():
    return date.today()

def test_todos_init(todos):
    assert len(todos) == 5
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

def test_context_project_regex(todos):
    todos.update([
        "(A) 1999-12-24 Thank Mom for the dinner @phone @email mom@email.com",
        "(B) Schedule Goodwill pickup +GarageSale NotA+Project @phone",
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale",
        "x 2013-10-01 @GroceryStore Eskimo pies" ])
    todo = todos[0]
    assert todo.raw      == "(A) 1999-12-24 Thank Mom for the dinner @phone @email mom@email.com"
    assert todo.contexts == ["@email", "@phone"]
    assert todo.projects == []
    assert todo.priority == "A"
    todo = todos[1]
    assert todo.raw      == "(B) Schedule Goodwill pickup +GarageSale NotA+Project @phone"
    assert todo.contexts == ["@phone"]
    assert todo.projects == ["+GarageSale"]
    assert todo.priority == "B"

def test_todos_all_contexts(todos):
    assert ["@GroceryStore", "@phone"] == todos.all_contexts()

def test_todos_all_projects(todos):
    assert ["+GarageSale", "+Unpacking"] == todos.all_projects()

def test_todos_completed_date(todos):
    assert todos.completed_date("2011-03-02 Document +TodoTxt task format")                  == ""
    assert todos.completed_date("(A) 2011-03-02 Document +TodoTxt task format")              == ""
    assert todos.completed_date("x 2012-03-03 2011-03-02 Document +TodoTxt task format")     == "2012-03-03"
    assert todos.completed_date("x 2012-03-03 (A) 2011-03-02 Document +TodoTxt task format") == "2012-03-03"

def test_todos_creation_date(todos):
    assert todos.creation_date("2011-03-02 Document +TodoTxt task format")                  == "2011-03-02"
    assert todos.creation_date("(A) 2011-03-02 Document +TodoTxt task format")              == "2011-03-02"
    assert todos.creation_date("x 2012-03-03 2011-03-02 Document +TodoTxt task format")     == "2011-03-02"
    assert todos.creation_date("x 2012-03-03 (A) 2011-03-02 Document +TodoTxt task format") == "2011-03-02"

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

def test_todos_sorted(todos):
    todos.parse_raw_entries([
        "(B) Schedule Goodwill pickup +GarageSale @phone",
        "(A) Thank Mom for the dinner @phone",
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale",
        "x 2013-10-01 @GroceryStore Eskimo pies" ])
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

def test_todo_highlight(todos):
    todos.parse_raw_entries(["2013-10-25 This is a +Very @cool test"])
    assert todos.todo_items[0].colored == ('plain', ['', ('creation_date', '2013-10-25'), ' This is a ', ('project', '+Very'), ' ', ('context', '@cool'), ' test'])

def test_todos_filter_context_and_project(todos):
    assert [t.raw for t in todos.filter_context_and_project("@phone", "+GarageSale")] == [
        "(B) Schedule Goodwill pickup +GarageSale @phone" ]

def test_todos_update(todos):
    todos.update([
        "(A) 1999-12-24 Thank Mom for the dinner @phone",
        "(B) Schedule Goodwill pickup +GarageSale @phone",
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale",
        "x 2013-10-01 @GroceryStore Eskimo pies" ])
    assert [t.raw for t in todos] == [
        "(A) 1999-12-24 Thank Mom for the dinner @phone",
        "(B) Schedule Goodwill pickup +GarageSale @phone",
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale",
        "x 2013-10-01 @GroceryStore Eskimo pies" ]
    todos.update([
        "x 1999-12-25 (A) 1999-12-24 Thank Mom for the dinner @phone"
        "x 1999-11-10 (B) Schedule Goodwill pickup +GarageSale @phone"
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale",
        "x 2013-10-01 @GroceryStore Eskimo pies" ])
    assert [t.raw for t in todos] == [
        "x 1999-12-25 (A) 1999-12-24 Thank Mom for the dinner @phone"
        "x 1999-11-10 (B) Schedule Goodwill pickup +GarageSale @phone"
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale",
        "x 2013-10-01 @GroceryStore Eskimo pies" ]

def test_todos_complete(todos):
    today = date.today()
    todos.update([
        "(A) 1999-12-24 Thank Mom for the dinner @phone",
        "(B) Schedule Goodwill pickup +GarageSale @phone",
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale",
        "x 2013-10-01 @GroceryStore Eskimo pies" ])
    todos[0].complete()
    todos[1].complete()
    assert [t.raw for t in todos] == [
        "x {} (A) 1999-12-24 Thank Mom for the dinner @phone".format(today),
        "x {} (B) Schedule Goodwill pickup +GarageSale @phone".format(today),
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale",
        "x 2013-10-01 @GroceryStore Eskimo pies" ]
    assert [t.creation_date for t in todos] == [
        "1999-12-24",
        "",
        "",
        "2013-10-19",
        "" ]
    assert [t.completed_date for t in todos] == [
        "{}".format(today),
        "{}".format(today),
        "",
        "",
        "2013-10-01" ]
    assert [t.is_complete() for t in todos] == [ True, True, False, False, True ]
    todos[1].incomplete()
    assert todos[1].raw == "(B) Schedule Goodwill pickup +GarageSale @phone"
    assert todos[1].completed_date == ""

    assert todos[3].creation_date == "2013-10-19"
    assert todos[3].completed_date == ""
    todos[3].complete()
    assert todos[3].creation_date == "2013-10-19"
    assert todos[3].completed_date == "{}".format(today)

def test_todo_incomplete(todos):
    todos.update([
        "x 1999-12-25 (A) 1999-12-24 Thank Mom for the dinner @phone",
        "x 1999-11-10 (B) Schedule Goodwill pickup +GarageSale @phone",
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale",
        "x 2013-10-01 @GroceryStore Eskimo pies" ])
    assert todos[1].creation_date == ""
    assert todos[1].completed_date == "1999-11-10"
    todos[1].incomplete()
    assert todos[1].creation_date == ""
    assert todos[1].completed_date == ""

    assert todos[0].creation_date == "1999-12-24"
    assert todos[0].completed_date == "1999-12-25"
    todos[0].incomplete()
    assert todos[0].creation_date == "1999-12-24"
    assert todos[0].completed_date == ""

def test_todo_is_complete(todos):
    todos.update([
        "x 1999-12-25 (A) 1999-12-24 Thank Mom for the dinner @phone",
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale",
        "x @GroceryStore Eskimo pies" ])
    assert [t.is_complete() for t in todos] == [
        True,
        False,
        False,
        True ]

def test_todo_update(todos):
    t = todos[0]
    t.update("(A) 2000-20-12 Thank Mom for the dinner @phone @home +GiveThanks")
    assert t.raw            == "(A) 2000-20-12 Thank Mom for the dinner @phone @home +GiveThanks"
    assert t.priority       == "A"
    assert t.contexts       == ["@home", "@phone"]
    assert t.projects       == ["+GiveThanks"]
    assert t.creation_date  == "2000-20-12"
    assert t.due_date       == ""
    assert t.completed_date == ""
    assert t.is_complete()  == False

    t = todos[1]
    assert t.raw      == "(B) Schedule Goodwill pickup +GarageSale @phone"
    assert t.contexts == ["@phone"]
    assert t.projects == ["+GarageSale"]
    assert t.priority == "B"

    t = todos[2]
    t.update("x 2013-10-25 Unpack the guest bedroom +Unpacking due:2013-10-20")
    assert t.raw            == "x 2013-10-25 Unpack the guest bedroom +Unpacking due:2013-10-20"
    assert t.priority       == ""
    assert t.contexts       == []
    assert t.projects       == ["+Unpacking"]
    assert t.creation_date  == ""
    assert t.due_date       == "2013-10-20"
    assert t.completed_date == "2013-10-25"
    assert t.is_complete()  == True

    t = todos[3]
    assert t.raw           == "2013-10-19 Post signs around the neighborhood +GarageSale"
    assert t.contexts      == []
    assert t.projects      == ["+GarageSale"]
    assert t.creation_date == "2013-10-19"

    t = todos[4]
    assert t.raw            == "x 2013-10-01 @GroceryStore Eskimo pies"
    assert t.contexts       == ["@GroceryStore"]
    assert t.projects       == []
    assert t.completed_date == "2013-10-01"

def test_todo_add_creation_date(todos, today):
    todos[2].add_creation_date()
    assert todos[2].raw == "{} Unpack the guest bedroom +Unpacking due:2013-10-20".format(today)
    assert todos[2].creation_date == "{}".format(today)

    todos[3].add_creation_date()
    assert todos[3].raw == "2013-10-19 Post signs around the neighborhood +GarageSale"
    assert todos[3].creation_date == "2013-10-19".format(today)

def test_todos_append(todos, today):
    todos.append("THIS IS A TEST @testing")
    todos.append("THIS IS A TEST @testing", add_creation_date=False)
    assert [t.raw for t in todos] == [
        "(A) Thank Mom for the dinner @phone",
        "(B) Schedule Goodwill pickup +GarageSale @phone",
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale",
        "x 2013-10-01 @GroceryStore Eskimo pies",
        "{} THIS IS A TEST @testing".format(today),
        "THIS IS A TEST @testing".format(today)]
    assert [todo.raw_index for todo in todos.todo_items] == [0, 1, 2, 3, 4, 5, 6]

def test_todos_delete(todos):
    todos.delete(0)
    assert [t.raw for t in todos] == [
        "(B) Schedule Goodwill pickup +GarageSale @phone",
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale",
        "x 2013-10-01 @GroceryStore Eskimo pies"]
    assert [todo.raw_index for todo in todos.todo_items] == [0, 1, 2, 3]
    todos.delete(3)
    assert [t.raw for t in todos] == [
        "(B) Schedule Goodwill pickup +GarageSale @phone",
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale"]
    assert [todo.raw_index for todo in todos.todo_items] == [0, 1, 2]

def test_todos_insert(todos, today):
    todos.insert(1, "THIS IS A TEST @testing")
    todos.insert(1, "(B) THIS IS ANOTHER TEST @testing")
    todos.insert(1, "(A) THIS IS ANOTHER TEST @testing", add_creation_date=False)
    assert [t.raw for t in todos] == [
        "(A) Thank Mom for the dinner @phone",
        "(A) THIS IS ANOTHER TEST @testing".format(today),
        "(B) {} THIS IS ANOTHER TEST @testing".format(today),
        "{} THIS IS A TEST @testing".format(today),
        "(B) Schedule Goodwill pickup +GarageSale @phone",
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale",
        "x 2013-10-01 @GroceryStore Eskimo pies",
    ]
    assert [todo.raw_index for todo in todos.todo_items] == [0, 1, 2, 3, 4, 5, 6, 7]

def test_todos_search(todos):
    assert [t.raw for t in todos.search("the")] == [
        "(A) Thank Mom for the dinner @phone",
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale"]
    # one match per line!
    assert [t.search_matches for t in todos.search("the")] == [ ('the',), ('the',), ('the',) ]
    assert [t.raw for t in todos.search("te")] == [
        "(A) Thank Mom for the dinner @phone",
        "Unpack the guest bedroom +Unpacking due:2013-10-20",
        "2013-10-19 Post signs around the neighborhood +GarageSale",
        "x 2013-10-01 @GroceryStore Eskimo pies" ]
    assert [t.search_matches for t in todos.search("te")] == [ ('the',), ('t be',), ('the',), ('tore',) ]

    assert todos.search(".*") == [ ]
    assert todos.search("{b}") == [ ]

    todos.update([
        "(A) 1999-12-24 .Thank* Mom for the .dinner* @phone",
        "(B) Schedule Goodwill pickup +GarageSale @phone",
        "Unpack the guest {bedroom} +Unpacking due:2013-10-20",
        "2013-10-19 Post signs (around) the neighborhood +GarageSale",
        "x 2013-10-01 @GroceryStore Eskimo pies" ])

    assert [t.raw for t in todos.search(".*")]             == [ "(A) 1999-12-24 .Thank* Mom for the .dinner* @phone" ]
    assert [t.search_matches for t in todos.search(".*")]  == [('.dinner*',)]
    assert [t.raw for t in todos.search("{b}")]            == [ "Unpack the guest {bedroom} +Unpacking due:2013-10-20" ]
    assert [t.search_matches for t in todos.search("{b}")] == [('{bedroom}',)]

def test_todos_swap(todos):
    todos.swap(0, 1)
    assert [todo.raw_index for todo in todos.todo_items] == [1, 0, 2, 3, 4]
    todos.swap(3, 2)
    assert [todo.raw_index for todo in todos.todo_items] == [1, 0, 3, 2, 4]
    todos.swap(0, -1)
    assert [todo.raw_index for todo in todos.todo_items] == [4, 0, 3, 2, 1]
    todos.swap(4, 5)
    assert [todo.raw_index for todo in todos.todo_items] == [1, 0, 3, 2, 4]
