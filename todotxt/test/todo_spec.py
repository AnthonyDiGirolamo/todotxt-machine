import unittest
from .. import todo

class TestTodo(unittest.TestCase):

  def setUp(self):
    self.todo_items = [
      "(A) Thank Mom for the meatballs @phone",
      "(B) Schedule Goodwill pickup +GarageSale @phone",
      "Post signs around the neighborhood +GarageSale",
      "@GroceryStore Eskimo pies" ]

  def test_todo_init(self):
    todos = todo.Todo(self.todo_items)
    self.assertEqual( todos.items , self.todo_items )

if __name__ == '__main__':
      unittest.main()
