# -*- coding: utf-8 -*-

"""
britney.middleware.format
~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2013 - Arnaud Grausem
:licence: BSD see LICENSE for details
"""

import abc
import json

from . import Middleware


class Format(Middleware):
    """
    """

    __metaclass__ = abc.ABCMeta


    @abc.abstractmethod
    def dump(self):
        """
        """
        pass

    @abc.abstractmethod
    def load(self):
        """
        """
        pass
    
    @abc.abstractproperty
    def accept_type(self):
        """
        """
        pass

    @abc.abstractproperty
    def content_type(self):
        """
        """
        pass

    def process_request(self, environ):
        headers = [self.accept_type]
        if environ['spore.payload']:
            environ['spore.payload'] = self.dump(environ['spore.payload'])
            headers.append(self.content_type)
        self.add_headers(environ, *headers)

    def process_response(self, response):
        response.data = response.json()


class Json(Format):
    """
    """

    def dump(self, data):
        return json.dumps(data)

    def load(self, data):
        return json.loads(data)

    @property
    def content_type(self):
        return ('Content-Type', 'application/json')

    @property
    def accept_type(self):
        return ('Accept', 'application/json')
