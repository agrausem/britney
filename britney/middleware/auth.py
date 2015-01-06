# -*- coding: utf-8 -*-

"""
britney.middleware.auth
~~~~~~~~~~~~~~~~~~~~~~~

"""

__all__ = ['Basic', 'ApiKey']


import base64
from . import base


def _basic_auth(username, password):
    """
    """
    return 'Basic ' + base64.b64encode(
        ('%s:%s' % (username, password)).encode('latin1')
    ).strip().decode('latin1')


class Auth(base.Middleware):
    """
    """

    def needs_auth(self, environ):
        return environ['spore.authentication']

    def __call__(self, environ):
        """
        """
        if self.needs_auth(environ):
            return super(Auth, self).__call__(environ)


class Basic(Auth):
    """
    """

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def process_request(self, environ):
        """
        """
        base.add_header(environ, 'Authorization',
                        _basic_auth(self.username, self.password))


class ApiKey(Auth):
    """
    """

    def __init__(self, key_name, key_value, **kwargs):
        self.key = key_name
        if callable(key_value):
            self.value = key_value(**kwargs)
        else:
            self.value = key_value

    def process_request(self, environ):
        """
        """
        base.add_header(environ, self.key, self.value)