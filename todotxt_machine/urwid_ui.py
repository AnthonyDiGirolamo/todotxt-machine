#!/usr/bin/env python
# coding=utf-8

import urwid
import collections

# Modified from http://wiki.goffi.org/wiki/Urwid-satext/en
class AdvancedEdit(urwid.Edit):
    """Edit box with some custom improvments
    new chars:
              - C-a: like 'home'
              - C-e: like 'end'
              - C-k: remove everything on the right of the cursor
              - C-w: remove the word on the back"""

    def __init__(self, parent_ui, *args, **kwargs):
        self.parent_ui = parent_ui
        super(AdvancedEdit, self).__init__(*args, **kwargs)

    def setCompletionMethod(self, callback):
        """Define method called when completion is asked
        @callback: method with 2 arguments:
                    - the text to complete
                    - if there was already a completion, a dict with
                        - 'completed':last completion
                        - 'completion_pos': cursor position where the completion starts
                        - 'position': last completion cursor position
                      this dict must be used (and can be filled) to find next completion)
                   and which return the full text completed"""
        self.completion_cb = callback
        self.completion_data = {}

    def keypress(self, size, key):
        # import ipdb; ipdb.set_trace()
        if key == 'ctrl a':
            key = 'home'
        elif key == 'ctrl e':
            key = 'end'
        elif key == 'ctrl k':
            self.parent_ui.yanked_text = self.edit_text[self.edit_pos:]
            self._delete_highlighted()
            self.set_edit_text(self.edit_text[:self.edit_pos])
        elif key == 'ctrl y':
            self.set_edit_text(
                self.edit_text[:self.edit_pos] +
                self.parent_ui.yanked_text +
                self.edit_text[self.edit_pos:])
            self.set_edit_pos(self.edit_pos + len(self.parent_ui.yanked_text))
        elif key == 'ctrl w':
            before = self.edit_text[:self.edit_pos]
            pos = before.rstrip().rfind(" ")+1
            self.parent_ui.yanked_text = self.edit_text[pos:self.edit_pos]
            self.set_edit_text(before[:pos] + self.edit_text[self.edit_pos:])
            self.set_edit_pos(pos)
        elif key in ['meta b', 'ctrl b']:
            before = self.edit_text[:self.edit_pos]
            pos = before.rstrip().rfind(" ")+1
            self.set_edit_pos(pos)
        elif key in ['meta f', 'ctrl f']:
            after = self.edit_text[self.edit_pos:]
            pos = after.rstrip().find(" ")+1
            self.set_edit_pos(self.edit_pos+pos)
        elif key == 'tab':
            try:
                before = self.edit_text[:self.edit_pos]
                if self.completion_data:
                    if (not self.completion_data['completed']
                        or self.completion_data['position'] != self.edit_pos
                        or not before.endswith(self.completion_data['completed'])):
                        self.completion_data.clear()
                    else:
                        before = before[:-len(self.completion_data['completed'])]
                complet = self.completion_cb(before, self.completion_data)
                self.completion_data['completed'] = complet[len(before):]
                self.set_edit_text(complet+self.edit_text[self.edit_pos:])
                self.set_edit_pos(len(complet))
                self.completion_data['position'] = self.edit_pos
                return
            except AttributeError:
                #No completion method defined
                pass
        return super(AdvancedEdit, self).keypress(size, key)

class SearchWidget(urwid.Edit):
    def __init__(self, parent_ui, edit_text=""):
        self.parent_ui = parent_ui
        super(SearchWidget, self).__init__(edit_text=edit_text)

    def keypress(self, size, key):
        if key == 'enter':
            self.parent_ui.finalize_search()
        return super(SearchWidget, self).keypress(size, key)

