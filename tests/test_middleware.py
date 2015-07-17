# -*- coding: utf-8 -*-

import unittest
from britney.middleware.base import Middleware, add_header
from britney.middleware import auth
from britney.middleware import format as format_
from functools import partial


class TestMiddlewareBase(unittest.TestCase):
    """ Test middleware base class
    """

    def setUp(self):
        self.middleware = Middleware()
        self.environ = {'spore.headers': {}}

    def test_add_headers(self):
        header_one = ('Authorization', 'login:password')
        header_two = ('Content-Type', 'text/plain')
        add_header(self.environ, *header_one)
        add_header(self.environ, *header_two)
        self.assertEqual(len(self.environ['spore.headers']), 2)

    def test_process_request(self):
        process_request = lambda environ: None
        setattr(self.middleware, 'process_request', process_request)
        environ = {}
        self.assertIsNone(self.middleware(environ))
        self.assertEqual(environ, {'spore.headers': {}})

    def test_process_request_returning_response(self):
        process_request = lambda environ: 'fake_response'
        setattr(self.middleware, 'process_request', process_request)
        environ = {}
        self.assertIsNotNone(self.middleware(environ))
        self.assertEqual(environ, {'spore.headers': {}})

    def test_process_response(self):
        process_response = lambda response: response
        setattr(self.middleware, 'process_response', process_response)
        self.assertIsInstance(self.middleware({}), partial)

    def test_both_process_implemented(self):
        process_response = lambda response: response
        setattr(self.middleware, 'process_response', process_response)
        process_request = lambda environ: None
        setattr(self.middleware, 'process_request', process_request)
        self.assertIsInstance(self.middleware({}), partial)

    def test_both_implemented_but_bypass(self):
        process_response = lambda response: response
        setattr(self.middleware, 'process_response', process_response)
        process_request = lambda environ: 'fake_response'
        setattr(self.middleware, 'process_request', process_request)
        self.assertEqual(self.middleware({}), 'fake_response')


class TestAuthMiddlewareBase(unittest.TestCase):

    def setUp(self):
        self.middleware = auth.Auth()
        self.environ = {'spore.authentication': True}

    def test_needs_auth(self):
        self.assertTrue(self.middleware.needs_auth(self.environ))

    def test_dont_need_auth(self):
        self.environ['spore.authentication'] = False
        self.assertFalse(self.middleware.needs_auth(self.environ))


class TestBasicAuth(unittest.TestCase):

    def setUp(self):
        self.middleware = auth.Basic(username='test', password='0123456789')
        self.environ = {'spore.authentication': True, 'spore.headers': {}}

    def test_auth(self):
        self.middleware(self.environ)
        self.assertEqual(self.environ['spore.headers']['Authorization'],
                         auth._basic_auth('test', '0123456789'))


class TestApiKeyAuth(unittest.TestCase):

    def setUp(self):
        self.callable_format = lambda key, user: 'ApiKey %s:%s' % (key, user)
        self.environ = {'spore.authentication': True, 'spore.headers': {}}

    def test_auth_simple(self):
        middleware_simple = auth.ApiKey(key_name='X-API-Key',
                key_value='Bcdhcd7522HVGC')
        middleware_simple(self.environ)
        self.assertEqual(self.environ['spore.headers']['X-API-Key'],
                         'Bcdhcd7522HVGC')

    def test_auth_callable(self):
        self.middleware_callable = auth.ApiKey(key_name='X-API-Key',
                key_value=self.callable_format, key='fbfryfrbfyrbfr',
                user='test')
        self.middleware_callable(self.environ)
        self.assertEqual(self.environ['spore.headers']['X-API-Key'],
                         'ApiKey fbfryfrbfyrbfr:test')


class TestBaseFormatMiddleware(unittest.TestCase):

    class Quoted(format_.Format):

        content_type = 'quoted'
        accept = 'quoted'

        def dump(self, data):
            return "'%s'" % data

        def load(self, data):
            return data.strip("'")

    def setUp(self):
        self.middleware = self.Quoted()
        self.environ = {'spore.payload': None, 'spore.headers': {}, 'spore.payload_format': ''}

    def test_process_request_without_payload(self):
        self.assertIsNone(self.middleware.process_request(self.environ))
        self.assertDictEqual(self.environ['spore.headers'],
                {'Accept': 'quoted'})

    def test_process_request_with_payload(self):
        self.environ['spore.payload'] = 'my_payload'
        self.assertIsNone(self.middleware.process_request(self.environ))
        self.assertDictEqual(self.environ['spore.headers'], {
            'Accept': 'quoted',
            'Content-Length': len("'my_payload'"),
            'Content-Type': 'quoted'
        })
        self.assertEqual(self.environ['spore.payload'], "'my_payload'")

    def test_process_response(self):
       Response = type('Response', (object, ), {'text': "'my_content'",
           'data': ""})
       response = Response()
       self.assertIsNotNone(self.middleware.process_response(response))
       self.assertEqual(response.data, "my_content")


class TestJsonFormatMiddleware(unittest.TestCase):

    def setUp(self):
        self.middleware = format_.Json()
        self.environ = {'spore.payload': {'data': 'my_data'},
                        'spore.headers': {},
                        'spore.payload_format': ''}

    def test_calling_middleware(self):
        callback = self.middleware(self.environ)
        self.assertIsInstance(callback, partial)
        self.assertDictEqual(self.environ['spore.headers'], {
            'Accept': 'application/json',
            'Content-Length': len('{"data": "my_data"}'),
            'Content-Type': 'application/json'
        })
        self.assertEqual(self.environ['spore.payload'], '{"data": "my_data"}')
        Response = type('Response', (object, ), {
           'text': '{"content": "my_content"}', 'data': ""})
        response = Response()
        callback(response)
        self.assertDictEqual(response.data, {'content': 'my_content'})
