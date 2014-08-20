import urwid

class ItemWidget(urwid.WidgetWrap):
    def __init__(self, text):
        self.__super.__init__(urwid.Text(text))
    def selectable(self):
        return True

class MenuButton(urwid.Button):
    def __init__(self, caption, callback, colorscheme):
        super(MenuButton, self).__init__("")
        urwid.connect_signal(self, 'click', callback)
        self._w = urwid.AttrMap( urwid.AttrMap(
            urwid.LineBox(ItemWidget(caption)),
            None, 'selected'),
            None, colorscheme.focus_map)

class UrwidUI:
    def __init__(self, todos, colorscheme):
        self.todo = todos
        self.colorscheme = colorscheme

    def main(self):
        palette = [ (key, '', '', '', value['fg'], value['bg']) for key, value in self.colorscheme.colors.items() ]
        # palette = [
        #     ('body','dark cyan', '', 'standout'),
        #     ('focus','dark red', '', 'standout'),
        #     ('head','light red', 'black'),
        # ]

        def keystroke (input):
            if input in ('q', 'Q'):
                raise urwid.ExitMainLoop()
            if input is 'enter':
                focus = listbox.get_focus()[0].content
                view.set_header(urwid.AttrWrap(urwid.Text(
                    'selected: %s' % str(focus)), 'header'))

        items = []
        for todo_item in self.todo.todo_items:
            items.append(
                # ItemWidget(todo_item.raw_index, todo_item.colored)
                # urwid.Button(todo_item.colored)
                MenuButton(todo_item.colored, None, self.colorscheme)
            )

        header  = urwid.AttrMap(
            urwid.Columns( [
                urwid.Text( ('header_todo_count', " {0} Todos ".format(len(self.todo.todo_items))) ),
                # urwid.Text( " todotxt-machine ", align='center' ),
                urwid.Text( ('header_file', " {0} ".format(self.todo.file_path)), align='right' )
            ]), 'header')

        listbox = urwid.ListBox(urwid.SimpleListWalker(items))
        view    = urwid.Frame(urwid.AttrMap(listbox, 'plain'), header=header)
        loop    = urwid.MainLoop(view, palette, unhandled_input=keystroke)
        loop.screen.set_terminal_properties(colors=256)
        loop.run()
