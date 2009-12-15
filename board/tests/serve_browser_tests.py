import wsgiref.util
import mimetypes
from os import path
from copy import copy

import webob
import webob.exc

from board import yaml_storage

def get_mimetype(file_path):
    file_type = mimetypes.guess_type(file_path)[0]
    return file_type or 'application/octet-stream'

def make_static_file_app(file_path):
    def app(environ, start_response):
        next_path = wsgiref.util.shift_path_info(environ)

        if next_path is not None:
            if next_path == '..':
                res = webob.exc.HTTPUnauthorized('".." not allowed')
            else:
                res = make_static_file_app(path.join(file_path, next_path))

        elif path.isfile(file_path):
            with open(file_path) as f:
                data = f.read()
            res = webob.Response(data, content_type=get_mimetype(file_path))

        elif (path.isdir(file_path) and
              path.isfile(path.join(file_path, 'index.html'))):
            res = make_static_file_app(path.join(file_path, 'index.html'))

        else:
            res = webob.exc.HTTPNotFound('File %r not found' % file_path)

        return res(environ, start_response)

    return app

def serve_path(rel_path):
    return make_static_file_app(path.join(path.dirname(__file__), rel_path))

webdata_app = serve_path('browser_test_media')
media_app = serve_path('../web_media')

def load_fixture_app(environ, start_response):
    global root_note
    request = webob.Request(environ)
    root_note = yaml_storage.load(request.POST['fixture'])
    return webob.Response('loaded')(environ, start_response)

def browser_testing_app(environ, start_response):
    environ_orig = copy(environ)
    next_path = wsgiref.util.shift_path_info(environ)

    if next_path == 'root':
        res = root_note.get_delegate().wsgi

    elif next_path == 'load_fixture':
        res = load_fixture_app

    elif next_path == 'board_media':
        res = media_app

    else:
        environ = environ_orig
        res = webdata_app

    return res(environ, start_response)

def main(host='127.0.0.1', port=8000, app=browser_testing_app, quiet=True):
    from wsgiref.simple_server import make_server, WSGIRequestHandler
    class QuietHandler(WSGIRequestHandler):
        pass
    if quiet:
        QuietHandler.log_request = lambda *args, **kwargs: None
    server = make_server(host, port, app, handler_class=QuietHandler)
    print 'listening at %s:%d' % (host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print 'bye'

if __name__ == '__main__':
    main()

__test__ = False # keep Nose from looking into this module
