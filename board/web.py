import json

from zope import interface
from zope import component

from interfaces import INote
from interfaces import INoteWsgiApp

class NoteWsgiPublisher(object):
    interface.implements(INoteWsgiApp)
    component.adapts(INote)

    def __init__(self, note):
        self.note = note

    def __call__(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        data = {'properties': dict(self.note)}
        return [json.dumps(data)]
