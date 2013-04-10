# -*- coding: utf-8 -*-

"""
"""

import re
from requests.compat import urlunparse


class RequestBuilder(object):
    """
    """

    def __init__(self, env):
        self.env = env
        self.__query = []
        print self.env


    @property
    def scheme(self):
        return self.env['spore.url_scheme']

    @property
    def userinfo(self):
        return self.env.get('spore.userinfo', '')

    @property
    def netloc(self):
        """
        """
        if self.env.get('HTTP_HOST', ''):
            netloc = self.env['HTTP_HOST']
        else:
            netloc = ''

            if self.userinfo:
                netloc += '{}@'.format(self.userinfo)
            
            netloc += self.env['SERVER_NAME']

            if self.scheme == 'https':
                if self.env['SERVER_PORT'] != '443':
                    netloc += ':{0[SERVER_PORT]}'.format(self.env)
            else:
                if self.env['SERVER_PORT'] != '80':
                    netloc += ':{0[SERVER_PORT]}'.format(self.env)
        return netloc

    @property
    def path(self):
        """
        """
        params = self.env['spore.params']
        path_info = self.env['PATH_INFO']

        for parameter, value in params:
            path_info, changed = re.subn(r':%s' % parameter, value, path_info)
            if changed:
                continue
            self.__query.append((parameter, value))
        return self.env['SCRIPT_NAME'] + path_info
    
    @property
    def query(self):
        """
        """
        params = self.env['spore.params']
        query_string = self.env['QUERY_STRING']

        if not self.__query:
            path = self.path

        for parameter, value in params:
            query_string, changed = re.subn(r':%s' % parameter, value,
                    query_string)
            if changed and (parameter, value) in self.__query:
                self.__query.remove((parameter, value))

        if query_string and self.__query:
            query_string += '&'

        query_string += '&'.join('{0[0]}={0[1]}'.format(item) for item in
                self.__query)

        return query_string

    def get_url(self):
        """
        """
        return urlunparse((self.scheme, self.netloc, self.path, '', self.query,
            ''))
