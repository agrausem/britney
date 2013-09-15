# -*- coding: utf-8 -*-


import os
import json
import unittest
from britney.request import RequestBuilder


class TestRequestBuilderUrl(unittest.TestCase):

    def setUp(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'request.json')
        with open(path, 'r') as method_data:
            self.data = json.loads(method_data.read())

    def test_good_url(self):
        for test_data in self.data:
            built_request = RequestBuilder(test_data['env'])
            self.assertEqual(built_request.uri, test_data['url'])

    def test_headers(self):
        environ = {'spore.headers': [('Authorization', 'cdbcdvvvfvf=='),
            ('Content-Type', 'text/plain')]}
        environ.update(self.data[0]['env'])
        built_request = RequestBuilder(environ)
        headers = built_request.headers()
        self.assertIn('Authorization', headers)
        self.assertIn('Content-Type', headers)
        self.assertEqual(headers['Authorization'], 'cdbcdvvvfvf==')
        self.assertEqual(headers['Content-Type'], 'text/plain')

    def test_payload(self):
        environ = {'spore.payload': {'param': 'test'}}
        environ.update(self.data[0]['env'])
        built_request = RequestBuilder(environ)
        payload = built_request.data()
        self.assertEqual(payload, {'param': 'test'})
