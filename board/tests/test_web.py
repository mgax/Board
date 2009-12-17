import unittest
import wsgiref.util
from wsgiref.validate import validator
import json
from StringIO import StringIO

import webob

from board import model

def test_request(environ={}, **kwargs):
    environ = dict(environ)
    environ.setdefault('SERVER_NAME', 'example.com')
    environ.setdefault('QUERY_STRING', '')
    environ.setdefault('SCRIPT_NAME', '')
    wsgiref.util.setup_testing_defaults(environ)
    return webob.Request(environ, **kwargs)

def wsgi_get(app, url):
    environ = {'PATH_INFO': url, 'QUERY_STRING': '', 'SCRIPT_NAME': ''}
    wsgiref.util.setup_testing_defaults(environ)
    response = dict()
    def start_response(status, headers):
        response.update({'status': status, 'headers': headers})
    ret = validator(app)(environ, start_response)
    response['body'] = ''.join(ret)
    ret.close()
    return response

def check_json_response(response):
    body = response.body # making sure we finish reading the body iterator
    assert response.status == '200 OK'
    assert response.content_type == 'application/json'
    return json.loads(body)

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

        req = test_request(method='POST')
        req.POST['action'] = 'set_props'
        req.POST['data'] = '{"x": "y"}'
        # don't use the validator, since webob uses -1 for content length
        res = req.get_response(note.get_delegate().wsgi)
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(dict(note), {'a': 'b', 'x': 'y'})

        req = test_request(method='POST')
        req.POST['action'] = 'set_props'
        req.POST['data'] = '{"a": null}'
        res = req.get_response(note.get_delegate().wsgi)
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(dict(note), {'x': 'y'})

    def test_list_children(self):
        k1 = model.Note({'-name-': 'kidone'})
        k2 = model.Note({'-name-': 'kidtwo'})
        note = model.Note(children=[k1, k2])

        req = test_request({'PATH_INFO': '/children'})
        res = req.get_response(validator(note.get_delegate().wsgi))
        data = check_json_response(res)
        self.assertEqual(data, {'children': ['http://example.com/c:kidone',
                                             'http://example.com/c:kidtwo']})

    def test_create_child(self):
        k2 = model.Note({'-name-': 'kidtwo'})
        k1 = model.Note({'-name-': 'kidone'}, children=[k2])
        note = model.Note(children=[k1])

        req = test_request({'PATH_INFO': '/c:kidone/children'}, method='PUT')
        req.body = json.dumps({'-name-': 'newkid', 'something': 'for nothing'})
        # don't use the validator, since webob uses -1 for content length
        res = req.get_response(note.get_delegate().wsgi)
        self.assertEqual(res.status, '303 See Other')
        self.assertEqual(res.headers['Location'],
                         'http://example.com/c:kidone/c:newkid')

        req = test_request({'PATH_INFO': '/c:kidone/c:newkid'})
        res = req.get_response(validator(note.get_delegate().wsgi))
        data = check_json_response(res)
        self.assertEqual(data['properties']['something'], 'for nothing')

    def test_create_child_bad_request(self):
        k2 = model.Note({'-name-': 'kidtwo'})
        k1 = model.Note({'-name-': 'kidone'}, children=[k2])
        note = model.Note(children=[k1])

        # non-JSON data
        req = test_request({'PATH_INFO': '/c:kidone/children'}, method='PUT')
        req.body = 'non-json data'
        res = req.get_response(note.get_delegate().wsgi)
        self.assertEqual(res.status, '400 Bad Request')

        # JSON, but not dict
        req = test_request({'PATH_INFO': '/c:kidone/children'}, method='PUT')
        req.body = json.dumps('hi there')
        res = req.get_response(note.get_delegate().wsgi)
        self.assertEqual(res.status, '400 Bad Request')

        # dict, but values not all strings
        req = test_request({'PATH_INFO': '/c:kidone/children'}, method='PUT')
        req.body = json.dumps({'a': 'b', 'a-list': ['1', '2']})
        res = req.get_response(note.get_delegate().wsgi)
        self.assertEqual(res.status, '400 Bad Request')

        # missing -name-
        req = test_request({'PATH_INFO': '/c:kidone/children'}, method='PUT')
        req.body = json.dumps({'a': 'b'})
        res = req.get_response(note.get_delegate().wsgi)
        self.assertEqual(res.status, '400 Bad Request')

        # and finally a good one
        req = test_request({'PATH_INFO': '/c:kidone/children'}, method='PUT')
        req.body = json.dumps({'-name-': 'b'})
        res = req.get_response(note.get_delegate().wsgi)
        self.assertEqual(res.status, '303 See Other')
