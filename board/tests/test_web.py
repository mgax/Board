import unittest
import wsgiref.util

from board import model
from board import configure
from board.interfaces import INoteWsgiApp


class WebTest(unittest.TestCase):
    def setUp(self):
        configure.setup_components()

    def test_adapter(self):
        note = model.Note({'a': 'some test value'})
        app = INoteWsgiApp(note)
        self.assertTrue(callable(app))

        environ = {}
        wsgiref.util.setup_testing_defaults(environ)
        response = {}
        def start_response(status, headers):
            response.update({'status': status, 'headers': headers})

        response_body = app(environ, start_response)
        self.assertTrue('some test value' in ''.join(response_body))
