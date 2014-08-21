import urwid
import collections

class MenuButton(urwid.Button):
    def __init__(self, todo, colorscheme):
        super(MenuButton, self).__init__("")
        self.todo        = todo
        self.wrapping    = 'clip'
        self.border      = 'no border'
        self.colorscheme = colorscheme
        self.editing     = False
        # urwid.connect_signal(self, 'click', callback)
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

    def keypress(self, size, key):
        # import ipdb; ipdb.set_trace()
        if self.editing:
            if key in ['down', 'up']:
                return None # don't pass up or down to the ListBox
            elif key is 'enter':
                self.todo.update(self._w.edit_text.strip())
                self.update_todo()
                self.editing = False
                return key
            else:
                return self._w.keypress(size, key)
        else:
            if key in ['enter', 'e', 'A']:
                self.editing = True
                self._w = urwid.Edit(caption="", edit_text=self.todo.raw)
                return key
            else:
                return key

class UrwidUI:
    def __init__(self, todos, colorscheme):
        self.wrapping    = collections.deque(['clip', 'space'])
        self.border      = collections.deque(['no border', 'bordered'])

        self.todos       = todos
        self.items       = []

        self.colorscheme = colorscheme
        self.palette     = [ (key, '', '', '', value['fg'], value['bg']) for key, value in self.colorscheme.colors.items() ]

    def keystroke(self, input):
        focus_index = self.listbox.get_focus()[1]

        if input in ('q', 'Q'):
            raise urwid.ExitMainLoop()

        # Movement
        elif input is 'g':
            self.listbox.set_focus(0)
        elif input is 'G':
            self.listbox.set_focus(len(self.listbox.body)-1)
        elif input is 'k':
            if focus_index > 0:
                self.listbox.set_focus(focus_index - 1)
        elif input is 'j':
            if focus_index+1 < len(self.listbox.body):
                self.listbox.set_focus(focus_index + 1)
        elif input is 'J':
            if focus_index+1 < len(self.listbox.body):
                self.todos.swap(focus_index, focus_index + 1)
                self.listbox.body[focus_index].todo = self.todos[focus_index]
                self.listbox.body[focus_index+1].todo = self.todos[focus_index+1]
                self.listbox.body[focus_index].update_todo()
                self.listbox.body[focus_index+1].update_todo()
                self.listbox.set_focus(focus_index + 1)
        elif input is 'K':
            if focus_index > 0:
                self.todos.swap(focus_index, focus_index - 1)
                self.listbox.body[focus_index].todo = self.todos[focus_index]
                self.listbox.body[focus_index-1].todo = self.todos[focus_index-1]
                self.listbox.body[focus_index].update_todo()
                self.listbox.body[focus_index-1].update_todo()
                self.listbox.set_focus(focus_index - 1)

        # View options
        elif input is 'c':
            self.view.widget_list.append(urwid.SolidFill('#'))
        elif input is 'w':
            self.wrapping.rotate(1)
            for widget in self.listbox.body:
                widget.wrapping = self.wrapping[0]
                widget.update_todo()
        elif input is 'l':
            self.border.rotate(1)
            for widget in self.listbox.body:
                widget.border = self.border[0]
                widget.update_todo()

        # Editing
        elif input is 'x':
            focus = self.listbox.get_focus()[0]
            i = focus.todo.raw_index

            # if self.sorting > 0:
            #     i = self.selected_item

            if self.todos[i].is_complete():
                self.todos[i].incomplete()
            else:
                self.todos[i].complete()
            focus.update_todo()

        # elif input is 'enter':
        #     # import ipdb; ipdb.set_trace()
        #     focus_index = self.listbox.get_focus()[1]
        #     edit_todo = urwid.Edit(caption="", edit_text=self.listbox.body[focus_index].todo_raw)
        #     self.listbox.body[focus_index] = edit_todo
        #     # self.view.set_header(urwid.AttrWrap(urwid.Text('selected: %s' % str(focus)), 'header'))

    def main(self):
        for t in self.todos.todo_items:
            self.items.append(MenuButton(t, self.colorscheme))

        self.header = urwid.AttrMap(
            urwid.Columns( [
                urwid.Text( ('header_todo_count', " {0} Todos ".format(len(self.todos.todo_items))) ),
                # urwid.Text( " todotxt-machine ", align='center' ),
                urwid.Text( ('header_file', " {0} ".format(self.todos.file_path)), align='right' )
            ]), 'header')
        self.footer = urwid.AttrMap(
            urwid.Columns( [
            ]), 'footer')

        self.listbox = urwid.ListBox(urwid.SimpleListWalker(self.items))
        self.view    = urwid.Columns([urwid.Frame(urwid.AttrMap(self.listbox, 'plain'), header=self.header, footer=self.footer)])

        loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.keystroke)
        loop.screen.set_terminal_properties(colors=256)
        loop.run()
