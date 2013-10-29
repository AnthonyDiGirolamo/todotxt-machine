#!/usr/bin/env python
import re
from datetime import date

from todotxt.terminal_operations import TerminalOperations

class Todo:
    """Single Todo item"""

    colors = {
        "foreground":    TerminalOperations.foreground_color(250),
        "completed":     TerminalOperations.foreground_color(59),
        "context":       TerminalOperations.foreground_color(118),
        "project":       TerminalOperations.foreground_color(161),
        "creation_date": TerminalOperations.foreground_color(135),
        "due_date":      TerminalOperations.foreground_color(208),
        "priority": {
            "A": TerminalOperations.foreground_color(int("0xa7",16)),
            "B": TerminalOperations.foreground_color(int("0xad",16)),
            "C": TerminalOperations.foreground_color(int("0xb9",16)),
            "D": TerminalOperations.foreground_color(int("0x4d",16)),
            "E": TerminalOperations.foreground_color(int("0x50",16)),
            "F": TerminalOperations.foreground_color(int("0x3e",16)),
        }
    }

    def __init__(self, item, index,
            colored="", priority="", contexts=[], projects=[],
            creation_date="", due_date="", completed_date=""):
        self.raw            = item.strip()
        self.raw_index      = index
        self.creation_date  = creation_date
        self.priority       = priority
        self.contexts       = contexts
        self.projects       = projects
        self.due_date       = due_date
        self.completed_date = completed_date
        self.colored        = self.highlight()
        self.colored_length = TerminalOperations.length_ignoring_escapes(self.colored)

    def update(self, item):
        self.raw            = item.strip()
        self.priority       = Todos.priority(item)
        self.contexts       = Todos.contexts(item)
        self.projects       = Todos.projects(item)
        self.creation_date  = Todos.creation_date(item)
        self.due_date       = Todos.due_date(item)
        self.completed_date = Todos.completed_date(item)
        self.colored        = self.highlight()
        self.colored_length = TerminalOperations.length_ignoring_escapes(self.colored)

    def __repr__(self):
        return repr({
            "raw":            self.raw,
            "colored":        self.colored,
            "raw_index":      self.raw_index,
            "priority":       self.priority,
            "contexts":       self.contexts,
            "projects":       self.projects,
            "creation_date":  self.creation_date,
            "due_date":       self.due_date,
            "completed_date": self.completed_date
        })

    def highlight(self, line=""):
        colors = Todo.colors
        colored = self.raw if line == "" else line

        if colored[:2] == "x ":
            colored = colors['completed'] + colored
        else:
            line_color = colors["foreground"]
            if self.priority:
                line_color = colors["priority"][self.priority] if self.priority in "ABCDEF" else colors["foreground"]
                colored = line_color + colored

            for context in self.contexts:
                colored = colored.replace(context, "{}{}{}".format(
                    colors["context"], context, line_color ))

            for project in self.projects:
                colored = colored.replace(project, "{}{}{}".format(
                    colors["project"], project, line_color ))

            colored = colored.replace(self.creation_date, "{}{}{}".format(
                colors["creation_date"], self.creation_date, line_color), 1)

        return colored

    def is_complete(self):
        if self.raw[0:2] == "x ":
            return True
        elif self.completed_date == "":
            return False
        else:
            return True

    def complete(self):
        today = date.today()
        self.raw = "x {} ".format(today) + self.raw
        self.completed_date = "{}".format(today)

    def incomplete(self):
        self.raw = re.sub(Todos._completed_regex, "", self.raw)
        self.completed_date = ""

    def add_creation_date(self):
        if self.creation_date == "":
            p = "({}) ".format(self.priority) if self.priority != "" else ""
            self.update("{}{} {}".format(p, date.today(), self.raw.replace(p, "")))


class Todos:
    """Todo items"""
    _context_regex       = re.compile(r'\s*(@\S+)\s*')
    _project_regex       = re.compile(r'\s*(\+\S+)\s*')
    _creation_date_regex = re.compile(r'^'
                                      r'(?:x \d\d\d\d-\d\d-\d\d )?'
                                      r'(?:\(\w\) )?'
                                      r'(\d\d\d\d-\d\d-\d\d)\s*')
    _due_date_regex      = re.compile(r'\s*due:(\d\d\d\d-\d\d-\d\d)\s*')
    _priority_regex      = re.compile(r'\(([A-Z])\) ')
    _completed_regex     = re.compile(r'^x (\d\d\d\d-\d\d-\d\d) ')

    def __init__(self, todo_items):
        self.update(todo_items)

    def update(self, todo_items):
        self.raw_items = todo_items
        self.parse_raw_entries()

    def append(self, item, add_creation_date=True):
        self.insert(len(self.todo_items), item, add_creation_date)

    def insert(self, index, item, add_creation_date=True):
        self.todo_items.insert(index, self.create_todo(item, index) )
        self.update_raw_indices()
        newtodo = self.todo_items[index]
        if add_creation_date and newtodo.creation_date == "":
            newtodo.add_creation_date()
        self.raw_items.append(newtodo.raw)

    def delete(self, index):
        del self.todo_items[index]
        del self.raw_items[index]
        self.update_raw_indices()

    def __iter__(self):
        self.index = -1
        return self

    def __next__(self):
        self.index = self.index + 1
        if self.index == len(self.todo_items):
            raise StopIteration
        return self.todo_items[self.index]

    def next(self):
        self.index = self.index + 1
        if self.index == len(self.todo_items):
            raise StopIteration
        return self.todo_items[self.index]

    def __len__(self):
        return len(self.todo_items)

    def __getitem__(self, index):
        return self.todo_items[index]

    def __repr__(self):
        return repr( [i for i in self.todo_items] )

    def create_todo(self, todo, index):
        return Todo(todo, index,
            contexts       = Todos.contexts(todo),
            projects       = Todos.projects(todo),
            priority       = Todos.priority(todo),
            creation_date  = Todos.creation_date(todo),
            due_date       = Todos.due_date(todo),
            completed_date = Todos.completed_date(todo))

    def parse_raw_entries(self):
        self.todo_items = [
            self.create_todo(todo, index)
            for index, todo in enumerate(self.raw_items) ]

    def update_raw_indices(self):
        for index, todo in enumerate(self.todo_items):
            todo.raw_index = index

    @staticmethod
    def contexts(item):
        return sorted( Todos._context_regex.findall(item) )

    @staticmethod
    def projects(item):
        return sorted( Todos._project_regex.findall(item) )

    @staticmethod
    def creation_date(item):
        match = Todos._creation_date_regex.search(item)
        return match.group(1) if match else ""

    @staticmethod
    def due_date(item):
        match = Todos._due_date_regex.search(item)
        return match.group(1) if match else ""

    @staticmethod
    def priority(item):
        match = Todos._priority_regex.match(item)
        return match.group(1) if match else ""

    @staticmethod
    def completed_date(item):
        match = Todos._completed_regex.match(item)
        return match.group(1) if match else ""

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
        return sorted(set( Todos._context_regex.findall(" ".join(self.raw_items))))

    def all_projects(self):
        # List comprehension
        # return sorted(set( [project for item in self.raw_items for project in self.projects(item)] ))

        # Join all items and use one regex.findall
        return sorted(set( Todos._project_regex.findall(" ".join(self.raw_items))))

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

    def filter_context_and_project(self, context, project):
        return [item for item in self.todo_items if project in item.projects and context in item.contexts]

