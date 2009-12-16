import unittest
import wsgiref.util
import wsgiref.validate
import json
from StringIO import StringIO

import webob

from board import model

def wsgi_get(app, url):
    app = wsgiref.validate.validator(app)
    environ = {'PATH_INFO': url, 'QUERY_STRING': '', 'SCRIPT_NAME': ''}
    wsgiref.util.setup_testing_defaults(environ)
    response = dict()
    def start_response(status, headers):
        response.update({'status': status, 'headers': headers})
    ret = app(environ, start_response)
    response['body'] = ''.join(ret)
    ret.close()
    return response

class WebTest(unittest.TestCase):
    def test_adapter(self):
        note = model.Note({'a': 'some test value'})
        app = note.get_delegate().wsgi
        response = wsgi_get(app, '/')
        json_content_type = ('Content-Type', 'application/json')
        self.assertTrue(json_content_type in response['headers'])
        data = json.loads(response['body'])
        self.assertEqual(data, {'properties': {'a': 'some test value'}})

    def test_traversal(self):
        root = model.Note({'content': 'white'})
        k1 = model.Note({'-name-': 'k1', 'content': 'red'})
        root.append_child(k1)
        k2 = model.Note({'-name-': 'k2', 'content': 'green'})
        root.append_child(k2)
        k11 = model.Note({'-name-': 'k11', 'content': 'blue'})
        k1.append_child(k11)

        def assert_content(expected_fragment, response):
            self.assertEqual(response['status'], '200 OK')
            body = response['body']
            for fragment in ['white', 'red', 'green', 'blue']:
                if expected_fragment == fragment:
                    self.assertTrue(fragment in body)
                else:
                    self.assertFalse(fragment in body)

        def assert_404(response):
            self.assertEqual(response['status'], '404 Not Found')

        root_app = root.get_delegate().wsgi
        assert_content('white', wsgi_get(root_app, '/'))
        assert_content('red', wsgi_get(root_app, '/c:k1'))
        assert_content('red', wsgi_get(root_app, '/c:k1/'))
        assert_content('blue', wsgi_get(root_app, '/c:k1/c:k11'))
        assert_content('blue', wsgi_get(root_app, '/c:k1/c:k11/'))
        assert_content('green', wsgi_get(root_app, '/c:k2'))
        assert_content('green', wsgi_get(root_app, '/c:k2/'))
        assert_404(wsgi_get(root_app, '/c:'))
        assert_404(wsgi_get(root_app, '/k1'))
        assert_404(wsgi_get(root_app, '/k1/c:k11'))
        assert_404(wsgi_get(root_app, '/c:asdf'))
        assert_404(wsgi_get(root_app, '/c:k1xxx'))
        assert_404(wsgi_get(root_app, '/c:k1/c:asdf'))
        assert_404(wsgi_get(root_app, '/c:k1/c:asdf/'))
        assert_404(wsgi_get(root_app, '/c:k1/c:asdf/c:k11'))

        k1_app = k1.get_delegate().wsgi
        assert_content('red', wsgi_get(k1_app, '/'))
        assert_content('blue', wsgi_get(k1_app, '/c:k11'))
        assert_content('blue', wsgi_get(k1_app, '/c:k11/'))
        assert_404(wsgi_get(k1_app, '/c:k1'))
        assert_404(wsgi_get(k1_app, '/c:k2'))

    def test_change_properties(self):
        note = model.Note({'a': 'b'})

        req = webob.Request({'wsgi.input': StringIO()}, method='POST')
        req.POST['action'] = 'set_props'
        req.POST['data'] = '{"x": "y"}'
        res = req.get_response(note.get_delegate().wsgi)
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(dict(note), {'a': 'b', 'x': 'y'})

        req = webob.Request({'wsgi.input': StringIO()}, method='POST')
        req.POST['action'] = 'set_props'
        req.POST['data'] = '{"a": null}'
        res = req.get_response(note.get_delegate().wsgi)
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(dict(note), {'x': 'y'})
