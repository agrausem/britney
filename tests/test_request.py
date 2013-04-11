# -*- coding: utf-8 -*-


import os
import json
import unittest
from britney.request import RequestBuilder


class TestRequestBuilderUrl(unittest.TestCase):
    """
    """

    def setUp(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'request.json')
        with open(path, 'r') as method_data:
            self.data = json.loads(method_data.read())

    def test_good_url(self):
        """
        """
        for test_data in self.data:
            built_request = RequestBuilder(test_data['env'])
            """
            for property_ in ('netloc', 'base_url', 'path'):
                self.assertEqual(getattr(property_, built_request),
                        test_data[property_])
            """
            self.assertEqual(built_request.uri, test_data['url'])
