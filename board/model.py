import collections

class Note(collections.MutableMapping):
    """
    A note is the basic object in Board. It behaves like a ``dict``, with one
    notable exception: storing None is equivalent to removing an item, and
    getting a missing value returns None.
    """
    
    def __init__(self):
        self._properties = {}
        self._children = []

    def __setitem__(self, key, value):
        if value is None:
            del self[key]
        elif not isinstance(value, basestring):
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
        self._children.append(note)

    def insert_child_before(self, note, before):
        if before is None:
            self.append_child(note)
        else:
            i = self._children.index(before) + 1
            self._children.insert(i, note)

    def children(self):
        return iter(self._children)
