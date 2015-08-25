

class KeyBindings:

    user_keys = []
    key_bindings = {}

    def __init__(self, user_keys):
        self.user_keys = user_keys
        self.fillWithDefault();


    def fillWithDefault(self):
        self.key_bindings['toggle-help'] = ['h', '?']
        self.key_bindings['quit'] = ['q']
        self.key_bindings['toggle-toolbar'] = ['t']
        self.key_bindings['toggle-borders'] = ['b']
        self.key_bindings['toggle-wrapping'] = ['w']
        self.key_bindings['save'] = ['S']
        self.key_bindings['reload'] = ['R']
        self.key_bindings['down'] = ['j', 'down']
        self.key_bindings['up'] = ['k', 'up']
        self.key_bindings['top'] = ['g']
        self.key_bindings['right'] = ['L', 'right']
        self.key_bindings['left'] = ['H', 'left']
        self.key_bindings['bottom'] = ['G']
        self.key_bindings['change-focus'] = ['tab']
        self.key_bindings['toggle-complete'] = ['x']
        self.key_bindings['archive'] = ['X']
        self.key_bindings['append'] = ['n']
        self.key_bindings['insert-after'] = ['o']
        self.key_bindings['insert-before'] = ['O']
        self.key_bindings['save-item'] = ['enter']
        self.key_bindings['edit'] = ['enter', 'A', 'e']
        self.key_bindings['delete'] = ['D']
        self.key_bindings['swap-down'] = ['J']
        self.key_bindings['swap-up'] = ['K']
        self.key_bindings['edit-complete'] = ['tab']
        self.key_bindings['edit-save'] = ['return']
        self.key_bindings['edit-move-left'] = ['left']
        self.key_bindings['edit-move-right'] = ['right']
        self.key_bindings['edit-word-left'] = ['meta b', 'ctrl b']
        self.key_bindings['edit-word-right'] = ['meta f', 'ctrl f']
        self.key_bindings['edit-end'] = ['ctrl e', 'end']
        self.key_bindings['edit-home'] = ['ctrl a', 'home']
        self.key_bindings['edit-delete-word'] = ['ctrl w']
        self.key_bindings['edit-delete-end'] = ['ctrl k']
        self.key_bindings['edit-paste'] = ['ctrl y']
        self.key_bindings['toggle-filter'] = ['f']
        self.key_bindings['clear-filter'] = ['F']
        self.key_bindings['toggle-sorting'] = ['s']
        self.key_bindings['search'] = ['/']
        self.key_bindings['search-end'] = ['enter']
        self.key_bindings['search-clear'] = ['C']


    def userKeysToList(self, userKey):
        return (userKey.replace(' ', '')).split(',')


    def getKeyBinding(self, bind):
        try:
            return self.key_bindings[bind]
        except KeyError:
            return []

    def is_binded_to(self, key, bind):
        return key in self.getKeyBinding(bind)
