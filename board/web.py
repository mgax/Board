import json
import wsgiref.util

from zope import interface
from zope import component
import webob.exc

from interfaces import INote
from interfaces import INoteWsgiApp

class NoteWsgiPublisher(object):
    interface.implements(INoteWsgiApp)
    component.adapts(INote)

    def __init__(self, note):
        self.note = note

    def __call__(self, environ, start_response):
        next_name = wsgiref.util.shift_path_info(environ)
        if next_name is None:
            res = self.handle
        else:
            child = self.note.lookup(next_name)
            if child is None:
                res = webob.exc.HTTPNotFound()
            else:
                res = INoteWsgiApp(child)

        return res(environ, start_response)

    def handle(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'application/json')])
        data = {'properties': dict(self.note)}
        return [json.dumps(data)]
