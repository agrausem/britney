import unittest
import britney
from britney.middleware import Json
from britney.middleware.base import Middleware
from os.path import abspath, dirname, join
import responses
from datetime import datetime


class OrderMiddleware(Middleware):

    def process_order(self, response):
        if hasattr(response, 'order'):
            response.order.append(self.__class__.__name__)
        else:
            response.order = [self.__class__.__name__]


class JsonOrder(OrderMiddleware, Json):

    def process_response(self, response):
        self.process_order(response)
        return super(JsonOrder, self).process_response(response)


class Timer(OrderMiddleware):

    def process_request(self, environ):
        self.timer = datetime.now()

    def process_response(self, response):
        self.process_order(response)
        response.time = datetime.now() - self.timer
        return response


class TestSporeResponse(unittest.TestCase):

    description_path = join(dirname(abspath(__file__)), 'descriptions')

    def setUp(self):
        self.client = britney.new(join(self.description_path, 'api.json'))

    @responses.activate
    def test_simple_method(self):
        responses.add(responses.GET, 'http://test.api.org/test',
                      body='{"test": "good"}', status=200,
                      content_type='application/json')

        response = self.client.test()

        self.assertEqual(response.text, '{"test": "good"}')
        self.assertEqual(response.status_code, 200)

    @responses.activate
    def test_chaining_middlewares(self):
        self.client.enable(Timer)
        self.client.enable(JsonOrder)

        responses.add(responses.GET,
                      'http://test.api.org/test-requires/1.json',
                      body='{"test": "good"}', status=200,
                      content_type='application/json')

        response = self.client.test_requires(format='json', id='1')

        self.assertEqual(response.order, ['JsonOrder', 'Timer'])

    @responses.activate
    def test_format_middleware(self):
        self.client.enable('Json')

        responses.add(responses.GET,
                      'http://test.api.org/test-requires/1.json',
                      body='{"test": "good"}', status=200,
                      content_type='application/json')

        response = self.client.test_requires(format='json', id='1')
        self.assertEqual(response.data, {'test': 'good'})

    @responses.activate
    def test_bad_status_code(self):
        responses.add(responses.GET,
                      'http://test.api.org/test-requires/2.json',
                      body='{"detail": "not found"}', status=404,
                      content_type='application/json')

        with self.assertRaises(britney.HTTPError):
            self.client.test_requires(format='json', id='2')
