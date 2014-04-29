# -*- coding: utf-8 -*-

"""
britney.middleware.base
~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2013 by Arnaud Grausem
:license: BSD see LICENSE for details
"""

from functools import partial


class Middleware(object):
    """
    """

    def __call__(self, environ):
        """
        Launch actions on the future request and get callback to call hook to
        response
        :param environ: the environment of the request
        """
        if hasattr(self, 'process_request'):
            environ.setdefault('spore.headers', {})
            response = self.process_request(environ)
            if response is not None:
                return response
        if hasattr(self, 'process_response'):
            callback = partial(self.process_response)
            return callback


def add_header(environ, header_name, header_value):
    """
    Used to add a header to the environment of the request
    :param environ: the request environment
    :param header_name: name of the header to add
    :param header_value: value of the header
    """
    environ.get('spore.headers')[header_name] = header_value