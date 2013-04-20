# -*- coding: utf-8 -*-

from functools import partial
import json
import os
import unittest
from britney.core import SporeMethod
from britney import errors


class TestMethodAuthentication(unittest.TestCase):
    """ Tests the value of the authentication attribute of a method, coming
    from both local and global parameters of the description.
    """

    def setUp(self):
        self.method = partial(SporeMethod, method='GET', name='test_method',
                path='/test', api_base_url='http://my_test.org') 

    def test_with_global_param_only(self):
        method = self.method(global_authentication=True)
        self.assertTrue(method.authentication)

    def test_with_local_param_only(self):
        method = self.method(authentication=True)
        self.assertTrue(method.authentication)

    def test_with_global_but_not_local_param(self):
        method = self.method(authentication=False, global_authentication=True)
        self.assertFalse(method.authentication)

    def test_with_local_but_not_global_param(self):
        method = self.method(authentication=True, global_authentication=False)
        self.assertTrue(method.authentication)

    def test_with_both_params(self):
        method = self.method(authentication=True, global_authentication=True)
        self.assertTrue(method.authentication)

    def test_with_not_both_params(self):
        method = self.method(authentication=False, global_authentication=False)
        self.assertFalse(method.authentication)

    def test_with_no_auth_param(self):
        method = self.method()
        self.assertFalse(method.authentication)


class TestMethodFormats(unittest.TestCase):
    """ Tests the value of the formats attribute of a method, coming from both
    local and global parameters of the description
    """

    def setUp(self):
        self.method = partial(SporeMethod, method='GET', name='test_method',
                path='/test', api_base_url='http://my_test.org') 

    def test_with_global_param_only(self):
        method = self.method(global_formats=['json', 'xml'])
        self.assertListEqual(method.formats, ['json', 'xml'])

    def test_with_local_param_only(self):
        method = self.method(formats=['json'])
        self.assertListEqual(method.formats, ['json'])

    def test_with_both_params(self):
        method = self.method(formats=['json'], global_formats=['json', 'xml'])
        self.assertListEqual(method.formats, ['json'])

    def test_with_no_auth_param(self):
        method = self.method()
        self.assertIsNone(method.formats)


class TestMethodRequiredParameters(unittest.TestCase):
    """ Tests the value of the built parameters in case of required and
    optional parameters defined in description, and the exceptions raised when
    params are missing or too much args are passed
    """

    def setUp(self):
        self.method = partial(SporeMethod, method='GET', name='test_method',
                path='/test', api_base_url='http://my_test.org') 
        
    def test_no_required_params(self):
        method = self.method()
        self.assertListEqual(method.build_params(), [])

    def test_missing_required_args(self):
        method = self.method(required_params=['user_id', 'format'])

        with self.assertRaises(errors.SporeMethodCallError) as call_error:
            method.build_params(user_id='2')

        error = call_error.exception
        self.assertEqual(error.cause, 'Required parameters are missing')
        self.assertEqual(error.expected_values, set(['format']))

    def test_too_much_args(self):
        method = self.method(required_params=['user_id', 'format'],
                optional_params=['page'])

        with self.assertRaises(errors.SporeMethodCallError) as call_error:
            method.build_params(user_id=2, format='json', page=3,
                    offset=True)

        error = call_error.exception
        self.assertEqual(error.cause, 'Too much parameter')
        self.assertEqual(error.expected_values, set(['offset']))
        
    def test_required_and_optional_args(self):
        method = self.method(required_params=['user_id', 'format'],
                optional_params=['page'])
        params = method.build_params(user_id=2, format='json', page=3)
        self.assertEqual(len(params), 3)

        keys = [param[0] for param in params]
        self.assertListEqual(sorted(keys), ['format', 'page', 'user_id'])

        values = [param[1] for param in params]
        self.assertListEqual(sorted(values), [2, 3, 'json'])


