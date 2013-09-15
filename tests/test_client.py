# -*- coding: utf-8 -*-

import unittest
from britney import errors
from britney.core import Spore
from britney.core import SporeMethod
from britney.middleware import auth


class TestClientBuilder(unittest.TestCase):
    """ Test client generation, errors catched in REST description and
    representation
    """

    def test_missing_required_in_desc(self):
        with self.assertRaises(errors.SporeClientBuildError) as build_error:
            Spore()

        error = build_error.exception
        self.assertIn('name', error.errors)
        self.assertIn('base_url', error.errors)
        self.assertIn('methods', error.errors)

    def test_representation(self):
        client = Spore(name='my_client', base_url='http://my_url.org',
                methods={'my_method': {'method': 'GET', 'path': '/api'}})
        self.assertEqual(repr(client), '<Spore [my_client]>')

    def test_default_attrs(self):
        client = Spore(name='my_client', base_url='http://my_url.org',
                methods={'my_method': {'method': 'GET', 'path': '/api'}})
        self.assertEqual(client.name, 'my_client')
        self.assertEqual(client.base_url, 'http://my_url.org')
        self.assertIsInstance(getattr(client, 'my_method'), SporeMethod)
        self.assertEqual(client.authority, '')
        self.assertIsNone(client.authentication)
        self.assertEqual(client.version, '')
        self.assertEqual(client.formats, [])
        self.assertEqual(client.meta, {})
        self.assertEqual(client.middlewares, [])

    def test_bad_method_description(self):
        with self.assertRaises(errors.SporeClientBuildError) as build_error:
            Spore(name='my_client', base_url='http://my_url.org',
                methods={'my_method': {'method': 'GET'}})

        error = build_error.exception
        self.assertIn('my_method', error.errors['methods'])


class TestClientMiddleware(unittest.TestCase):
    """ Test enabling middlewares on conditions or not
    """


    def setUp(self):
        self.client = Spore(name='my_client', base_url='http://my_url.org',
                methods={'my_method': {'method': 'GET', 'path': '/api'}})

    def test_enable(self):
        self.client.enable(auth.Basic, username='my_login',
                password='my_password')
        self.assertIsInstance(self.client.middlewares[0], type(()))
        self.assertIsInstance(self.client.middlewares[0][1], auth.Basic)

    def test_enable_if(self):
        self.client.enable_if(lambda request: bool(request['payload']), 
                auth.Basic, username='my_login', password='my_password')
        self.assertIsInstance(self.client.middlewares[0], type(()))
        self.assertIsInstance(self.client.middlewares[0][1], auth.Basic)

        request = {'payload': {'arg': 1}}
        self.assertTrue(self.client.middlewares[0][0](request))
        request = {'payload': {}}
        self.assertFalse(self.client.middlewares[0][0](request))

    def test_enable_failed(self):
        with self.assertRaises(ValueError) as callable_error:
            self.client.enable('func', username='my_login',
                    password='my_password')
