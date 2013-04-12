# -*- coding: utf-8 -*-

"""
britney.middleware
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2013 by Arnaud Grausem
:license: BSD see LICENSE for details
"""

from functools import partial


class Middleware(object):
    """
    """

    def add_headers(self, environ, *headers):
        """
        """
        for header in headers:
            environ['spore.headers'].append(header)

    def __call__(self, environ):
        """
        """
        if hasattr(self, 'process_request'):
            environ.setdefault('spore.headers', [])
            self.process_request(environ)
        if hasattr(self, 'process_response'):
            callback = partial(self.process_response)
            return callback
