import collections

class Note(collections.MutableMapping):
    """
    A note is the basic object in Board. It behaves like a ``dict``, with one
    notable exception: storing None is equivalent to removing an item, and
    getting a missing value returns None.
    """
    
    def __init__(self):
        self._data = {}

    def __setitem__(self, key, value):
        if value is None:
            del self[key]
        elif not isinstance(value, basestring):
            raise ValueError
        else:
            self._data[key] = value

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key, default=None):
        try:
            return self._data[key]
        except KeyError:
            return default

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)