class TestMethodBaseUrl(unittest.TestCase):
    """ Tests the value of the base_url attribute of a method, coming
    from both local and global parameters of the description.
    """

    def setUp(self):
        self.method = partial(SporeMethod, method='GET', name='test_method',
                path='/test') 

    def test_with_global_base_url_only(self):
        method = self.method(api_base_url='http://api.test.org/')
        self.assertEqual(method.base_url, 'http://api.test.org/')

    def test_with_local_base_url_only(self):
        method = self.method(base_url='http://api.test.org/v2/')
        self.assertEqual(method.base_url, 'http://api.test.org/v2/')
    
    def test_with_both_base_url(self):
        method = self.method(api_base_url='http://api.test.org/',
                base_url='http://api.test.org/v2/')
        self.assertEqual(method.base_url, 'http://api.test.org/v2/')

    def test_with_no_base_url(self):
        with self.assertRaises(errors.SporeMethodBuildError) as build_error:
            self.method()

        error = build_error.exception
        self.assertTrue(error.errors.has_key('base_url'))


class TestMethodBaseEnviron(unittest.TestCase):
    """ Tests the build of the base environment of a request based on WSGI
    specification in fact of the JSON description of a REST API.
    """

    def setUp(self):
        pass

    def test_userinfo(self):
        method = SporeMethod(method='GET', name='test_method', path='/test',
                base_url='http://toto:123456789@api.test.org/') 
        base_environ = method.base_environ()
        self.assertEqual(base_environ['spore.userinfo'], 'toto:123456789')
        self.assertEqual(base_environ['SERVER_NAME'], 'api.test.org')
        self.assertEqual(base_environ['SERVER_PORT'], 80)
        self.assertEqual(base_environ['SCRIPT_NAME'], '')
        self.assertEqual(base_environ['PATH_INFO'], '/test')
        self.assertEqual(base_environ['QUERY_STRING'], '')
        self.assertEqual(base_environ['wsgi.url_scheme'], 'http')

    def test_script_name(self):
        method = SporeMethod(method='GET', name='test_method', path='/test',
                base_url='http://api.test.org/v2/')
        base_environ = method.base_environ()
        self.assertEqual(base_environ['spore.userinfo'], '')
        self.assertEqual(base_environ['SERVER_NAME'], 'api.test.org')
        self.assertEqual(base_environ['SERVER_PORT'], 80)
        self.assertEqual(base_environ['SCRIPT_NAME'], '/v2')
        self.assertEqual(base_environ['PATH_INFO'], '/test')
        self.assertEqual(base_environ['QUERY_STRING'], '')
        self.assertEqual(base_environ['wsgi.url_scheme'], 'http')
        
    def test_path_and_query(self):
        method = SporeMethod(method='GET', name='test_method',
                path='/test?format=json', base_url='http://api.test.org/v2/')
        base_environ = method.base_environ()
        self.assertEqual(base_environ['spore.userinfo'], '')
        self.assertEqual(base_environ['SERVER_NAME'], 'api.test.org')
        self.assertEqual(base_environ['SERVER_PORT'], 80)
        self.assertEqual(base_environ['SCRIPT_NAME'], '/v2')
        self.assertEqual(base_environ['PATH_INFO'], '/test')
        self.assertEqual(base_environ['QUERY_STRING'], 'format=json')
        self.assertEqual(base_environ['wsgi.url_scheme'], 'http')

    def test_https(self):
        method = SporeMethod(method='GET', name='test_method', path='/test',
                base_url='https://api.test.org/')
        base_environ = method.base_environ()
        self.assertEqual(base_environ['spore.userinfo'], '')
        self.assertEqual(base_environ['SERVER_NAME'], 'api.test.org')
        self.assertEqual(base_environ['SERVER_PORT'], 443)
        self.assertEqual(base_environ['SCRIPT_NAME'], '')
        self.assertEqual(base_environ['PATH_INFO'], '/test')
        self.assertEqual(base_environ['QUERY_STRING'], '')
        self.assertEqual(base_environ['wsgi.url_scheme'], 'https')

    def test_server_port(self):
        method = SporeMethod(method='GET', name='test_method', path='/test',
                base_url='https://api.test.org:8081/')
        base_environ = method.base_environ()
        self.assertEqual(base_environ['spore.userinfo'], '')
        self.assertEqual(base_environ['SERVER_NAME'], 'api.test.org')
        self.assertEqual(base_environ['SERVER_PORT'], 8081)
        self.assertEqual(base_environ['SCRIPT_NAME'], '')
        self.assertEqual(base_environ['PATH_INFO'], '/test')
        self.assertEqual(base_environ['QUERY_STRING'], '')
        self.assertEqual(base_environ['wsgi.url_scheme'], 'https')
