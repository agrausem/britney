# -*- coding: utf-8 -*-

"""
britney.middleware.format
~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2013 - Arnaud Grausem
:licence: BSD see LICENSE for details
"""

__all__ = ['Json']


import abc
import json

from . import base


class Format(base.Middleware):
    """
    """

    __metaclass__ = abc.ABCMeta


    @abc.abstractmethod
    def dump(self, data):
        """
        """
        pass

    @abc.abstractmethod
    def load(self, data):
        """
        """
        pass
    
    @abc.abstractproperty
    def accept(self):
        """
        """
        pass

    @abc.abstractproperty
    def content_type(self):
        """
        """
        pass

    def content_length(self, content):
        """
        :param content:
        :return: content length header information
        """
        return 'Content-Length', len(content)


    def process_request(self, environ):
        base.add_header(environ, *self.accept)
        if environ['spore.payload']:
            payload = self.dump(environ['spore.payload'])
            environ['spore.payload'] = payload
            base.add_header(environ, *self.content_length(payload))
            base.add_header(environ, *self.content_type)

    def process_response(self, response):
        response.data = self.load(response.text)


class Json(Format):
    """
    """

    def dump(self, data):
        return json.dumps(data)

    def load(self, data):
        return json.loads(data)

    @property
    def content_type(self):
        return 'Content-Type', 'application/json'

    @property
    def accept(self):
        return 'Accept', 'application/json'