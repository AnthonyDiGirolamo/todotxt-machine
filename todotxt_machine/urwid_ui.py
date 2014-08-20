import urwid

class ItemWidget(urwid.WidgetWrap):
    def __init__(self, id, text):
        self.id = id
        self.content = "raw_index[{0}] {1}".format(str(id), text)
        # self.item = [
        w = urwid.AttrWrap(text, 'default', 'selected')
        # w = urwid.AttrWrap( urwid.Text(text), 'default', focus_attr='selected')
        # ]
        # w = urwid.Columns(self.item)
        self.__super.__init__(w)

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key

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
        import ipdb; ipdb.set_trace()
        for todo_item in self.todo.todo_items:
            items.append(ItemWidget(todo_item.raw_index, todo_item.colored))

        header  = urwid.AttrMap(urwid.Text('selected:'), 'header')
        listbox = urwid.ListBox(urwid.SimpleListWalker(items))
        view    = urwid.Frame(urwid.AttrWrap(listbox, 'default'), header=header)
        loop    = urwid.MainLoop(view, palette, unhandled_input=keystroke)
        loop.screen.set_terminal_properties(colors=256)
        loop.run()
