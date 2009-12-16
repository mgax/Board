import json
import wsgiref.util

import webob
import webob.exc

class DefaultDelegate(object):
    def __init__(self, note):
        self.note = note

    def wsgi(self, environ, start_response):
        next_name = wsgiref.util.shift_path_info(environ)
        res = None

        if next_name in (None, ''):
            res = self.wsgi_response(webob.Request(environ))

        elif next_name.startswith('c:') and len(next_name) > 2:
            child = self.note.lookup(next_name[2:])
            if child is not None:
                res = child.get_delegate().wsgi

        if res is None:
            res = webob.exc.HTTPNotFound()

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
