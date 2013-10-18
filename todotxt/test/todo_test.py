import unittest
from .. import todo

class TestTodo(unittest.TestCase):

  def setUp(self):
    self.todo_items = [
      "(A) Thank Mom for the meatballs @phone",
      "(B) Schedule Goodwill pickup +GarageSale @phone",
      "Post signs around the neighborhood +GarageSale",
      "@GroceryStore Eskimo pies" ]
    self.todos = todo.Todo(self.todo_items)

  def test_todo_init(self):
    assert self.todos.items == self.todo_items

  def test_todo_contexts(self):
    assert "@phone" in self.todos.contexts("(A) Thank Mom for the meatballs @phone")

  def test_todo_projects(self):
    assert "+GarageSale" in self.todos.projects("(B) Schedule Goodwill pickup +GarageSale @phone")

if __name__ == '__main__':
  unittest.main()