class TodoWidget(urwid.Button):
    def __init__(self, todo, colorscheme, parent_ui, editing=False, wrapping='clip', border='no border'):
        super(TodoWidget, self).__init__("")
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
        if self.parent_ui.searching and self.parent_ui.search_string:
            text = urwid.Text(self.todo.highlight_search_matches(), wrap=self.wrapping)
        else:
            if self.border == 'bordered':
                text = urwid.Text(self.todo.highlight(show_due_date=False, show_contexts=False, show_projects=False), wrap=self.wrapping)
            else:
                text = urwid.Text(self.todo.colored, wrap=self.wrapping)

        if self.border == 'bordered':
            lt=''
            if self.todo.due_date:
                lt = ('due_date', "due:{0}".format(self.todo.due_date))
            t = []
            t.append( ('context', ' '.join(self.todo.contexts)) )
            if self.todo.contexts and self.todo.projects:
                t.append(' ')
            t.append( ('project', ' '.join(self.todo.projects)) )
            bc = 'plain'
            if self.todo.priority and self.todo.priority in "ABCDEF":
                bc = "priority_{0}".format(self.todo.priority.lower())
            text = TodoLineBox(text, top_left_title=lt, bottom_right_title=t, border_color=bc, )
        self._w = urwid.AttrMap( urwid.AttrMap(
            text,
            None, 'selected'),
            None, self.colorscheme.focus_map)

    def edit_item(self):
        self.editing = True
        self.edit_widget = AdvancedEdit(self.parent_ui, caption="", edit_text=self.todo.raw)
        self.edit_widget.setCompletionMethod(self.completions)
        self._w = urwid.AttrMap(self.edit_widget, 'plain_selected')

    def completions(self, text, completion_data={}):
        space = text.rfind(" ")
        start = text[space+1:]
        words = self.parent_ui.todos.all_contexts() + self.parent_ui.todos.all_projects()
        try:
            start_idx=words.index(completion_data['last_word'])+1
            if start_idx == len(words):
                start_idx = 0
        except (KeyError,ValueError):
            start_idx = 0
        for idx in list(range(start_idx,len(words))) + list(range(0,start_idx)):
            if words[idx].lower().startswith(start.lower()):
                completion_data['last_word'] = words[idx]
                return text[:space+1] + words[idx] + (': ' if space < 0 else '')
        return text

    def save_item(self):
        self.todo.update(self._w.original_widget.edit_text.strip())
        self.update_todo()
        if self.parent_ui.filter_panel_is_open:
            self.parent_ui.update_filters(new_contexts=self.todo.contexts, new_projects=self.todo.projects)
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

class TodoLineBox(urwid.WidgetDecoration, urwid.WidgetWrap):

    def __init__(self, original_widget, top_left_title="", bottom_right_title="", border_color='plain',
                 tlcorner=u'┌', tline=u'─', lline=u'│',
                 trcorner=u'┐', blcorner=u'└', rline=u'│',
                 bline=u'─', brcorner=u'┘'):
        """
        Draw a line around original_widget.

        Use 'title' to set an initial title text with will be centered
        on top of the box.

        You can also override the widgets used for the lines/corners:
            tline: top line
            bline: bottom line
            lline: left line
            rline: right line
            tlcorner: top left corner
            trcorner: top right corner
            blcorner: bottom left corner
            brcorner: bottom right corner

        """

        tline, bline = urwid.AttrMap(urwid.Divider(tline), border_color),   urwid.AttrMap(urwid.Divider(bline), border_color)
        lline, rline = urwid.AttrMap(urwid.SolidFill(lline), border_color), urwid.AttrMap(urwid.SolidFill(rline), border_color)
        tlcorner, trcorner = urwid.AttrMap(urwid.Text(tlcorner), border_color), urwid.AttrMap(urwid.Text(trcorner), border_color)
        blcorner, brcorner = urwid.AttrMap(urwid.Text(blcorner), border_color), urwid.AttrMap(urwid.Text(brcorner), border_color)

        self.ttitle_widget = urwid.Text(top_left_title)
        self.tline_widget = urwid.Columns([
            ('fixed', 1, tline),
            ('flow', self.ttitle_widget),
            tline,
        ])
        self.btitle_widget = urwid.Text(bottom_right_title)
        self.bline_widget = urwid.Columns([
            bline,
            ('flow', self.btitle_widget),
            ('fixed', 1, bline),
        ])

        middle = urwid.Columns([
            ('fixed', 1, lline),
            original_widget,
            ('fixed', 1, rline),
        ], box_columns=[0, 2], focus_column=1)

        top = urwid.Columns([
            ('fixed', 1, tlcorner),
            self.tline_widget,
            ('fixed', 1, trcorner)
        ])

        bottom = urwid.Columns([
            ('fixed', 1, blcorner),
            self.bline_widget,
            ('fixed', 1, brcorner)
        ])

        pile = urwid.Pile([('flow', top), middle, ('flow', bottom)], focus_item=1)

        urwid.WidgetDecoration.__init__(self, original_widget)
        urwid.WidgetWrap.__init__(self, pile)


