# -*- coding: utf-8 -*-

import unittest
from britney.middleware import Middleware
from britney.middleware import auth


class TestMiddlewareBase(unittest.TestCase):
    """ Test middleware base class
    """

    def setUp(self):
        self.middleware = Middleware()
        self.environ = {'spore.headers': []}

    def test_add_headers(self):
        header_one = ('Authorization', 'login:password')
        header_two = ('Content-Type', 'text/plain')
        self.middleware.add_headers(self.environ, header_one, header_two)
        self.assertEqual(len(self.environ['spore.headers']), 2)

    def test_process_request(self):
        process_request = lambda environ: None
        setattr(self.middleware, 'process_request', process_request)
        environ = {}
        self.assertIsNone(self.middleware(environ))
        self.assertEqual(environ, {'spore.headers': []})

    def test_process_request_returning_response(self):
        process_request = lambda environ: 'fake_response'
        setattr(self.middleware, 'process_request', process_request)
        environ = {}
        self.assertIsNotNone(self.middleware(environ))
        self.assertEqual(environ, {'spore.headers': []})

    def test_process_response(self):
        from functools import partial
        process_response = lambda response: response
        setattr(self.middleware, 'process_response', process_response)
        self.assertIsInstance(self.middleware({}), partial)

    def test_both_process_implemented(self):
        from functools import partial
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
        self.environ = {'spore.authentication': True, 'spore.headers': []}

    def test_auth(self):
        self.middleware(self.environ)
        header, value = self.environ['spore.headers'][0]
        self.assertEqual(header, 'Authorization')
        self.assertEqual(value, auth._basic_auth('test', '0123456789'))


class TestApiKeyAuth(unittest.TestCase):

    def setUp(self):
        self.callable_format = lambda key, user: 'ApiKey %s:%s' % (key, user)
        self.environ = {'spore.authentication': True, 'spore.headers': []}

    def test_auth_simple(self):
        middleware_simple = auth.ApiKey(key_name='X-API-Key',
                key_value='Bcdhcd7522HVGC')
        middleware_simple(self.environ)
        header, value = self.environ['spore.headers'][0]
        self.assertEqual(header, 'X-API-Key')
        self.assertEqual(value, 'Bcdhcd7522HVGC')

    def test_auth_callable(self):
        self.middleware_callable = auth.ApiKey(key_name='X-API-Key',
                key_value=self.callable_format, key='fbfryfrbfyrbfr',
                user='test')
        self.middleware_callable(self.environ)
        header, value = self.environ['spore.headers'][0]
        self.assertEqual(header, 'X-API-Key')
        self.assertEqual(value, 'ApiKey fbfryfrbfyrbfr:test')
