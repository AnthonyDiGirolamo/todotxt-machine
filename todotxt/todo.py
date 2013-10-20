#!/usr/bin/env python
import re

# class NoCreationDateError(Exception):
#   pass
# class NoDueDateError(Exception):
#   pass
# class NoPriorityError(Exception):
#   pass

class Todo:
  """Single Todo item"""

  def __init__(self, item,
      priority="", contexts=[], projects=[],
      creation_date="", due_date="", completed_date=""):
    self.raw            = item
    self.priority       = priority
    self.contexts       = contexts
    self.projects       = projects
    self.creation_date  = creation_date
    self.due_date       = due_date
    self.completed_date = completed_date

  # def is_complete(self):
  #   if self.completed_date == "":
  #     return False
  #   else:
  #     return True

class Todos:
  """Todo items"""

  def __init__(self, todo_items):
    self.raw_items = todo_items
    self._context_regex       = re.compile(r'\s*(@\S+)\s*')
    self._project_regex       = re.compile(r'\s*(\+\S+)\s*')
    self._creation_date_regex = re.compile(r'^\(?\w?\)?\s*(\d\d\d\d-\d\d-\d\d)\s*')
    self._due_date_regex      = re.compile(r'\s*due:(\d\d\d\d-\d\d-\d\d)\s*')
    self._priority_regex      = re.compile(r'\((\w)\) ')
    self._completed_regex     = re.compile(r'^x (\d\d\d\d-\d\d-\d\d)')
    self.parse_raw_entries()

  def __iter__(self):
    self.index = -1
    return self

  def __next__(self):
    self.index = self.index + 1
    if self.index == len(self.todo_items):
      raise StopIteration
    return self.todo_items[self.index]

  def parse_raw_entries(self):
    self.todo_items = [ Todo(todo,
      contexts=self.contexts(todo),
      projects=self.projects(todo),
      priority=self.priority(todo),
      creation_date=self.creation_date(todo),
      due_date=self.due_date(todo),
      completed_date=self.completed(todo)) for todo in self.raw_items]

  def contexts(self, item):
    return sorted( self._context_regex.findall(item) )

  def projects(self, item):
    return sorted( self._project_regex.findall(item) )

  def all_contexts(self):
    # Nested Loop
    # all_contexts = []
    # for item in self.raw_items:
    #   for found_context in self.contexts(item):
    #     if found_context not in all_contexts:
    #       all_contexts.append(found_context)
    # return all_contexts

    # List comprehension
    # return sorted(set( [found_context for item in self.raw_items for found_context in self.contexts(item)] ))

    # Join all items and use one regex.findall
    return sorted(set( self._context_regex.findall(" ".join(self.raw_items))))

  def all_projects(self):
    # List comprehension
    # return sorted(set( [project for item in self.raw_items for project in self.projects(item)] ))

    # Join all items and use one regex.findall
    return sorted(set( self._project_regex.findall(" ".join(self.raw_items))))

  def creation_date(self, item):
    match = self._creation_date_regex.search(item)
    if match and len(match.groups()) == 1:
      return match.group(1)
    else:
      # raise NoCreationDateError
      return ""

  def due_date(self, item):
    match = self._due_date_regex.search(item)
    if match and len(match.groups()) == 1:
      return match.group(1)
    else:
      # raise NoDueDateError
      return ""

  def priority(self, item):
    match = self._priority_regex.match(item)
    if match and len(match.groups()) == 1:
      return match.group(1)
    else:
      # raise NoPriorityError
      return ""

  def completed(self, item):
    match = self._completed_regex.match(item)
    if match and len(match.groups()) == 1:
      return match.group(1)
    else:
      return False