class ViPile(urwid.Pile):
    def __init__(self, widget_list, focus_item=None):
        """Pile with Vi-like navigation."""
        super(ViPile, self).__init__(widget_list, focus_item)
        command_map = urwid.command_map.copy()
        command_map['j'] = urwid.CURSOR_DOWN
        command_map['k'] = urwid.CURSOR_UP
        self._command_map = command_map


class ViColumns(urwid.Columns):
    def __init__(self, widget_list, dividechars=0, focus_column=None, min_width=1, box_columns=None):
        super(ViColumns, self).__init__(widget_list, dividechars, focus_column, min_width, box_columns)
        command_map = urwid.command_map.copy()
        command_map['L'] = urwid.CURSOR_RIGHT
        command_map['H'] = urwid.CURSOR_LEFT
        self._command_map = command_map

class ViListBox(urwid.ListBox):
    def __init__(self, *args, **kwargs):
        super(ViListBox, self).__init__(*args, **kwargs)
        command_map = urwid.command_map.copy()
        command_map['j'] = urwid.CURSOR_DOWN
        command_map['k'] = urwid.CURSOR_UP
        self._command_map = command_map

class UrwidUI:
    def __init__(self, todos, colorscheme):
        self.wrapping    = collections.deque(['clip', 'space'])
        self.border      = collections.deque(['no border', 'bordered'])
        self.sorting     = collections.deque(["Unsorted", "Descending", "Ascending"])
        self.sorting_display = {"Unsorted": "-", "Descending": "v", "Ascending": "^"}

        self.todos       = todos

        self.colorscheme = colorscheme
        self.palette     = [ (key, '', '', '', value['fg'], value['bg']) for key, value in self.colorscheme.colors.items() ]

        self.active_projects = []
        self.active_contexts = []

        self.toolbar_is_open       = False
        self.help_panel_is_open    = False
        self.filter_panel_is_open  = False
        self.filtering             = False
        self.searching             = False
        self.search_string         = ''
        self.yanked_text           = ''

    def visible_lines(self):
        lines = self.loop.screen_size[1] - 1 # minus one for the header
        if self.toolbar_is_open:
            lines -= 1
        if self.searching:
            lines -= 1
        return lines

    def move_selection_down(self):
        self.listbox.keypress((0, self.visible_lines()), 'down')

    def move_selection_up(self):
        self.listbox.keypress((0, self.visible_lines()), 'up')

    def move_selection_top(self):
        self.listbox.set_focus(0)

    def move_selection_bottom(self):
        self.listbox.set_focus(len(self.listbox.body)-1)

    def toggle_help_panel(self, button=None):
        if self.filter_panel_is_open:
            self.toggle_filter_panel()
        if self.help_panel_is_open:
            self.view.contents.pop()
            self.help_panel_is_open = False
            # set header line to word-wrap contents
            # for header_column in self.frame.header.original_widget.contents:
            #     header_column[0].set_wrap_mode('space')
        else:
            self.help_panel = self.create_help_panel()
            self.view.contents.append( (self.help_panel, self.view.options(width_type='weight', width_amount=3)) )
            self.view.set_focus(1)
            self.help_panel_is_open = True
            # set header line to clip contents
            # for header_column in self.frame.header.original_widget.contents:
            #     header_column[0].set_wrap_mode('clip')

    def toggle_sorting(self, button=None):
        self.delete_todo_widgets()
        self.sorting.rotate(1)
        if self.sorting[0] == 'Ascending':
            self.todos.sorted()
        elif self.sorting[0] == 'Descending':
            self.todos.sorted_reverse()
        elif self.sorting[0] == 'Unsorted':
            self.todos.sorted_raw()
        self.reload_todos_from_memory()
        self.move_selection_top()
        self.update_header()

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

    def toggle_wrapping(self, checkbox=None, state=None):
        self.wrapping.rotate(1)
        for widget in self.listbox.body:
            widget.wrapping = self.wrapping[0]
            widget.update_todo()
        if self.toolbar_is_open:
            self.update_header()

    def toggle_border(self, checkbox=None, state=None):
        self.border.rotate(1)
        for widget in self.listbox.body:
            widget.border = self.border[0]
            widget.update_todo()
        if self.toolbar_is_open:
            self.update_header()

    def toggle_toolbar(self):
        self.toolbar_is_open = not self.toolbar_is_open
        self.update_header()

    def swap_down(self):
        focus, focus_index = self.listbox.get_focus()
        if not self.filtering and not self.searching:
            if focus_index+1 < len(self.listbox.body):
                self.todos.swap(focus_index, focus_index + 1)
                self.listbox.body[focus_index].todo = self.todos[focus_index]
                self.listbox.body[focus_index+1].todo = self.todos[focus_index+1]
                self.listbox.body[focus_index].update_todo()
                self.listbox.body[focus_index+1].update_todo()
                self.move_selection_down()

    def swap_up(self):
        focus, focus_index = self.listbox.get_focus()
        if not self.filtering and not self.searching:
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

    def archive_done_todos(self):
        if self.todos.archive_done():
            self.delete_todo_widgets()
            self.reload_todos_from_memory()
            self.move_selection_top()
            self.update_header()

    def reload_todos_from_file(self, button=None):
        self.delete_todo_widgets()

        self.todos.reload_from_file()

        for t in self.todos.todo_items:
            self.listbox.body.append( TodoWidget(t, self.colorscheme, self, wrapping=self.wrapping[0], border=self.border[0]) )

        self.update_header("Reloaded")

    def keystroke(self, input):
        focus, focus_index = self.listbox.get_focus()

        if input in ('q', 'Q'):
            raise urwid.ExitMainLoop()

        # Movement
        elif input is 'g':
            self.move_selection_top()
        elif input is 'G':
            self.move_selection_bottom()
        elif input is 'J':
            self.swap_down()
        elif input is 'K':
            self.swap_up()
        elif input is 'tab':
            current_focus = self.frame.get_focus()
            if current_focus == 'body':

                if self.filter_panel_is_open and self.toolbar_is_open:

                    if self.view.focus_position == 1:
                        self.view.focus_position = 0
                        self.frame.focus_position = 'header'
                    elif self.view.focus_position == 0:
                        self.view.focus_position = 1

                elif self.toolbar_is_open:
                    self.frame.focus_position = 'header'

                elif self.filter_panel_is_open:
                    if self.view.focus_position == 1:
                        self.view.focus_position = 0
                    elif self.view.focus_position == 0:
                        self.view.focus_position = 1

            elif current_focus == 'header':
                self.frame.focus_position = 'body'

        # View options
        elif input in ['h', '?']:
            self.toggle_help_panel()
        elif input is 't':
            self.toggle_toolbar()
        elif input is 'f':
            self.toggle_filter_panel()
        elif input is 'F':
            self.clear_filters()
        elif input is 'w':
            self.toggle_wrapping()
        elif input is 'b':
            self.toggle_border()
        elif input is 's':
            self.toggle_sorting()

        elif input is '/':
            self.start_search()
        elif input is 'C':
            if self.searching:
                self.clear_search_term()

        # Editing
        elif input is 'x':
            if focus.todo.is_complete():
                focus.todo.incomplete()
            else:
                focus.todo.complete()
            focus.update_todo()
            self.update_header()

        elif input is 'X':
            self.archive_done_todos()

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
            self.reload_todos_from_file()

    def add_new_todo(self, position=False):
        focus_index = self.listbox.get_focus()[1]
        if self.filtering:
            position = 'append'

        if position is 'append':
            new_index = self.todos.append('', add_creation_date=False)
            self.listbox.body.append(TodoWidget(self.todos[new_index], self.colorscheme, self, editing=True, wrapping=self.wrapping[0], border=self.border[0]))
        else:
            if position is 'insert_after':
                new_index = self.todos.insert(focus_index+1, '', add_creation_date=False)
            elif position is 'insert_before':
                new_index = self.todos.insert(focus_index, '', add_creation_date=False)

            self.listbox.body.insert(new_index, TodoWidget(self.todos[new_index], self.colorscheme, self, editing=True, wrapping=self.wrapping[0], border=self.border[0]))

        if position:
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
                    ('header_todo_count', "{0} Todos ".format(self.todos.__len__())),
                    ('header_todo_pending_count', " {0} Pending ".format(self.todos.pending_items_count())),
                    ('header_todo_done_count', " {0} Done ".format(self.todos.done_items_count())),
                ]),
                # urwid.Text( " todotxt-machine ", align='center' ),
                urwid.Text( ('header_file', "{0}  {1} ".format(message, self.todos.file_path)), align='right' )
            ]), 'header')

    def create_toolbar(self):
        return urwid.AttrMap(urwid.Columns( [
            urwid.Padding(
            urwid.AttrMap(
            urwid.CheckBox([('header_file', 'w'), 'ord wrap'], state=(self.wrapping[0] == 'space'), on_state_change=self.toggle_wrapping),
            'header', 'plain_selected'), right=2 ),

            urwid.Padding(
            urwid.AttrMap(
            urwid.CheckBox([('header_file', 'b'), 'orders'], state=(self.border[0] == 'bordered'), on_state_change=self.toggle_border),
            'header', 'plain_selected'), right=2 ),

            urwid.Padding(
            urwid.AttrMap(
            urwid.Button([('header_file', 'R'), 'eload'], on_press=self.reload_todos_from_file),
            'header', 'plain_selected'), right=2 ),

            urwid.Padding(
            urwid.AttrMap(
            urwid.Button([('header_file', 'S'), 'ave'], on_press=self.save_todos),
            'header', 'plain_selected'), right=2 ),

            urwid.Padding(
            urwid.AttrMap(
            urwid.Button([('header_file', 's'), 'ort: '+self.sorting_display[self.sorting[0]]], on_press=self.toggle_sorting),
            'header', 'plain_selected'), right=2 ),

            urwid.Padding(
            urwid.AttrMap(
            urwid.Button([('header_file', 'f'), 'ilter'], on_press=self.toggle_filter_panel),
            'header', 'plain_selected'), right=2 )
        ] ), 'header')

    def search_box_updated(self, edit_widget, new_contents):
        old_contents = edit_widget.edit_text
        self.search_string = new_contents
        self.search_todo_list(self.search_string)

    def search_todo_list(self, search_string=""):
        if search_string:
            self.delete_todo_widgets()

            self.searching = True

            for t in self.todos.search(search_string):
                self.listbox.body.append( TodoWidget(t, self.colorscheme, self, wrapping=self.wrapping[0], border=self.border[0]) )

    def start_search(self):
        self.searching = True
        self.update_footer()
        self.frame.set_focus('footer')

    def finalize_search(self):
        self.search_string = ''
        self.frame.set_focus('body')
        for widget in self.listbox.body:
            widget.update_todo()

    def clear_search_term(self, button=None):
        self.delete_todo_widgets()
        self.searching = False
        self.search_string = ''
        self.update_footer()
        self.reload_todos_from_memory()

    def create_footer(self):
        if self.searching:
            self.search_box = SearchWidget(self, edit_text=self.search_string)
            w = urwid.AttrMap(urwid.Columns([
                (1, urwid.Text('/')),
                self.search_box,
                (16, urwid.AttrMap(
                    urwid.Button([('header_file', 'C'), 'lear Search'], on_press=self.clear_search_term),
                    'header', 'plain_selected') )
            ]), 'footer')
            urwid.connect_signal(self.search_box, 'change', self.search_box_updated)
        else:
            w = None
        return w

    def create_help_panel(self):
        header_highlight = 'plain_selected'
        return urwid.AttrMap(
            urwid.LineBox(
            urwid.Padding(
            ViListBox(
                [ urwid.Divider() ] +

                [ urwid.AttrWrap(urwid.Text("""
General
""".strip()), header_highlight) ] +
                # [ urwid.Divider(u'─') ] +

                [ urwid.Text("""
h, ?         - show / hide this help message
q            - quit and save
t            - show / hide toolbar
w            - toggle word wrap
b            - toggle borders on todo items
S            - save current todo file
R            - reload the todo file (discarding changes)
""")] +

                [ urwid.AttrWrap(urwid.Text("""
Movement
""".strip()), header_highlight) ] +
                # [ urwid.Divider(u'─') ] +

                [ urwid.Text("""
mouse click  - select any todo, checkbox or button
j, down      - move selection down
k, up        - move selection up
g, page up   - move selection to the top item
G, page down - move selection to the bottom item
left, right  - move selection between todos and filter panel
H, L
tab          - toggle focus between todos, filter panel, and toolbar
""")] +

                [ urwid.AttrWrap(urwid.Text("""
Manipulating Todo Items
""".strip()), header_highlight) ] +
                # [ urwid.Divider(u'─') ] +

                [ urwid.Text("""
x            - complete / un-complete selected todo item
X            - archive completed todo items to done.txt (if specified)
n            - add a new todo to the end of the list
o            - add a todo after the selected todo (when not filtering)
O            - add a todo before the selected todo (when not filtering)
enter, A, e  - edit the selected todo
D            - delete the selected todo
J            - swap with item below
K            - swap with item above
""")] +

                [ urwid.AttrWrap(urwid.Text("""
While Editing a Todo
""".strip()), header_highlight) ] +
                # [ urwid.Divider(u'─') ] +

                [ urwid.Text("""
tab          - tab complete contexts and projects
return       - save todo item
left, right  - move cursor left and right
ctrl-b       - move cursor backwards (left) by one word
ctrl-f       - move cursor forwards (right) by one word
home, end    - move cursor the beginning or end of the line
ctrl-a, ctrl-e
ctrl-w       - delete one word backwards
ctrl-k       - delete from the cursor to the end of the line
ctrl-y       - paste last deleted text
""")] +

                [ urwid.AttrWrap(urwid.Text("""
Sorting
""".strip()), header_highlight) ] +
                # [ urwid.Divider(u'─') ] +

                [ urwid.Text("""
s            - toggle sort order (Unsorted, Ascending, Descending)
               sort order is saved on quit
""")] +
                [ urwid.AttrWrap(urwid.Text("""
Filtering
""".strip()), header_highlight) ] +
                # [ urwid.Divider(u'─') ] +

                [ urwid.Text("""
f            - open / close the filtering panel
F            - clear any active filters
""")] +
                [ urwid.AttrWrap(urwid.Text("""
Searching
""".strip()), header_highlight) ] +
                # [ urwid.Divider(u'─') ] +

                [ urwid.Text("""
/            - start search
enter        - finalize search
C            - clear search
""")]
            ),
            left=1, right=1, min_width=10 ), title='Key Bindings'), 'default')

    def create_filter_panel(self):
        w = urwid.AttrMap(
            urwid.Padding(
            urwid.ListBox(
                [
                    ViPile(
                        [ urwid.Text('Contexts & Projects', align='center') ] +
                        [ urwid.Divider(u'─') ] +
                        [urwid.AttrWrap(urwid.CheckBox(c, state=(c in self.active_contexts), on_state_change=self.checkbox_clicked, user_data=['context', c]), 'context_dialog_color', 'context_selected') for c in self.todos.all_contexts()] +
                        [ urwid.Divider(u'─') ] +
                        [urwid.AttrWrap(urwid.CheckBox(p, state=(p in self.active_projects), on_state_change=self.checkbox_clicked, user_data=['project', p]), 'project_dialog_color', 'project_selected') for p in self.todos.all_projects()] +
                        [ urwid.Divider(u'─') ] +
                        [ urwid.AttrMap(urwid.Button(['Clear ', ('header_file_dialog_color','F'), 'ilters'], on_press=self.clear_filters), 'dialog_color', 'plain_selected') ]
                    )
                ] +
                [ urwid.Divider() ],
            ),
            left=1, right=1, min_width=10 )
            ,
        'dialog_color')

        bg = urwid.AttrWrap(urwid.SolidFill(u" "), 'dialog_background') # u"\u2592"
        shadow = urwid.AttrWrap(urwid.SolidFill(u" "), 'dialog_shadow')

        bg = urwid.Overlay( shadow, bg,
            ('fixed left', 2), ('fixed right', 1),
            ('fixed top', 2), ('fixed bottom', 1))
        w = urwid.Overlay( w, bg,
            ('fixed left', 1), ('fixed right', 2),
            ('fixed top', 1), ('fixed bottom', 2))
        return w

    def delete_todo_widgets(self):
        for i in range(len(self.listbox.body)-1, -1, -1):
            self.listbox.body.pop(i)

    def reload_todos_from_memory(self):
        for t in self.todos.todo_items:
            self.listbox.body.append( TodoWidget(t, self.colorscheme, self, wrapping=self.wrapping[0], border=self.border[0]) )

    def clear_filters(self, button=None):
        self.delete_todo_widgets()
        self.reload_todos_from_memory()

        self.active_projects = []
        self.active_contexts = []
        self.filtering = False
        self.view.set_focus(0)
        self.update_filters()

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

        if self.active_projects or self.active_contexts:
            self.filter_todo_list()
            self.view.set_focus(0)
        else:
            self.clear_filters()

    def filter_todo_list(self):
        self.delete_todo_widgets()

        for t in self.todos.filter_contexts_and_projects(self.active_contexts, self.active_projects):
            self.listbox.body.append( TodoWidget(t, self.colorscheme, self, wrapping=self.wrapping[0], border=self.border[0]) )

        self.filtering = True

    def update_filters(self, new_contexts=[], new_projects=[]):
        if self.active_contexts:
            for c in new_contexts:
                self.active_contexts.append(c)
        if self.active_projects:
            for p in new_projects:
                self.active_projects.append(p)
        self.update_filter_panel()

    def update_filter_panel(self):
        self.filter_panel = self.create_filter_panel()
        if len(self.view.widget_list) > 1:
            self.view.widget_list.pop()
            self.view.widget_list.append(self.filter_panel)

    def update_header(self, message=""):
        if self.toolbar_is_open:
            self.frame.header = urwid.Pile([self.create_header(message), self.create_toolbar()])
        else:
            self.frame.header = self.create_header(message)

    def update_footer(self, message=""):
        self.frame.footer = self.create_footer()

    def main(self):
        self.header = self.create_header()
        self.footer = self.create_footer()

        self.listbox = ViListBox(urwid.SimpleListWalker(
            [TodoWidget(t, self.colorscheme, self) for t in self.todos.todo_items]
        ))

        self.frame  = urwid.Frame(urwid.AttrMap(self.listbox, 'plain'), header=self.header, footer=self.footer)

        self.view = ViColumns([
            ('weight', 2, self.frame )
         ])

        self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.keystroke)
        self.loop.screen.set_terminal_properties(colors=256)
        self.loop.run()

