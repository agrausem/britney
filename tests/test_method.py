# -*- coding: utf-8 -*-

import os
import json
import unittest
from britney.core import SporeMethod
from britney.errors import SporeMethodBuildError


class TestSuccessfullBuild(unittest.TestCase):
    """
    """
    pass


class TestMethodBuilder(unittest.TestCase):
    """
    """

    def setUp(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'method.json')
        with open(path, 'r') as method_data:
            self.data = json.loads(method_data.read())

    def tearDown(self):
        pass

    def r_test_missing_required_parameters(self):
        """
        """
        with self.assertRaises(SporeMethodBuildError) as build_error:
            SporeMethod()


        self.assertListEqual(sorted(build_error.errors.keys()), ['base_url',
            'method', 'name', 'path'])

    def test_base_url(self):
        """
        """
        method = SporeMethod(method='GET', name='test_method', path='/test',
                api_base_url='http://my_test.org')
        self.assertEqual(method.base_url, 'http://my_test.org')

        method = SporeMethod(method='GET', name='test_method', path='/test',
                api_base_url='http://my_test.org',
                base_url='http://my_test2.org')
        self.assertEqual(method.base_url, 'http://my_test2.org')

        method = SporeMethod(method='GET', name='test_method', path='/test',
                base_url='http://my_test2.org')
        self.assertEqual(method.base_url, 'http://my_test2.org')

    def test_formats(self):
        """
        """
        method = SporeMethod(method='GET', name='test_method', path='/test',
                api_base_url='http://my_test.org', formats=['json'])
        self.assertListEqual(method.formats, ['json'])

        method = SporeMethod(method='GET', name='test_method', path='/test',
                api_base_url='http://my_test.org', formats=['json'],
                global_formats=['json', 'xml'])
        self.assertListEqual(method.formats, ['json'])

        method = SporeMethod(method='GET', name='test_method', path='/test',
                api_base_url='http://my_test.org',
                global_formats=['json', 'xml'])
        self.assertListEqual(method.formats, ['json', 'xml'])

    def test_authentication(self):
        """
        """
        method = SporeMethod(method='GET', name='test_method', path='/test',
                api_base_url='http://my_test.org', global_authentication=True)
        self.assertTrue(method.authentication)

        method = SporeMethod(method='GET', name='test_method', path='/test',
                api_base_url='http://my_test.org', authentication=True)
        self.assertTrue(method.authentication)

        method = SporeMethod(method='GET', name='test_method', path='/test',
                api_base_url='http://my_test.org', global_authentication=True,
                authentication=False)
        self.assertFalse(method.authentication)
            
        method = SporeMethod(method='GET', name='test_method', path='/test',
                api_base_url='http://my_test.org')
        self.assertFalse(method.authentication)

    def test_environ_url(self):
        """
        """
        for data in self.data:
            environ = data.pop('environ')
            method = SporeMethod(name='test', **data)
            base_environ = method.base_environ()
            for key in environ:
                self.assertEqual(base_environ[key], environ[key])
