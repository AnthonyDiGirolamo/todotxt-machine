#!/usr/bin/env python
# coding=utf-8

import urwid
import collections

class MenuButton(urwid.Button):
    def __init__(self, todo, colorscheme, parent_ui, editing=False, wrapping='clip', border='no border'):
        super(MenuButton, self).__init__("")
        self.todo        = todo
        self.wrapping    = wrapping
        self.border      = border
        self.colorscheme = colorscheme
        self.parent_ui   = parent_ui
        self.editing     = editing
        # urwid.connect_signal(self, 'click', callback)
        if editing:
            self.edit_item()
        else:
            self.update_todo()

    def selectable(self):
        return True

    def update_todo(self):
        text = urwid.Text(self.todo.colored, wrap=self.wrapping)
        if self.border == 'bordered':
            text = urwid.LineBox(text)
        self._w = urwid.AttrMap( urwid.AttrMap(
            text,
            None, 'selected'),
            None, self.colorscheme.focus_map)

    def edit_item(self):
        self.editing = True
        self._w = urwid.Edit(caption="", edit_text=self.todo.raw)

    def save_item(self):
        self.todo.update(self._w.edit_text.strip())
        self.update_todo()
        self.parent_ui.update_filter_panel(new_contexts=self.todo.contexts, new_projects=self.todo.projects)
        self.editing = False

    def keypress(self, size, key):
        if self.editing:
            if key in ['down', 'up']:
                return None # don't pass up or down to the ListBox
            elif key is 'enter':
                self.save_item()
                return key
            else:
                return self._w.keypress(size, key)
        else:
            if key in ['enter', 'e', 'A']:
                self.edit_item()
                return key
            else:
                return key

