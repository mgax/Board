import json
import wsgiref.util

import webob
import webob.exc

class DefaultDelegate(object):
    def __init__(self, note):
        self.note = note

    def wsgi(self, environ, start_response):
        next_name = wsgiref.util.shift_path_info(environ)
        if next_name is None:
            res = self.wsgi_response(webob.Request(environ))
        else:
            child = self.note.lookup(next_name)
            if child is None:
                res = webob.exc.HTTPNotFound()
            else:
                res = child.get_delegate().wsgi

        return res(environ, start_response)

    def wsgi_response(self, req):
        if req.method == 'GET':
            json_data = json.dumps({'properties': dict(self.note)})
            return webob.Response(json_data, content_type='application/json')

        elif req.method == 'POST':
            action = req.POST['action']
            if action == 'set_props':
                for key, value in json.loads(req.POST['data']).iteritems():
                    self.note[key] = value
            else:
                raise NotImplementedError
            return webob.Response()

        else:
            raise NotImplementedError

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
