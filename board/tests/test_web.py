import unittest
import wsgiref.util
import wsgiref.validate
import json

from board import model
from board import configure
from board.interfaces import INoteWsgiApp

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
    def setUp(self):
        configure.setup_components()

    def test_adapter(self):
        note = model.Note({'a': 'some test value'})
        app = INoteWsgiApp(note)
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

        root_app = INoteWsgiApp(root)
        assert_content('white', wsgi_get(root_app, '/'))
        assert_content('red', wsgi_get(root_app, '/k1'))
        assert_content('red', wsgi_get(root_app, '/k1/'))
        assert_content('blue', wsgi_get(root_app, '/k1/k11'))
        assert_content('blue', wsgi_get(root_app, '/k1/k11/'))
        assert_content('green', wsgi_get(root_app, '/k2'))
        assert_content('green', wsgi_get(root_app, '/k2/'))
        assert_404(wsgi_get(root_app, '/asdf'))
        assert_404(wsgi_get(root_app, '/k1xxx'))
        assert_404(wsgi_get(root_app, '/k1/asdf'))
        assert_404(wsgi_get(root_app, '/k1/asdf/'))
        assert_404(wsgi_get(root_app, '/k1/asdf/k11'))

        k1_app = INoteWsgiApp(k1)
        assert_content('red', wsgi_get(k1_app, '/'))
        assert_content('blue', wsgi_get(k1_app, '/k11'))
        assert_content('blue', wsgi_get(k1_app, '/k11/'))
        assert_404(wsgi_get(k1_app, '/k1'))
        assert_404(wsgi_get(k1_app, '/k2'))
