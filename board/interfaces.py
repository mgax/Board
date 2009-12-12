from zope import interface

class INote(interface.Interface):
    """ One note """

    parent = interface.Attribute('The parent note (None if this note is root)')

    def __setitem__(key, value):
        """ Set a property (if `value` is None, it removes the property). """

    def __getitem__(key):
        """ Retrieve a property """

    def get(key, default=None):
        """ Retrieve a property, or `default` if missing """

    def __delitem__(key):
        """ Remove a property. Equivalent to note.__setitem__(key, None) """

    def __iter__():
        """ Iterate through the names of all properties of this note """

    def __len__():
        """ Returns the number of properties of this note """

    def append_child(note):
        """ Add a child note to the end of the child list """

    def insert_child_before(note, before):
        """ Add a child to the child list, before the specified child """

    def children():
        """ Iterate through all the children of this note, in order """

    def lookup(path):
        """ Traverse this note and its neighbors, according to `path` """

class INoteWsgiApp(interface.Interface):
    """ A WSGI-compliant application that publishes a note """

    def __call__(environ, start_response):
        """ The WSGI API """
