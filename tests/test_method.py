# -*- coding: utf-8 -*-

from functools import partial
import unittest
from britney.core import SporeMethod, Spore
from britney import errors
from britney.middleware.utils import Mock, fake_response


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
        self.assertTrue(2 in values)
        self.assertTrue(3 in values)
        self.assertTrue('json' in values)


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
        self.assertTrue('base_url' in error.errors)


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


class TestMethodBuilder(unittest.TestCase):
    """ Test method generation, errors catched in REST description and
    representation
    """

    def test_missing_required_in_desc(self):
        with self.assertRaises(errors.SporeMethodBuildError) as build_error:
            SporeMethod(base_url='http://api.test.org')

        error = build_error.exception
        self.assertTrue('name' in error.errors)
        self.assertTrue('path' in  error.errors)
        self.assertTrue('method' in error.errors)

    def test_representation(self):
        method = SporeMethod(method='GET', path='/tests', name='test_method',
                base_url='http://api.test.org')
        self.assertEqual(repr(method), '<SporeMethod [test_method]>')


class TestMethodPayload(unittest.TestCase):
    """ Test payload generation and check for POST, PATCH and POST requests
    """

    def setUp(self):
        self.method = partial(SporeMethod, method='GET', name='test_method',
                path='/test', api_base_url='http://my_test.org') 

    def test_payload_error(self):
        method = self.method(required_payload=True)
        with self.assertRaises(errors.SporeMethodCallError) as call_error:
            method.build_payload(data=[])

        error = call_error.exception
        self.assertEqual(error.cause, 'Payload is required for this function')

    def test_payload(self):
        method = self.method(required_payload=True)
        payload = method.build_payload(data={'test': 'data'})
        self.assertEqual(payload, {'test': 'data'})


class TestMethodStatus(unittest.TestCase):
    """ Test checking expected http status from response
    """

    def setUp(self):
        self.build_response = lambda status: partial(fake_response,
                                                     content='fake_response',
                                                     status_code=status)
        self.client = Spore(name='my_client', base_url='http://my_url.org',
                methods={'my_method': {'method': 'GET', 'path': '/api'}})

    def tearDown(self):
        self.client.middlewares = []

    def test_ok_http_status(self):
        fakes = {}
        for status in (200, 220, 235, 298):
            fakes['/api'] = self.build_response(status)
            self.client.enable(Mock, fakes=fakes)
            result = self.client.my_method()
            self.assertIsNone(self.client.my_method.check_status(result))
            self.client.middlewares = []

    def test_not_ok_status_with_expected(self):
        self.client.my_method.expected_status = [302, 401, 403, 404, 502]
        fakes = {}
        for status in [302, 401, 403, 404, 502]:
            fakes['/api'] = self.build_response(status)
            self.client.enable(Mock, fakes=fakes)
            result = self.client.my_method()
            self.assertIsNone(self.client.my_method.check_status(result))
            self.client.middlewares = []

    def test_unexpected_status(self):
        with self.assertRaises(errors.SporeMethodStatusError) as status_error:
            fake_response_func = self.build_response(502)
            self.client.enable(Mock, fakes={'/api': fake_response_func})
            result = self.client.my_method()
            self.client.my_method.check_status(result)

        error = status_error.exception
        self.assertEqual(str(error), 'Error 502')
