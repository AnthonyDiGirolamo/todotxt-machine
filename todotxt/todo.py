#!/usr/bin/env python
import re

from todotxt.terminal_operations import TerminalOperations

# class NoCreationDateError(Exception):
#   pass
# class NoDueDateError(Exception):
#   pass
# class NoPriorityError(Exception):
#   pass

class Todo:
    """Single Todo item"""

    def __init__(self, item, index,
            colored="", priority="", contexts=[], projects=[],
            creation_date="", due_date="", completed_date=""):
        self.raw            = item
        self.raw_index      = index
        self.priority       = priority
        self.contexts       = contexts
        self.projects       = projects
        self.creation_date  = creation_date
        self.due_date       = due_date
        self.completed_date = completed_date
        self.colored        = self.highlight()

    def __repr__(self):
        return repr({"raw": self.raw,
                "colored": self.colored,
                "raw_index": self.raw_index,
                "priority": self.priority,
                "contexts": self.contexts,
                "projects": self.projects,
                "creation_date": self.creation_date,
                "due_date": self.due_date,
                "completed_date": self.completed_date})

    def highlight(self):
        colored = self.raw

        for context in self.contexts:
            colored = colored.replace(context, "{}{}{}".format(
                TerminalOperations.foreground_color(None, 1),
                context,
                TerminalOperations.foreground_color(None, 13),
            ))

        for project in self.projects:
            colored = colored.replace(project, "{}{}{}".format(
                TerminalOperations.foreground_color(None, 4),
                project,
                TerminalOperations.foreground_color(None, 13),
            ))

        colored = colored.replace(self.creation_date, "{}{}{}".format(
            TerminalOperations.foreground_color(None, 2),
            self.creation_date,
            TerminalOperations.foreground_color(None, 13),
        ), 1)
        return colored

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
        self._priority_regex      = re.compile(r'\(([A-Z])\) ')
        self._completed_regex     = re.compile(r'^x (\d\d\d\d-\d\d-\d\d)')
        self._context_regex_highlighing = re.compile(r'(\s*)(@\S+)(\s*)')
        self._project_regex_highlighing = re.compile(r'(\s*)(\+\S+)(\s*)')
        self.parse_raw_entries()

    def __iter__(self):
        self.index = -1
        return self

    def __next__(self):
        self.index = self.index + 1
        if self.index == len(self.todo_items):
            raise StopIteration
        return self.todo_items[self.index]

    def __repr__(self):
        return repr( [i for i in self.todo_items] )

    def parse_raw_entries(self):
        self.todo_items = [
            Todo(todo, index,
                contexts       = self.contexts(todo),
                projects       = self.projects(todo),
                priority       = self.priority(todo),
                creation_date  = self.creation_date(todo),
                due_date       = self.due_date(todo),
                completed_date = self.completed(todo))
            for index, todo in enumerate(self.raw_items) ]

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
        return match.group(1) if match else ""

    def due_date(self, item):
        match = self._due_date_regex.search(item)
        return match.group(1) if match else ""

    def priority(self, item):
        match = self._priority_regex.match(item)
        return match.group(1) if match else ""

    def completed(self, item):
        match = self._completed_regex.match(item)
        return match.group(1) if match else False

    def sorted(self, reversed_sort=False):
        self.todo_items.sort( key=lambda todo: todo.raw, reverse=reversed_sort )

    def sorted_reverse(self):
        self.sorted(reversed_sort=True)

    def sorted_raw(self):
        self.todo_items.sort( key=lambda todo: todo.raw_index )

    def filter_context(self, context):
        return [item for item in self.todo_items if context in item.contexts]

    def filter_project(self, project):
        return [item for item in self.todo_items if project in item.projects]


