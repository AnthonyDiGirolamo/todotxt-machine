#!/usr/bin/env python
import re
from datetime import date

from todotxt.terminal_operations import TerminalOperations

class Todo:
    """Single Todo item"""

    # ! SOLARIZED HEX     16/8 TERMCOL       XTERM/HEX   L*A*B      RGB         HSB
    # ! --------- ------- ---- -------       ----------- ---------- ----------- -----------
    # ! base03    #002b36  8/4 brightblack   234 #1c1c1c 15 -12 -12   0  43  54 193 100  21
    # ! base02    #073642  0/4 black         235 #262626 20 -12 -12   7  54  66 192  90  26
    # ! base01    #586e75 10/7 brightgreen   240 #585858 45 -07 -07  88 110 117 194  25  46
    # ! base00    #657b83 11/7 brightyellow  241 #626262 50 -07 -07 101 123 131 195  23  51
    # ! base0     #839496 12/6 brightblue    244 #808080 60 -06 -03 131 148 150 186  13  59
    # ! base1     #93a1a1 14/4 brightcyan    245 #8a8a8a 65 -05 -02 147 161 161 180   9  63
    # ! base2     #eee8d5  7/7 white         254 #e4e4e4 92 -00  10 238 232 213  44  11  93
    # ! base3     #fdf6e3 15/7 brightwhite   230 #ffffd7 97  00  10 253 246 227  44  10  99
    # ! yellow    #b58900  3/3 yellow        136 #af8700 60  10  65 181 137   0  45 100  71
    # ! orange    #cb4b16  9/3 brightred     166 #d75f00 50  50  55 203  75  22  18  89  80
    # ! red       #dc322f  1/1 red           160 #d70000 50  65  45 220  50  47   1  79  86
    # ! magenta   #d33682  5/5 magenta       125 #af005f 50  65 -05 211  54 130 331  74  83
    # ! violet    #6c71c4 13/5 brightmagenta  61 #5f5faf 50  15 -45 108 113 196 237  45  77
    # ! blue      #268bd2  4/4 blue           33 #0087ff 55 -10 -45  38 139 210 205  82  82
    # ! cyan      #2aa198  6/6 cyan           37 #00afaf 60 -35 -05  42 161 152 175  74  63
    # ! green     #859900  2/2 green          64 #5f8700 60 -20  65 133 153   0  68 100  60

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
        self.priority       = priority
        self.contexts       = contexts
        self.projects       = projects
        self.creation_date  = creation_date
        self.due_date       = due_date
        self.completed_date = completed_date
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

    def parse_raw_entries(self):
        self.todo_items = [
            Todo(todo, index,
                contexts       = self.contexts(todo),
                projects       = self.projects(todo),
                priority       = self.priority(todo),
                creation_date  = self.creation_date(todo),
                due_date       = self.due_date(todo),
                completed_date = self.completed_date(todo))
            for index, todo in enumerate(self.raw_items) ]

    def contexts(self, item):
        return sorted( Todos._context_regex.findall(item) )

    def projects(self, item):
        return sorted( Todos._project_regex.findall(item) )

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

    def creation_date(self, item):
        match = Todos._creation_date_regex.search(item)
        return match.group(1) if match else ""

    def due_date(self, item):
        match = Todos._due_date_regex.search(item)
        return match.group(1) if match else ""

    def priority(self, item):
        match = Todos._priority_regex.match(item)
        return match.group(1) if match else ""

    def completed_date(self, item):
        match = Todos._completed_regex.match(item)
        return match.group(1) if match else ""

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

