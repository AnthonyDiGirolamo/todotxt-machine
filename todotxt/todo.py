#!/usr/bin/env python
import re

class Todo:
  """Todo items"""

  def __init__(self, todo_items):
    self.items = todo_items
    self._context_regex = re.compile(r'\s*(@\S+)\s*')
    self._project_regex = re.compile(r'\s*(\+\S+)\s*')

  def contexts(self, item):
    return self._context_regex.findall(item)

  def projects(self, item):
    return self._project_regex.findall(item)

  def all_contexts(self):
    all_contexts = []
    for item in self.items:
      for found_context in self.contexts(item):
        if found_context not in all_contexts:
          all_contexts.append(found_context)
    return all_contexts

