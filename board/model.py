import collections

from board import delegation

class Note(collections.MutableMapping):
    """
    A note is the basic object in Board. It behaves like a ``dict``, with one
    notable exception: storing None is equivalent to removing an item, and
    getting a missing value returns None.
    """

    _document = None
    _id = None

    def __init__(self, properties=None, children=None, parent=None):
        if properties is None:
            properties = self._properties_factory()
        if children is None:
            children = self._children_factory()
        self._properties = properties
        self._children = children
        self._parent = parent
        for note in children:
            self._link_child(note)

    _properties_factory = dict
    _children_factory = list

    @property
    def parent(self):
        return self._parent

    def _link_child(self, note):
        if note._parent is not None:
            note._parent.remove_child(note)
        note._parent = self
        if self._document is not None:
            self._document._note_added(note)

    def __setitem__(self, key, value):
        if value is None:
            del self[key]
        elif (not isinstance(key, basestring) or
              not isinstance(value, basestring)):
            raise ValueError
        else:
            self._properties[key] = value

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key, default=None):
        try:
            return self._properties[key]
        except KeyError:
            return default

    def __delitem__(self, key):
        del self._properties[key]

    def __iter__(self):
        return iter(self._properties)

    def __len__(self):
        return len(self._properties)

    def append_child(self, note):
        self.insert_child_before(note, None)

    def insert_child_before(self, note, before):
        if before is None:
            self._children.append(note)
        else:
            i = self._children.index(before) + 1
            self._children.insert(i, note)
        self._link_child(note)

    def remove_child(self, note):
        self._children.remove(note)
        note._parent = None

    def children(self):
        return iter(self._children)

    def lookup(self, path):
        if path == '':
            return self
        elif path.startswith('/'):
            seek = self
            while seek.parent is not None:
                seek = seek.parent
            return seek.lookup(path[1:])

        if '/' not in path:
            path = path + '/'
        next_name, path_remainder = path.split('/', 1)

        for child in self.children():
            if child.get('-name-', None) == next_name:
                return child.lookup(path_remainder)
        else:
            return None

    def get_delegate(self):
        return delegation.lookup_delegate(self)

class Document(object):
    def __init__(self):
        root = Note()
        root._id = 0
        root._document = self
        self.root = root
        self._index = {0: root}
        self._next_id = 1

    def __len__(self):
        return len(self._index)

    def _note_added(self, note):
        assert note._document is None
        assert list(note.children()) == []
        note._document = self
        note._id = self._next_id
        self._next_id += 1
        self._index[note._id] = note
