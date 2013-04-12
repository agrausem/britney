# -*- coding: utf-8 -*-

"""
britney.middleware.auth
~~~~~~~~~~~~~~~~~~~~~~~

"""

from base64 import b64encode
from functools import partial

from . import Middleware


def _basic_auth(username, password):
    """
    """
    return 'Basic ' + b64encode(
        ('%s:%s' % (username, password)).encode('latin1')
    ).strip().decode('latin1')


class Auth(Middleware):
    """
    """

    def needs_auth(self, environ):
        return environ['spore.authentication']

    def __call__(self, environ):
        """
        """
        if self.needs_auth(environ):
            super(Auth, self).__call__(environ)


class Basic(Auth):
    """
    """

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def process_request(self, environ):
        """
        """
        header = ('Authorization', _basic_auth(self.username, self.password))
        self.add_headers(environ, header)


class Proxy(Basic):
    """
    """
    
    def __init__(self, username, password):
        super(Proxy, self).__init__(username, password)


    def process_request(self, environ):
        """
        """
        header = ('Proxy-Authorization', _basic_auth(self.username,
            self.password))
        self.add_headers(environ, header)


class ApiKey(Auth):
    """
    """

    def __init__(self, key_name, key_value, *args):
        self.key = key_name
        if callable(key_value):
            self.value = key_value(*args)
        else:
            self.value = key_value

    def process_request(self, environ):
        """
        """
        header = (self.key, self.value)
        self.add_headers(environ, header)
