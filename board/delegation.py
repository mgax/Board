import json

import webob
import webob.exc

def JSONResponse(data, **kwargs):
    return webob.Response(json.dumps(data), content_type='application/json')

class DefaultDelegate(object):
    def __init__(self, note):
        self.note = note

    def wsgi(self, environ, start_response):
        req = webob.Request(environ)
        next_name = req.path_info_peek()
        res = webob.exc.HTTPNotFound()

        if next_name in (None, ''):
            res = self.wsgi_response(req)

        elif next_name == 'children':
            res = self.wsgi_response_children(req)

        elif next_name.startswith('c:') and len(next_name) > 2:
            req.path_info_pop()
            child = self.note.lookup(next_name[2:])
            if child is not None:
                res = child.get_delegate().wsgi

        return res(environ, start_response)

    def wsgi_response(self, req):
        if req.method == 'GET':
            return JSONResponse({'properties': dict(self.note)})

        elif req.method == 'POST':
            action = req.POST['action']
            if action == 'set_props':
                for key, value in json.loads(req.POST['data']).iteritems():
                    self.note[key] = value
                return webob.Response()

        raise NotImplementedError

    def wsgi_response_children(self, req):
        if req.method == 'GET':
            def url(child):
                return req.application_url + '/c:' + child['-name-']

            child_urls = [url(child) for child in self.note.children()]
            return JSONResponse({'children': child_urls})

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
