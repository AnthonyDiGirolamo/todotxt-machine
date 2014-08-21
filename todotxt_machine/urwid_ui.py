import urwid
import collections

class MenuButton(urwid.Button):
    def __init__(self, todo, colorscheme):
        super(MenuButton, self).__init__("")
        self.todo = todo
        self.wrapping = 'clip'
        self.border = 'no border'
        self.colorscheme = colorscheme
        self.editing = False
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
            if key is 'enter':
                self.editing = True
                self._w = urwid.Edit(caption="", edit_text=self.todo.raw)
                return key
            else:
                return key

class UrwidUI:
    def __init__(self, todos, colorscheme):
        self.wrapping = collections.deque(['clip', 'space'])
        self.border = collections.deque(['no border', 'bordered'])
        self.todos = todos
        self.colorscheme = colorscheme

    def main(self):
        palette = [ (key, '', '', '', value['fg'], value['bg']) for key, value in self.colorscheme.colors.items() ]

        items = []
        for todo_item in self.todos.todo_items:
            items.append(
                # ItemWidget(todo_item.raw_index, todo_item.colored)
                # urwid.Button(todo_item.colored)
                MenuButton(todo_item, self.colorscheme)
            )

        header  = urwid.AttrMap(
            urwid.Columns( [
                urwid.Text( ('header_todo_count', " {0} Todos ".format(len(self.todos.todo_items))) ),
                # urwid.Text( " todotxt-machine ", align='center' ),
                urwid.Text( ('header_file', " {0} ".format(self.todos.file_path)), align='right' )
            ]), 'header')

        listbox = urwid.ListBox(urwid.SimpleListWalker(items))
        view    = urwid.Frame(urwid.AttrMap(listbox, 'plain'), header=header)

        def keystroke (input):
            if input in ('q', 'Q'):
                raise urwid.ExitMainLoop()

            # Movement
            elif input is 'g':
                listbox.set_focus(0)
            elif input is 'G':
                listbox.set_focus(len(listbox.body)-1)
            elif input in ('k', 'K'):
                focus_index = listbox.get_focus()[1]
                if focus_index > 0:
                    listbox.set_focus(focus_index - 1)
            elif input in ('j', 'J'):
                focus_index = listbox.get_focus()[1]
                if focus_index+1 < len(listbox.body):
                    listbox.set_focus(focus_index + 1)

            # View options
            elif input is 'w':
                self.wrapping.rotate(1)
                for widget in listbox.body:
                    widget.wrapping = self.wrapping[0]
                    widget.update_todo()
            elif input is 'l':
                self.border.rotate(1)
                for widget in listbox.body:
                    widget.border = self.border[0]
                    widget.update_todo()

            # Editing
            elif input is 'x':
                focus = listbox.get_focus()[0]
                i = focus.todo_id

                # if self.sorting > 0:
                #     i = self.selected_item

                if self.todos[i].is_complete():
                    self.todos[i].incomplete()
                else:
                    self.todos[i].complete()
                focus.update_todo(self.todos[i].colored)

            # elif input is 'enter':
            #     # import ipdb; ipdb.set_trace()
            #     focus_index = listbox.get_focus()[1]
            #     edit_todo = urwid.Edit(caption="", edit_text=listbox.body[focus_index].todo_raw)
            #     listbox.body[focus_index] = edit_todo
            #     # view.set_header(urwid.AttrWrap(urwid.Text('selected: %s' % str(focus)), 'header'))

        loop = urwid.MainLoop(view, palette, unhandled_input=keystroke)
        loop.screen.set_terminal_properties(colors=256)
        loop.run()
