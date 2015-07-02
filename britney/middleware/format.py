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

    content_type = ''
    accept = ''

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

    def content_length(self, content):
        """
        :param content:
        :return: content length header information
        """
        return len(content)

    def process_request(self, environ):
        base.add_header(environ, 'Accept', self.accept)
        if environ['spore.payload'] and not environ['spore.payload_format']:
            self.process_payload(environ)

    def process_payload(self, environ):
        """
        """
        payload = self.dump(environ['spore.payload'])
        environ['spore.payload'] = payload
        base.add_header(environ, 'Content-Length', self.content_length(payload))
        base.add_header(environ, 'Content-Type', self.content_type)

    def process_response(self, response):
        response.data = self.load(response.text) if response.text else {}
        return response

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

    content_type = 'application/json'
    accept = 'application/json'

    def dump(self, data):
        return json.dumps(data)

    def load(self, data):
        return json.loads(data)
