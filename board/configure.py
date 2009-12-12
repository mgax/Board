import functools
from zope import component

from board import web

def run_once(func):
    run = []
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not run:
            run.append(True)
            return func(*args, **kwargs)
    return wrapper

@run_once
def setup_components():
    component.provideAdapter(web.NoteWsgiPublisher)
