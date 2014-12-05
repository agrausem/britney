# -*- coding: utf-8 -*-

"""
britney.middleware.utils
~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2013 by Arnaud Grausem
:license: BSD see LICENSE for details
"""

import requests
from requests_testadapter import TestAdapter
from six import b
from . import base
from ..request import RequestBuilder


def fake_response(request, content, status_code=200, headers=None):
    """ For test purposes, this function can build fake response with customize
    attribute values
    :param request:  the prepared request to send
    :type request:  ~requests.PreparedRequest
    :param content: the content of the response
    :type content: string
    :param status_code: the status of the response. Defaults to 200
    :type status_code: integer
    :param headers: the headers to set
    :type headers: a dictionnary
    :return: a fake response
    :rtype: ~requests.Response
    """
    session = requests.session()
    session.mount('http://', TestAdapter(b(content), status=status_code,
        headers=headers))
    method = getattr(session, request.method.lower())
    return method(request.url)
    

class Mock(base.Middleware):
    """ This middleware can add the ability to fake a server that exposes an
    API.

    .. py:attribute:: fakes

        fakes should be a dict. Keys are pathes and values associated are
        callables that takes a request as argument and returns a response
        object

    Here is an example to use it : ::

        from requests import Response
        import britney
        from britney.middleware import utils

        def expected_response(request):
            return utils.fake_response(request, 'OK', status_code=200,
            headers={'Content-Type': 'text-plain'})

        client = britney.spyre('/path/to/spec.json')
        client.enable(utils.Mock, fakes={'/test': expected_response})

        result = client.test()

        assert(result.text == 'OK')
        assert(result.status_code == 200)
        assert('Content-Type' in result.headers)
    """

    def __init__(self, fakes, middlewares=None):
        self.fakes = fakes
        self.middlewares = middlewares or []

    def process_request(self, environ):
        finalized_request = RequestBuilder(environ)
        for path, func in self.fakes.items():
            if path == finalized_request.path_info:
                response = func(finalized_request())
                response.environ = environ
                return self.mock_process_response(response)

    def mock_process_response(self, response):
        if self.middlewares:
            for predicate, middleware in self.middlewares:
                if hasattr(middleware, 'process_response') and \
                        predicate(response.environ):
                    middleware.process_response(response)
        return response
