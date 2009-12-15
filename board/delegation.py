class DefaultDelegate(object):
    def __init__(self, note):
        self.note = note

registry = {None: DefaultDelegate}

def register(name, factory):
    assert name not in registry
    registry[name] = factory

def lookup_delegate(note):
    try:
        factory = registry[note['-delegate-']]
    except KeyError:
        factory = registry[None]
    return factory(note)
