# -*- coding: utf-8 -*-

import os
import json
import unittest
from britney.core import SporeMethod
from britney import errors
from functools import partial


class TestSuccessfullBuild(unittest.TestCase):
    """
    """
    pass


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

    def too_much_args(self):
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
        

class TestMethodBuilder(unittest.TestCase):
    """
    """

    def setUp(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'method.json')
        with open(path, 'r') as method_data:
            self.data = json.loads(method_data.read())


    def tearDown(self):
        pass


    def test_environ_url(self):
        """
        """
        for data in self.data:
            environ = data.pop('environ')
            method = SporeMethod(name='test', **data)
            base_environ = method.base_environ()
            for key in environ:
                self.assertEqual(base_environ[key], environ[key])
