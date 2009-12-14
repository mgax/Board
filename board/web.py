import json
import wsgiref.util

from zope import interface
from zope import component
import webob
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
        req = webob.Request(environ)

        if req.method == 'GET':
            json_data = json.dumps({'properties': dict(self.note)})
            res = webob.Response(json_data, content_type='application/json')

        elif req.method == 'POST':
            action = req.POST['action']
            if action == 'set_props':
                for key, value in json.loads(req.POST['data']).iteritems():
                    self.note[key] = value
            else:
                raise NotImplementedError
            res = webob.Response()

        else:
            raise NotImplementedError

        return res(environ, start_response)