class UrwidUI:
    def __init__(self, todos, colorscheme):
        self.wrapping    = collections.deque(['clip', 'space'])
        self.border      = collections.deque(['no border', 'bordered'])

        self.todos       = todos

        self.colorscheme = colorscheme
        self.palette     = [ (key, '', '', '', value['fg'], value['bg']) for key, value in self.colorscheme.colors.items() ]

        self.active_projects = []
        self.active_contexts = []

        self.help_panel_is_open    = False
        self.filter_panel_is_open  = False
        self.filtering             = False
        self.searching             = False

    def move_selection_down(self):
        self.listbox.keypress((0, self.loop.screen_size[1]-2), 'down')

    def move_selection_up(self):
        self.listbox.keypress((0, self.loop.screen_size[1]-2), 'up')

    def toggle_help_panel(self, button=None):
        if self.filter_panel_is_open:
            self.toggle_filter_panel()
        if self.help_panel_is_open:
            self.view.contents.pop()
            self.help_panel_is_open = False
        else:
            self.help_panel = self.create_help_panel()
            self.view.contents.append( (self.help_panel, self.view.options(width_type='weight', width_amount=2)) )
            self.view.set_focus(1)
            self.help_panel_is_open = True

    def toggle_filter_panel(self, button=None):
        if self.help_panel_is_open:
            self.toggle_help_panel()
        if self.filter_panel_is_open:
            self.view.contents.pop()
            self.filter_panel_is_open = False
        else:
            self.filter_panel = self.create_filter_panel()
            self.view.contents.append( (self.filter_panel, self.view.options(width_type='weight', width_amount=1)) )
            self.filter_panel_is_open = True

    def toggle_wrapping(self, button=None):
        self.wrapping.rotate(1)
        for widget in self.listbox.body:
            widget.wrapping = self.wrapping[0]
            widget.update_todo()

    def toggle_border(self, button=None):
        self.border.rotate(1)
        for widget in self.listbox.body:
            widget.border = self.border[0]
            widget.update_todo()

    def swap_down(self):
        focus, focus_index = self.listbox.get_focus()
        if not self.filtering:
            if focus_index+1 < len(self.listbox.body):
                self.todos.swap(focus_index, focus_index + 1)
                self.listbox.body[focus_index].todo = self.todos[focus_index]
                self.listbox.body[focus_index+1].todo = self.todos[focus_index+1]
                self.listbox.body[focus_index].update_todo()
                self.listbox.body[focus_index+1].update_todo()
                self.move_selection_down()

    def swap_up(self):
        focus, focus_index = self.listbox.get_focus()
        if not self.filtering:
            if focus_index > 0:
                self.todos.swap(focus_index, focus_index - 1)
                self.listbox.body[focus_index].todo = self.todos[focus_index]
                self.listbox.body[focus_index-1].todo = self.todos[focus_index-1]
                self.listbox.body[focus_index].update_todo()
                self.listbox.body[focus_index-1].update_todo()
                self.move_selection_up()

    def save_todos(self, button=None):
        self.todos.save()
        self.update_header("Saved")

    def reload_todos(self, button=None):
        for i in range(len(self.listbox.body)-1, -1, -1):
            self.listbox.body.pop(i)

        self.todos.reload_from_file()

        for t in self.todos.todo_items:
            self.listbox.body.append( MenuButton(t, self.colorscheme, self, wrapping=self.wrapping[0], border=self.border[0]) )

        self.update_header("Reloaded")

    def keystroke(self, input):
        focus, focus_index = self.listbox.get_focus()

        if input in ('q', 'Q'):
            raise urwid.ExitMainLoop()

        # Movement
        elif input is 'g':
            self.listbox.set_focus(0)
        elif input is 'G':
            self.listbox.set_focus(len(self.listbox.body)-1)
        elif input is 'k':
            self.move_selection_up()
        elif input is 'j':
            self.move_selection_down()
        elif input is 'J':
            self.swap_down()
        elif input is 'K':
            self.swap_up()

        # View options
        elif input in ['h', '?']:
            self.toggle_help_panel()
        elif input is 'f':
            self.toggle_filter_panel()
        elif input is 'F':
            self.clear_filters()
        elif input is 'w':
            self.toggle_wrapping()
        elif input is 'b':
            self.toggle_border()

        # Editing
        elif input is 'x':
            i = focus.todo.raw_index

            # if self.sorting > 0:
            #     i = self.selected_item

            if self.todos[i].is_complete():
                self.todos[i].incomplete()
            else:
                self.todos[i].complete()
            focus.update_todo()
            self.update_header()
        elif input is 'D':
            if self.todos.todo_items:
                i = focus.todo.raw_index
                self.todos.delete(i)
                del self.listbox.body[focus_index]
                self.update_header()

        elif input is 'n':
            self.add_new_todo(position='append')
        elif input is 'O':
            self.add_new_todo(position='insert_before')
        elif input is 'o':
            self.add_new_todo(position='insert_after')

        # Save current file
        elif input is 'S':
            self.save_todos()

        # Reload original file
        elif input is 'R':
            self.reload_todos()

    def add_new_todo(self, position=False):
        focus_index = self.listbox.get_focus()[1]
        if self.filtering:
            position = 'append'

        if position is 'append':
            new_index = self.todos.append('', add_creation_date=False)
            self.listbox.body.append(MenuButton(self.todos[new_index], self.colorscheme, self, editing=True, wrapping=self.wrapping[0], border=self.border[0]))
        else:
            if position is 'insert_after':
                new_index = self.todos.insert(focus_index+1, '', add_creation_date=False)
            elif position is 'insert_before':
                new_index = self.todos.insert(focus_index, '', add_creation_date=False)

            self.listbox.body.insert(new_index, MenuButton(self.todos[new_index], self.colorscheme, self, editing=True, wrapping=self.wrapping[0], border=self.border[0]))

        if position:
            # import ipdb; ipdb.set_trace()
            # FIXME
            if self.filtering:
                self.listbox.set_focus(len(self.listbox.body)-1)
            else:
                self.listbox.set_focus(new_index)
            # edit_widget = self.listbox.body[new_index]._w
            # edit_widget.edit_text += ' '
            # edit_widget.set_edit_pos(len(self.todos[new_index].raw) + 1)
            self.update_header()

    def create_header(self, message=""):
        return urwid.AttrMap(
            urwid.Columns( [
                urwid.Text( [
                    ('header_todo_count', " {0} Todos ".format(self.todos.__len__())),
                    ('header_todo_pending_count', " {0} Pending ".format(self.todos.pending_items_count())),
                    ('header_todo_done_count', " {0} Done ".format(self.todos.done_items_count())),
                ]),
                # urwid.Text( " todotxt-machine ", align='center' ),
                urwid.Text( ('header_file', "{0}  {1} ".format(message, self.todos.file_path)), align='right' )
            ]), 'header')

    def create_footer(self):
        if self.searching:
            return urwid.AttrMap(urwid.Columns([
                urwid.Text(''),
                # (11, urwid.AttrMap(urwid.Button('Filters', on_press=self.toggle_filter_panel), 'dialog_button', 'plain_selected') )
            ]), 'footer')

    def create_help_panel(self):
        return urwid.AttrMap(
            urwid.LineBox(
            urwid.Padding(
            urwid.ListBox(
                [ urwid.Divider() ] +
                [ urwid.Text("""General

h, ?         - display this help message
q            - quit and save
S            - save current todo file
R            - reload the todo file (discarding changes)

Movement

mouse click  - select any todo, checkbox or button
j, down      - move selection down
k, up        - move selection up
g, page up   - move selection to the top item
G, page down - move selection to the bottom item
left, right  - move selection between todos and filter panel

Manipulating Todo Items

x            - complete / un-complete selected todo item
n            - add a new todo to the end of the list
o            - add a todo after the selected todo (when not filtering)
O            - add a todo before the selected todo (when not filtering)
enter, A, e  - edit the selected todo
D            - delete the selected todo
J            - swap with item below
K            - swap with item above

Filtering

f            - open the filtering panel
F            - clear any active filters
""")]
            ),
            left=1, right=1, min_width=10 ), title='Key Bindings'), 'dialog_color')

    def create_filter_panel(self):
        w = urwid.AttrMap(
            # urwid.LineBox(
            urwid.Padding(
            urwid.ListBox(
                [ urwid.Divider() ] +
                [ urwid.LineBox(urwid.Pile(
                    [urwid.AttrWrap(urwid.CheckBox(c, state=(c in self.active_contexts), on_state_change=self.checkbox_clicked, user_data=['context', c]), 'context_dialog_color', 'context_selected') for c in self.todos.all_contexts()] +
                    [ urwid.Divider(u'─') ] +
                    [urwid.AttrWrap(urwid.CheckBox(p, state=(p in self.active_projects), on_state_change=self.checkbox_clicked, user_data=['project', p]), 'project_dialog_color', 'project_selected') for p in self.todos.all_projects()] +
                    [ urwid.Divider(u'─') ] +
                    [ urwid.AttrMap(urwid.Button('[F] Clear Filters', on_press=self.clear_filters), 'dialog_button', 'plain_selected') ] ), title='Contexts & Projects') ] +
                # [ urwid.Divider() ] +
                [ urwid.LineBox(urwid.Pile(
                    [ urwid.AttrMap(urwid.Button('[w] Toggle Wrapping', on_press=self.toggle_wrapping), 'dialog_button', 'plain_selected') ] +
                    [ urwid.AttrMap(urwid.Button('[b] Toggle Borders', on_press=self.toggle_border), 'dialog_button', 'plain_selected') ] +
                    [ urwid.Divider() ] +
                    [ urwid.AttrMap(urwid.Button('[R] Reload Todo.txt File', on_press=self.reload_todos), 'dialog_button', 'plain_selected') ] +
                    [ urwid.Divider() ] +
                    [ urwid.AttrMap(urwid.Button('[S] Save Todo.txt File', on_press=self.save_todos), 'dialog_button', 'plain_selected') ]
                ), title='Options') ] +
                [ urwid.Divider() ] +
                [ urwid.AttrMap(urwid.Button('[f] Close', on_press=self.toggle_filter_panel), 'dialog_button', 'plain_selected') ] +
                [ urwid.Divider() ],
            ),
            left=1, right=1, min_width=10 )
            ,
        'dialog_color')

        bg = urwid.AttrWrap(urwid.SolidFill(u" "), 'dialog_background') # u"\u2592"
        shadow = urwid.AttrWrap(urwid.SolidFill(u" "), 'dialog_shadow')

        bg = urwid.Overlay( shadow, bg,
            ('fixed left', 3), ('fixed right', 1),
            ('fixed top', 2), ('fixed bottom', 1))
        w = urwid.Overlay( w, bg,
            ('fixed left', 2), ('fixed right', 3),
            ('fixed top', 1), ('fixed bottom', 2))
        return w

    def clear_filters(self, button=None):
        for i in range(len(self.listbox.body)-1, -1, -1):
            self.listbox.body.pop(i)

        for t in self.todos.todo_items:
            self.listbox.body.append( MenuButton(t, self.colorscheme, self, wrapping=self.wrapping[0], border=self.border[0]) )

        self.active_projects = []
        self.active_contexts = []
        self.filtering = False
        self.view.set_focus(0)
        self.update_filter_panel()

    def checkbox_clicked(self, checkbox, state, data):
        if state:
            if data[0] == 'context':
                self.active_contexts.append(data[1])
            else:
                self.active_projects.append(data[1])
        else:
            if data[0] == 'context':
                self.active_contexts.remove(data[1])
            else:
                self.active_projects.remove(data[1])
        self.filter_todo_list()
        self.view.set_focus(0)

    def filter_todo_list(self):
        for i in range(len(self.listbox.body)-1, -1, -1):
            self.listbox.body.pop(i)

        for t in self.todos.filter_contexts_and_projects(self.active_contexts, self.active_projects):
            self.listbox.body.append( MenuButton(t, self.colorscheme, self, wrapping=self.wrapping[0], border=self.border[0]) )

        self.filtering = True

    def update_filter_panel(self, new_contexts=[], new_projects=[]):
        for c in new_contexts:
            self.active_contexts.append(c)
        for p in new_projects:
            self.active_projects.append(p)

        self.filter_panel = self.create_filter_panel()
        if len(self.view.widget_list) > 1:
            self.view.widget_list.pop()
            self.view.widget_list.append(self.filter_panel)

    def update_header(self, message=""):
        self.view[0].header = self.create_header(message)

    def update_footer(self, message=""):
        self.view[0].footer = self.create_footer()

    def main(self):
        self.header = self.create_header()
        self.footer = self.create_footer()

        self.listbox = urwid.ListBox(urwid.SimpleListWalker(
            [MenuButton(t, self.colorscheme, self) for t in self.todos.todo_items]
        ))
        self.view = urwid.Columns([
            ('weight', 2, urwid.Frame(urwid.AttrMap(self.listbox, 'plain'), header=self.header, footer=self.footer) )
         ])

        self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.keystroke)
        self.loop.screen.set_terminal_properties(colors=256)
        self.loop.run()
