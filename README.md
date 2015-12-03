todotxt-machine
===============

todotxt-machine is an interactive terminal based [todo.txt](http://todotxt.com/) file editor with an interface similar to [mutt](http://www.mutt.org/). It follows [the todo.txt
format](https://github.com/ginatrapani/todo.txt-cli/wiki/The-Todo.txt-Format) and stores todo items in plain text.

In Action
---------

[![animation1.gif](https://raw.githubusercontent.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/animation1.gif)](https://raw.githubusercontent.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/animation1.gif)

Features
--------

- View your todos in a list with helpful syntax highlighting
- Archive completed todos
- Define your own colorschemes
- Tab completion of contexts and projects
- Filter contexts and projects
- Search for the todos you want with fuzzy matching
- Sort in ascending or descending order, or keep things unsorted
- Clickable UI elements

Requirements
------------

Python 2.7 or Python 3.4 on Linux or Mac OS X.

todotxt-machine 1.1.8 and earlier drew its user interface using only raw
terminal escape sequences. While this was very educational it was difficult to
extend with new features. Version 2 and up uses
[urwid](http://excess.org/urwid/) to draw its interface and is much more easily
extendable.

Installation
------------

### Using [pip](https://pypi.python.org/pypi/pip)

    pip install todotxt-machine

### Manually

Download or clone this repo and run the `todotxt-machine.py` script.

    git clone https://github.com/AnthonyDiGirolamo/todotxt-machine.git
    cd todotxt-machine
    ./todotxt-machine.py

Command Line Options
--------------------

    todotxt-machine

    Usage:
      todotxt-machine
      todotxt-machine TODOFILE [DONEFILE]
      todotxt-machine [--config FILE]
      todotxt-machine (-h | --help)
      todotxt-machine --version
      todotxt-machine --show-default-bindings

    Options:
      -c FILE --config=FILE               Path to your todotxt-machine configuraton file [default: ~/.todotxt-machinerc]
      -h --help                           Show this screen.
      --version                           Show version.
      --show-default-bindings             Show default keybindings in config parser format
                                          Add this to your config file and edit to customize



Config File
-----------

You can tell todotxt-machine to use the same todo.txt file whenever it
starts up by adding a ``file`` entry to the `~/.todotxt-machinerc` file.
If you want to archive completed tasks, you can specify a done.txt file
using an ``archive`` entry. You can also set you preferred colorscheme or even
define new themes.  Here is a short example:

    [settings]
    file = ~/todo.txt
    archive = ~/done.txt
    auto-save = True
    show-toolbar = False
    show-filter-panel = False
    enable-borders = False
    enable-word-wrap = True
    colorscheme = myawesometheme

Color Schemes
-------------

todotxt-machine currently supports [solarized](http://ethanschoonover.com/solarized) and [base16](https://github.com/chriskempson/base16) colors.

[![todo_colors.png](https://raw.githubusercontent.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/todo_colors.png)](https://raw.githubusercontent.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/todo_colors.png)

Pictured above are the following themes from left to right:

- `base16-light`
- `base16-dark`
- `solarized-light`
- `solarized-dark`

Here is a config file with a complete colorscheme definition:

    [settings]
    file = ~/todo.txt
    colorscheme = myawesometheme

    [colorscheme-myawesometheme]
    plain=h250
    selected=,h238
    header=h250,h235
    header_todo_count=h39,h235
    header_todo_pending_count=h228,h235
    header_todo_done_count=h156,h235
    header_file=h48,h235
    dialog_background=,h248
    dialog_color=,h240
    dialog_shadow=,h238
    footer=h39,h235
    search_match=h222,h235
    completed=h59
    context=h39
    project=h214
    creation_date=h135
    due_date=h161
    priority_a=h167
    priority_b=h173
    priority_c=h185
    priority_d=h77
    priority_e=h80
    priority_f=h62

You can add colorschemes by adding sections with names that start with
`colorscheme-`. Then under the `[settings]` section you can say which
colorscheme you want to use.

The format for a color definitions is:

    name=foreground,background

Foreground and background colors are follow the 256 color formats [defined by urwid](http://urwid.org/manual/displayattributes.html#color-foreground-and-background-colors). Here is an excerpt from that link:

> High colors may be specified by their index `h0`, ..., `h255` or with the shortcuts for the color cube `#000`, `#006`, `#008`, ..., `#fff` or gray scale entries `g0` (black from color cube) , `g3`, `g7`, ... `g100` (white from color cube).

You can see all the colors defined [here](http://urwid.org/examples/index.html#palette-test-py).

I recommend you leave the foreground out of the following definitions by adding
a comma immediately after the `=`

    selected=,h238
    dialog_background=,h248
    dialog_color=,h240
    dialog_shadow=,h238

If you want to use your terminal's default foreground and background color use
blank strings and keep the comma:

    dialog_background=,

Let me know if you make any good colorschemes and I'll add it to the default collection.

Key Bindings
------------

You can customize any key binding by adding a setting to the `[keys]` section of
your config file `~/.todotxt-machinerc`.

For a list of the default key bindings run:

    todotxt-machine --show-default-bindings

You can easily append this to your config file by running:

    todotxt-machine --show-default-bindings >> ~/.todotxt-machinerc

When you edit a key binding the in app help will reflect it. Hit `h` or `?` to view the help.

Known Issues
------------

### OSX

- On Mac OS hitting `ctrl-y` suspends the application. Run `stty dsusp undef` to fix.
- Mouse interaction doesn't seem to work properly in the Apple Terminal. I would
  recommend using [iTerm2](http://iterm2.com/) or rxvt / xterm in
  [XQuartz](http://xquartz.macosforge.org/landing/).

### Tmux

- With tmux the background color in todotxt-machine can sometimes be lost at the end of a line. If this is
  happening to you set your `$TERM` variable to `screen` or `screen-256color`

    export TERM=screen-256color

Planned Features
----------------

- ~~User defined color themes~~
- ~~Manual reordering of todo items~~
- ~~Config file for setting colors and todo.txt file location~~
- ~~Support for archiving todos in done.txt~~
- ~~Custom keybindings~~
- Add vi readline keybindings. urwid doesn't support readline currently. The
  emacs style bindings currently available are emulated.

Updates
-------



See the [log here](https://github.com/AnthonyDiGirolamo/todotxt-machine/commits/master)
