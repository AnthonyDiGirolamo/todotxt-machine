#!/usr/bin/env python
import re

class NoCreationDateError(Exception):
  pass

class NoDueDateError(Exception):
  pass

class NoPriorityError(Exception):
  pass

class Todo:
  """Todo items"""

  def __init__(self, todo_items):
    self.items = todo_items
    self._context_regex       = re.compile(r'\s*(@\S+)\s*')
    self._project_regex       = re.compile(r'\s*(\+\S+)\s*')
    self._creation_date_regex = re.compile(r'^\(?\w?\)?\s*(\d\d\d\d-\d\d-\d\d)\s*')
    self._due_date_regex      = re.compile(r'\s*due:(\d\d\d\d-\d\d-\d\d)\s*')
    self._priority_regex      = re.compile(r'\((\w)\)')

  def contexts(self, item):
    return sorted( self._context_regex.findall(item) )

  def projects(self, item):
    return sorted( self._project_regex.findall(item) )

  def all_contexts(self):
    # Nested Loop
    # all_contexts = []
    # for item in self.items:
    #   for found_context in self.contexts(item):
    #     if found_context not in all_contexts:
    #       all_contexts.append(found_context)
    # return all_contexts

    # List comprehension
    # return sorted(set( [found_context for item in self.items for found_context in self.contexts(item)] ))

    # Join all items and use one regex.findall
    return sorted(set( self._context_regex.findall(" ".join(self.items))))

  def all_projects(self):
    # List comprehension
    # return sorted(set( [project for item in self.items for project in self.projects(item)] ))

    # Join all items and use one regex.findall
    return sorted(set( self._project_regex.findall(" ".join(self.items))))

  def creation_date(self, item):
    match = self._creation_date_regex.search(item)
    if match and len(match.groups()) == 1:
      return match.group(1)
    else:
      raise NoCreationDateError

  def due_date(self, item):
    match = self._due_date_regex.search(item)
    if match and len(match.groups()) == 1:
      return match.group(1)
    else:
      raise NoDueDateError

  def priority(self, item):
    match = self._priority_regex.match(item)
    if match and len(match.groups()) == 1:
      return match.group(1)
    else:
      raise NoPriorityError
