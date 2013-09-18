# -*- coding: utf-8 -*-

import json
import os
import requests
from six import StringIO
import unittest
from britney import errors
from britney import spyre
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


class TestClientGenerator(unittest.TestCase):

    def setUp(self):
        self.data_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'descriptions')

    def test_no_description_file(self):
        with self.assertRaises(IOError) as io_error:
            spyre('/path/dont/exist/api.json')
        
    def test_no_description_url(self):
        with self.assertRaises(requests.ConnectionError) as http_error:
            spyre('http://description.not.fou.nd/api.json')

    def test_no_valid_json_document(self):
        with self.assertRaises(ValueError) as json_error:
            json_file = os.path.join(self.data_path, 'no_api.json')
            spyre(json_file)

    def test_without_base_url(self):
        json_file = os.path.join(self.data_path, 'api.json')
        client = spyre(json_file)
        with open(json_file, 'r') as api_description:
            content = json.loads(api_description.read())
            self.assertEqual(client.base_url, content['base_url'])

    def test_with_base_url(self):
        json_file = os.path.join(self.data_path, 'api.json')
        client = spyre(json_file, base_url='http://my_base.url/')
        self.assertEqual(client.base_url, 'http://my_base.url/')

    def test_has_methods(self):
        json_file = os.path.join(self.data_path, 'api.json')
        client = spyre(json_file, base_url='http://my_base.url/')
        with open(json_file, 'r') as api_description:
            content = json.loads(api_description.read())
            for method in content['methods']:
                self.assertEqual(getattr(client, method).name, method) 

