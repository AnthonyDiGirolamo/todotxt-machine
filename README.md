todotxt-machine
===============

todotxt-machine is an interactive terminal based [todo.txt](http://todotxt.com/) file editor with an interface similar to [mutt](http://www.mutt.org/). It follows [the todo.txt
format](https://github.com/ginatrapani/todo.txt-cli/wiki/The-Todo.txt-Format) and stores todo items in plain text.

Screenshots
-----------

View your todos in a list with helpful syntax highlighting:

[![screenshot1.png](https://raw.github.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/screenshot1.png)](https://raw.github.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/screenshot1.png)

Sort in ascending or descending order, or keep things unsorted:

[![screenshot3.png](https://raw.github.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/screenshot3.png)](https://raw.github.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/screenshot3.png)

Filter contexts and projects:

[![screenshot2.png](https://raw.github.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/screenshot2.png)](https://raw.github.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/screenshot2.png)

Search for the todos you want to edit:

[![screenshot4.png](https://raw.github.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/screenshot4.png)](https://raw.github.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/screenshot4.png)

Search with fuzzy matching:

[![screenshot5.png](https://raw.github.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/screenshot5.png)](https://raw.github.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/screenshot5.png)

Tab completion of contexts and projects:

[![screenshot5.png](https://raw.github.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/screenshot6.png)](https://raw.github.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/screenshot6.png)

And some quotes for when you have nothing left to do:

[![screenshot_quote1.png](https://raw.github.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/screenshot_quote1.png)](https://raw.github.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/screenshot_quote1.png)

[![screenshot_quote2.png](https://raw.github.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/screenshot_quote2.png)](https://raw.github.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/screenshot_quote2.png)

Requirements
------------

Python 2.7 or Python 3.3 with readline support on Linux or Mac OS X.
todotxt-machine outputs raw [terminal control
sequences](http://invisible-island.net/xterm/ctlseqs/ctlseqs.html) to draw its
interface and does not rely on modules like
[curses](http://docs.python.org/3.3/library/curses.html) or
[urwid](http://excess.org/urwid/).

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
      todotxt-machine [--file FILE] [--config FILE] [--readline-editing-mode=(vi|emacs)]
      todotxt-machine (-h | --help)
      todotxt-machine --version

    Options:
      -f FILE --file=FILE                 Path to your todo.txt file
      -c FILE --config=FILE               Path to your todotxt-machine configuraton file [default: ~/.todotxt-machinerc]
      --readline-editing-mode=(vi|emacs)  Set readline editing mode [default: vi]
      -h --help                           Show this screen.
      --version                           Show version.

Config File
-----------

You can tell todotxt-machine to use the same todo.txt file whenever it starts
up by adding a `file` entry to the ~/.todotxt-machinerc file.  You can also set
you preferred colorscheme or even define new themes.

Here is an example config file with a complete colorscheme definition:

    [settings]
    file = ~/todo.txt
    colorscheme = myawesometheme

    [colorscheme-myawesometheme]
    plain=h250
    selected=,h238
    header=h39,h235
    header_todo_count=h222,h62
    header_todo_pending_count=h232,h228
    header_todo_done_count=h22,h156
    header_sorting=h235,h39
    header_file=h48,h235
    dialog_button=h255,h242
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

Let me know if you make any good colorschemes and I'll add it to todotxt-machine.

Key Bindings
------------

### General

    h, ?         - display this help message
    q            - quit and save
    S            - save current todo file
    R            - reload the todo file (discarding changes)

### Movement

    mouse click  - select any todo, checkbox or button
    j, down      - move selection down
    k, up        - move selection up
    g, page up   - move selection to the top item
    G, page down - move selection to the bottom item
    left, right  - move selection between todos and filter panel

### Manipulating Todo Items

    x            - complete / un-complete selected todo item
    n            - add a new todo to the end of the list
    o            - add a todo after the selected todo (when not filtering)
    O            - add a todo before the selected todo (when not filtering)
    enter, A, e  - edit the selected todo
    D            - delete the selected todo
    J            - swap with item below
    K            - swap with item above

### While Editing a Todo

    tab          - tab complete contexts and projects
    return       - save todo item
    left, right  - move cursor left and right
    ctrl-b       - move cursor backwards (left) by one word
    ctrl-f       - move cursor forwards (right) by one word
    home, end    - move cursor the beginning or end of the line
    ctrl-a, ctrl-e
    ctrl-w       - delete one word backwards
    ctrl-k       - delete from the cursor to the end of the line

### Filtering

    f            - open the filtering panel
    F            - clear any active filters

### Sorting

    s            - switch sorting method

### Searching

    /            - start search
    enter        - finalize search
    L            - clear search


Planned Features
----------------

- ~~User defined color themes~~
- ~~Manual reordering of todo items~~
- ~~Config file for setting colors and todo.txt file location~~
- Support for archiving todos in done.txt

Updates
-------

See the [log here](https://github.com/AnthonyDiGirolamo/todotxt-machine/commits/master)
