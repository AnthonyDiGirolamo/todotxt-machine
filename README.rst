todotxt-machine
===============

todotxt-machine is an interactive terminal based
`todo.txt <http://todotxt.com/>`__ file editor with an interface similar
to `mutt <http://www.mutt.org/>`__. It follows `the todo.txt
format <https://github.com/ginatrapani/todo.txt-cli/wiki/The-Todo.txt-Format>`__
and stores todo items in plain text.

In Action
---------

.. image:: https://raw.githubusercontent.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/animation1.gif
   :target: https://raw.githubusercontent.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/animation1.gif

Features
--------

-  View your todos in a list with helpful syntax highlighting
-  Archive completed todos
-  Define your own colorschemes
-  Tab completion of contexts and projects
-  Filter contexts and projects
-  Search for the todos you want with fuzzy matching
-  Sort in ascending or descending order, or keep things unsorted
-  Clickable UI elements

Requirements
------------

Python 2.7 or Python 3.4 on Linux or Mac OS X.

todotxt-machine 1.1.8 and earlier drew its user interface using only raw
terminal escape sequences. While this was very educational it was
difficult to extend with new features. Version 2 and up used
`urwid <http://excess.org/urwid/>`__ to draw its interface and is much
more easily extendable.

Installation
------------

Using `pip <https://pypi.python.org/pypi/pip>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install todotxt-machine

Manually
~~~~~~~~

Download or clone this repo and run the ``todotxt-machine.py`` script.

::

    git clone https://github.com/AnthonyDiGirolamo/todotxt-machine.git
    cd todotxt-machine
    ./todotxt-machine.py

Command Line Options
--------------------

::

    todotxt-machine

    Usage:
      todotxt-machine
      todotxt-machine TODOFILE [DONEFILE]
      todotxt-machine [--config FILE]
      todotxt-machine (-h | --help)
      todotxt-machine --version

    Options:
      -c FILE --config=FILE  Path to your todotxt-machine configuraton file [default: ~/.todotxt-machinerc]
      -h --help              Show this screen.
      --version              Show version.

Config File
-----------

You can tell todotxt-machine to use the same todo.txt file whenever it
starts up by adding a ``file`` entry to the ~/.todotxt-machinerc file.
If you want to archive completed tasks, you can specify a done.txt file
using an ``archive`` entry. You can also set you preferred colorscheme or even
define new themes.  Here is a short example:

::

    [settings]
    file = ~/todo.txt
    archive = ~/done.txt
    colorscheme = myawesometheme

Color Schemes
-------------

todotxt-machine currently supports
`solarized <http://ethanschoonover.com/solarized>`__ and
`base16 <https://github.com/chriskempson/base16>`__ colors.

.. image:: https://raw.githubusercontent.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/todo_colors.png
   :target: https://raw.githubusercontent.com/AnthonyDiGirolamo/todotxt-machine/master/screenshots/todo_colors.png

Pictured above are the following themes from left to right:

-  ``base16-light``
-  ``base16-dark``
-  ``solarized-light``
-  ``solarized-dark``

Here is a config file with a complete colorscheme definition:

::

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
``colorscheme-``. Then under the ``[settings]`` section you can say
which colorscheme you want to use.

The format for a color definitions is:

::

    name=foreground,background

Foreground and background colors are follow the 256 color formats
`defined by
urwid <http://urwid.org/manual/displayattributes.html#color-foreground-and-background-colors>`__.
Here is an excerpt from that link:

    High colors may be specified by their index ``h0``, ..., ``h255`` or
    with the shortcuts for the color cube ``#000``, ``#006``, ``#008``,
    ..., ``#fff`` or gray scale entries ``g0`` (black from color cube) ,
    ``g3``, ``g7``, ... ``g100`` (white from color cube).

You can see all the colors defined
`here <http://urwid.org/examples/index.html#palette-test-py>`__.

I recommend you leave the foreground out of the following definitions by
adding a comma immediately after the ``=``

::

    selected=,h238
    dialog_background=,h248
    dialog_color=,h240
    dialog_shadow=,h238

If you want to use your terminal's default foreground and background
color use blank strings and keep the comma:

::

    dialog_background=,

Let me know if you make any good colorschemes and I'll add it to the
default collection.

Key Bindings
------------

General
~~~~~~~

::

    h, ?         - show / hide this help message
    q            - quit and save
    t            - show / hide toolbar
    w            - toggle word wrap
    b            - toggle borders on todo items
    S            - save current todo file
    R            - reload the todo file (discarding changes)

Movement
~~~~~~~~

::

    mouse click  - select any todo, checkbox or button
    j, down      - move selection down
    k, up        - move selection up
    g, page up   - move selection to the top item
    G, page down - move selection to the bottom item
    left, right  - move selection between todos and filter panel
    H, L
    tab          - toggle focus between todos, filter panel, and toolbar

Manipulating Todo Items
~~~~~~~~~~~~~~~~~~~~~~~

::

    x            - complete / un-complete selected todo item
    X            - archive completed todo items to done.txt (if specified)
    n            - add a new todo to the end of the list
    o            - add a todo after the selected todo (when not filtering)
    O            - add a todo before the selected todo (when not filtering)
    enter, A, e  - edit the selected todo
    D            - delete the selected todo
    J            - swap with item below
    K            - swap with item above

While Editing a Todo
~~~~~~~~~~~~~~~~~~~~

::

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

Filtering
~~~~~~~~~

::

    f            - open the filtering panel
    F            - clear any active filters

Sorting
~~~~~~~

::

    s            - toggle sort order (Unsorted, Ascending, Descending)
                   sort order is saved on quit

Searching
~~~~~~~~~

::

    /            - start search
    enter        - finalize search
    C            - clear search

Known Issues
------------

OSX
~~~

-  On Mac OS hitting ``ctrl-y`` suspends the application. Run
   ``stty dsusp undef`` to fix.
-  Mouse interaction doesn't seem to work properly in the Apple
   Terminal. I would recommend using `iTerm2 <http://iterm2.com/>`__ or
   rxvt / xterm in `XQuartz <http://xquartz.macosforge.org/landing/>`__.

Tmux
~~~~

-  With tmux the background color in todotxt-machine can sometimes be
   lost at the end of a line. If this is happening to you set your
   ``$TERM`` variable to ``screen`` or ``screen-256color``

   export TERM=screen-256color

Planned Features
----------------

-  [STRIKEOUT:User defined color themes]
-  [STRIKEOUT:Manual reordering of todo items]
-  [STRIKEOUT:Config file for setting colors and todo.txt file location]
-  [STRIKEOUT:Support for archiving todos in done.txt]
-  Custom keybindings
-  Add vi readline keybindings. urwid doesn't support readline
   currently. The emacs style bindings currently available are emulated.

Updates
-------

See the `log
here <https://github.com/AnthonyDiGirolamo/todotxt-machine/commits/master>`__

