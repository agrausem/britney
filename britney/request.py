# -*- coding: utf-8 -*-

"""
"""

import re
from requests import Request
from requests.compat import quote
from .utils import get_http_date


class RequestBuilder(object):
    """
    """

    _OLD_PLACEHOLDER_P = re.compile(r':(\w+)')
    _PARAMS_P = re.compile(r'(?<={)\w+(?=})')

    def __init__(self, env):
        self.env = env
        self.param_names = []
        self.path_info = self._replace_params(env['PATH_INFO'])
        self.query_string = self._replace_params(env.get('QUERY_STRING', ''))

        # building query with optional params submitted
        for param, value in self.env['spore.params']:
            if param not in self.param_names:
                if isinstance(value, (list, tuple)):
                    value = '&'.join('%s=%s' % (param, mvalue)
                                     for mvalue in value)
                else:
                    value = '%s=%s' % (param, value)
                self.query_string += '&%s' % value

        self.query_string = self.query_string.lstrip('&')

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
                if self.env['SERVER_PORT'] != 443:
                    uri += ':%d' % self.env['SERVER_PORT']
            else:
                if self.env['SERVER_PORT'] != 80:
                    uri += ':%d' % self.env['SERVER_PORT']

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

    def _simple_params(self):
        return {
            key: value for key, value
            in self.env['spore.params']
            if not isinstance(value, (list, tuple))
        }

    def _replace_params(self, template):
        # dealing with first version of spec (placeholder => ':')
        template = self._OLD_PLACEHOLDER_P.sub(r'{\1}', template)

        self.param_names.extend(self._PARAMS_P.findall(template))
        return template.format(**self._simple_params())

    @property
    def headers(self):
        """
        """
        headers = {
            'Host': '{0[SERVER_NAME]}:{0[SERVER_PORT]}'.format(self.env),
            'User-Agent': self.env['HTTP_USER_AGENT'],
            'Date': get_http_date()
        }
        self.env['spore.headers'].update(headers)
        return self.env['spore.headers']

    @property
    def data(self):
        """
        """
        return self.env['spore.payload'] or {}

    @property
    def files(self):
        """
        """
        return self.env.get('spore.files', None)

    def __call__(self):
        """
        """
        request = Request(
            method=self.env['REQUEST_METHOD'],
            url=self.uri,
            data=self.data,
            files=self.files,
            headers=self.headers
        )
        return request.prepare()
