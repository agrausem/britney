# -*- coding: utf-8 -*-

"""
"""

import re
from requests import Request
from requests.compat import quote


class RequestBuilder(object):
    """
    """

    def __init__(self, env):
        self.env = env
        self.path_info = env['PATH_INFO']
        self.query_string = env.get('QUERY_STRING', '')

        # building path and query with params submitted
        for param, value in env['spore.params']:
            self.path_info, p_changed = re.subn(':%s' % param, value, 
                    self.path_info)
            self.query_string, q_changed = re.subn(':%s' % param, value,
                    self.query_string)
            if not p_changed and not q_changed:
                self.query_string += '&%s=%s' % (param, value)

        # correct query string
        if self.query_string.startswith('&'):
            self.query_string = self.query_string[1:]

    @property
    def application_uri(self):
        """
        """
        uri = self.env['wsgi.url_scheme'] + '://'

        if self.env.get('HTTP_HOST', ''):
            uri += self.env['HTTP_HOST']
        else:
            if self.env['spore.userinfo']:
                uri += self.env['spore.userinfo'] + '@'
            
            uri += self.env['SERVER_NAME']

            if self.env['wsgi.url_scheme'] == 'https':
                if self.env['SERVER_PORT'] != '443':
                    uri += ':' + self.env['SERVER_PORT']
            else:
                if self.env['SERVER_PORT'] != '80':
                    uri += ':' + self.env['SERVER_PORT']

        return uri + quote(self.env['SCRIPT_NAME'] or '/')
    
    @property
    def uri(self):
        """
        """
        uri = self.application_uri

        path_info = quote(self.path_info, safe='/=;,')
        if not self.env['SCRIPT_NAME']:
            uri += path_info[1:]
        else:
            uri += path_info

        if self.query_string:
            uri += '?' + quote(self.query_string, safe='&=;,')

        return uri

    def headers(self):
        """
        """
        return dict(self.env.get('spore.headers', ()))

    def data(self):
        """
        """
        return self.env['spore.payload'] or {}


    def __call__(self):
        """
        """
        request = Request(
                method=self.env['REQUEST_METHOD'],
                url=self.uri,
                data=self.data(),
                headers=self.headers()
        )
        return request.prepare()
