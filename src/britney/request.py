# -*- coding: utf-8 -*-

"""
"""

from functools import partial
import re
from requests.compat import quote


class RequestBuilder(object):
    """
    """

    def __init__(self, env):
        self.env = env

    @property
    def base_url(self):
        """
        """
        url = '{0.env[spore.url_scheme]}://{0.netloc}'.format(self)
        return url + quote(self.env['SCRIPT_NAME'])

    @property
    def netloc(self):
        """
        """
        if self.env.get('HTTP_HOST', ''):
            netloc = self.env['HTTP_HOST']
        else:
            netloc = ''

            if self.env.get('spore.userinfo', ''):
                netloc += '{0[spore.userinfo]}@'.format(self.env)
            
            netloc += self.env['SERVER_NAME']

            if self.env['spore.url_scheme'] == 'https':
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
        query_string = self.env['QUERY_STRING']

        for parameter, value in params:
            p_keyword = re.compile(r':%s' % parameter)
            path_info, changed = quote(p_keyword.subn(value, path_info))
            if changed:
                continue
            else:
                query_string, changed = quote(p_keyword.subn(value, path_info))
                if not changed:
                    query_string += quote('&%s=%s') % (parameter, value)

        return path_info + '?' + query_string


    def get_url(self):
        """
        """
        return self.base_url + self.path
