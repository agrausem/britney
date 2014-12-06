# -*- coding: utf-8 -*-

import json
import os
import requests
import unittest
from britney import errors
from britney import spyre
from britney.core import Spore
from britney.core import SporeMethod
from britney.middleware import auth
from britney.middleware import format as content_type


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

    def test_enable_as_string(self):
        self.client.enable('Json')
        self.assertIsInstance(self.client.middlewares[0][1], content_type.Json)

    def test_middleware_not_found(self):
        with self.assertRaises(AttributeError) as not_found:
            self.client.enable('func', username='my_login',
                               password='my_password')

        self.assertEqual(str(not_found.exception),
                         'Unknown middleware func')

    def test_middleware_not_a_callable(self):
        with self.assertRaises(ValueError):
            self.client.enable(('func', 'func2'), username='my_login',
                               password='my_password')

    def test_middleware_with_bad_args(self):
        with self.assertRaises(TypeError):
            self.client.enable('ApiKey', name="name", value="value")


class TestDefaultParametersValue(unittest.TestCase):
    """
    """

    def setUp(self):
        self.client = Spore(name='my_client', base_url='http://my_url.org',
                            methods={
                                'my_method': {
                                    'method': 'GET',
                                    'path': '/api'
                                },
                                'my_req_method': {
                                    'method': 'GET',
                                    'path': '/api',
                                    'required_params': ['format']
                                }, 'my_opt_method': {
                                    'method': 'GET',
                                    'path': '/api',
                                    'optional_params': ['format']
                                }, 'my_both_method': {
                                    'method': 'GET',
                                    'path': '/api',
                                    'required_params': ['format'],
                                    'optional_params': ['username']
                                }, 'my_super_method': {
                                    'method': 'GET',
                                    'path': '/api',
                                    'required_params': ['format',
                                                        'last_name'],
                                    'optional_params': ['first_name']
                                }})
        self.client.add_default('format', 'json')
        self.client.add_default('username', 'toto')

    def test_default(self):
        self.assertEqual(self.client.defaults['format'], 'json')
        self.assertEqual(self.client.defaults['username'], 'toto')

    def test_method_default(self):
        self.assertEqual(self.client.my_method.defaults['format'], 'json')
        self.assertEqual(self.client.my_method.defaults['username'], 'toto')

    def test_remove_default(self):
        self.client.remove_default('format')
        self.assertEqual(self.client.defaults['username'], 'toto')

    def test_method_remove_default(self):
        self.client.remove_default('format')
        self.assertEqual(self.client.my_method.defaults['username'], 'toto')

    def test_remove_default_not_existing(self):
        self.client.remove_default('id')
        self.assertEqual(self.client.defaults['format'], 'json')
        self.assertEqual(self.client.defaults['username'], 'toto')

    def test_not_impacted(self):
        params = self.client.my_method.build_params()
        self.assertListEqual(params, [])

    def test_required(self):
        params = self.client.my_req_method.build_params()
        self.assertListEqual(params, [('format', 'json')])

    def test_optional(self):
        params = self.client.my_opt_method.build_params()
        self.assertListEqual(params, [('format', 'json')])

    def test_both(self):
        params = self.client.my_both_method.build_params()
        self.assertListEqual(sorted(params), 
                             [('format', 'json'), ('username', 'toto')])

    def test_with_params(self):
        params = self.client.my_super_method.build_params(last_name='toto')
        self.assertListEqual(sorted(params), 
                             [('format', 'json'), ('last_name', 'toto')])

    def test_missing(self):
        with self.assertRaises(errors.SporeMethodCallError):
            self.client.my_super_method.build_params()


class TestClientGenerator(unittest.TestCase):

    def setUp(self):
        self.data_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'descriptions')

    def test_no_description_file(self):
        with self.assertRaises(IOError) as io_error:
            spyre('/path/dont/exist/api.json')
        
    def test_no_description_url(self):
        with self.assertRaises(IOError) as http_error:
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

    def test_multiple_clients_with_same_method_names(self):
        client1 = spyre(os.path.join(self.data_path, 'api.json'))
        client2 = spyre(os.path.join(self.data_path, 'api2.json'))
        self.assertFalse(client1.test_requires == client2.test_requires)

