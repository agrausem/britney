# -*- coding: utf-8 -*-

"""
britney.core
~~~~~~~~~~~~

Core objects that builds the whole SPORE client, based on information defined
in a SPORE description.
See https://github.com/SPORE/specifications/blob/master/spore_description.pod
for more information about SPORE descriptions
"""

from functools import reduce
import requests
from requests.compat import urlparse
import requests.models
import six

from . import errors
from .request import RequestBuilder
from .utils import get_user_agent


class Spore(object):
    """ Base class generating at run-time the Spore HTTP Client to a REST
    Environment.

    :param name: name of the REST Web Service (required)
    :param base_url: base url of the REST Web Service (required)
    :param authority: authority that maintains the SPORE description of the
    REST Web Service (defaults to '')
    :param formats: a list of accepted formats (eg: json, xml) (defaults to
    None
    :param authentication: boolean for a global authentication check (defaults
    to None)
    :param methods: a dict containing the methods information that will
    instantiate a :py:class:`~britney.core.SporeMethod` (required)
    :param meta: meta information about the description and the service
    """

    def __new__(cls, *args, **kwargs):
        spec_errors, method_errors = {}, {}

        if not kwargs.get('name', ''):
            spec_errors['name'] = 'A name for this client is required'

        if not kwargs.get('base_url', ''):
            spec_errors['base_url'] = 'A base URL to the REST Web Service is \
            required'

        if 'methods' not in kwargs:
            spec_errors['methods'] = 'One method is required to create the \
            client'
        else:
            authentication = kwargs.get('authentication', None)
            formats = kwargs.get('formats', None)
            middlewares_module = __import__('britney.middleware',
                                            fromlist=('middleware'))
            setattr(cls, '_middlewares_module', middlewares_module)

            instance = super(Spore, cls).__new__(cls)
            setattr(instance, 'middlewares', [])
            setattr(instance, 'defaults', {})

            for method_name, method_description in kwargs['methods'].items():
                try:
                    method = SporeMethod(
                        name=method_name,
                        base_url=kwargs['base_url'],
                        middlewares=instance.middlewares,
                        global_authentication=authentication,
                        global_formats=formats,
                        defaults=instance.defaults,
                        **method_description
                    )
                except errors.SporeMethodBuildError as method_error:
                    method_errors[method_name] = method_error
                else:
                    setattr(instance, method_name, method)

        if spec_errors or method_errors:
            raise errors.SporeClientBuildError(spec_errors,
                                               method_errors)

        return instance

    def __init__(self, name='', base_url='', authority='', formats=None,
                 version='', authentication=None, methods=None, meta=None):
        self.name = name
        self.authority = authority
        self.base_url = base_url
        self.version = version
        self.authentication = authentication

        self.formats = [] if formats is None else formats
        self.meta = {} if meta is None else meta

    def __repr__(self):
        return '<Spore [{}]>'.format(self.name)

    def enable(self, middleware, **kwargs):
        """ Enables a middleware on the client object

        :param middleware: a middleware class
        :param kwargs: parameters to instantiate the middleware
        """
        self.enable_if(lambda request: True, middleware, **kwargs)

    def enable_if(self, predicate, middleware, **kwargs):
        """ Enables a middleware on the client object only if the predicate is
        true

        :param predicate: a function that takes the request as argument and
        returns a boolean
        :param middleware: a middleware class
        :param kwargs: parameters to instantiate the middleware
        :raises: ValueError when the middleware is not a callable
        """
        if isinstance(middleware, (six.string_types, six.text_type)):
            try:
                middleware = getattr(self._middlewares_module, middleware)
            except AttributeError:
                raise AttributeError('Unknown middleware %s' % middleware)

        elif not callable(middleware):
            raise ValueError(middleware)

        self.middlewares.append((predicate, middleware(**kwargs)))

    def add_default(self, param, value):
        """
        """
        self.defaults[param] = value

    def remove_default(self, param):
        """
        """
        try:
            del self.defaults[param]
        except KeyError:
            pass


class SporeMethod(object):
    """ A method that handles request and response on the REST Web Service.

    :param name: name of the method (required)
    :param api_base_url: the base url for the REST Web Service (required)
    :param method: the http method to use (eg: 'GET', 'POST', etc) (required)
    :param path: the path to the wanted resource (eg: '/api/users') (required)
    :param required_params: a list parameters that will be used to build the
    url path (defaults to None)
    :param optional_params: a list of parameters that will be used to build
    the request query
    :param expected_status: a list of expected status for the response
    (defaults to None).
    :param description: a short description for the method (defaults to '')
    :param middlewares: a list of the middlewares that will be applied to the
    request and the response.
    See :py:class:~`britney.middleware.BaseMiddleware`
    :param authentication: boolean to set authentication on the method. This
    param replaces the global authentication parameter set for the whole client
    on this particular method (defaults to None)
    :param formats: a list of formats accepted by the REST Web Service for this
    method. This parameter replaces the global formats set whole client
    (defaults to None)
    :param base_url: a specific base url for this method. This parameter
    replaces the base api url set for the whole client (defaults to '')
    :param documentation: documentation for this method
    :param global_authentication: a boolean that enables authentication for the
    whole client
    :param global_formats: a list of formats accepted for the whole client.
    """

    PAYLOAD_HTTP_METHODS = ('POST', 'PUT', 'PATCH')
    HTTP_METHODS = PAYLOAD_HTTP_METHODS + ('GET', 'TRACE', 'OPTIONS', 'DELETE',
                                           'HEAD')

    def __new__(cls, *args, **kwargs):
        method_errors = {}

        if not kwargs.get('method', ''):
            method_errors['method'] = 'A method description should define the \
            HTTP Method to use'

        if not kwargs.get('path', ''):
            method_errors['path'] = 'A method description should define the \
            path to the wanted resource(s)'

        if not kwargs.get('name', ''):
            method_errors['name'] = 'A method description should define a name'

        if not kwargs.get('api_base_url', '') \
                and not kwargs.get('base_url', ''):
            method_errors['base_url'] = 'A method description should define a \
            base url if not defined for the whole client'

        if method_errors:
            raise errors.SporeMethodBuildError(method_errors)

        documentation = kwargs.get('documentation', '')
        description = kwargs.get('description', '')

        instance = super(SporeMethod, cls).__new__(cls)
        instance.__doc__ = documentation or description

        return instance

    def __init__(self, name='', api_base_url='', method='', path='',
                 required_params=None, optional_params=None,
                 expected_status=None, required_payload=False, description='',
                 authentication=None, formats=None, base_url='',
                 documentation='', middlewares=None,
                 global_authentication=None, global_formats=None,
                 defaults=None):

        self.name = name
        self.method = method
        self.path = path
        self.description = description
        self.required_payload = required_payload

        self.base_url = base_url if base_url else api_base_url
        self.formats = formats if formats else global_formats

        self.required_params = required_params if required_params else []
        self.optional_params = optional_params if optional_params else []
        self.middlewares = middlewares
        self.defaults = defaults
        self.expected_status = expected_status if expected_status else []

        self.headers = []

        if authentication is None:
            self.authentication = global_authentication \
                if global_authentication is not None else False
        else:
            self.authentication = authentication

    def __repr__(self):
        return '<SporeMethod [{}]>'.format(self.name)

    def base_environ(self):
        """ Builds the base environment dictionnary describing the request to
        be sent to the REST Web Service.
        """

        parsed_base_url = urlparse(self.base_url)

        def script_name(parsed_url):
            return parsed_url.path.rstrip('/')

        def userinfo(parsed_url):
            if parsed_url.username is None:
                return ''
            return '{0.username}:{0.password}'.format(parsed_url)

        def server_port(parsed_url):
            if not parsed_url.port:
                if parsed_url.scheme == 'http':
                    return 80
                elif parsed_url.scheme == 'https':
                    return 443
            return parsed_url.port

        path = self.path.split('?')
        if len(path) > 1:
            path_info, query_string = path
        else:
            path_info, query_string = path[0], ''

        return {
            'REQUEST_METHOD': self.method,
            'SERVER_NAME': parsed_base_url.hostname,
            'SERVER_PORT': server_port(parsed_base_url),
            'SCRIPT_NAME': script_name(parsed_base_url),
            'PATH_INFO': path_info,
            'QUERY_STRING': query_string,
            'HTTP_USER_AGENT': get_user_agent(),
            'spore.expected_status': self.expected_status,
            'spore.authentication': self.authentication,
            'spore.params': '',
            'spore.payload': '',
            'spore.payload_format': '',
            'spore.errors': '',
            'spore.headers': {},
            'spore.format': self.formats,
            'spore.userinfo': userinfo(parsed_base_url),
            'spore.method': self.name,
            'wsgi.url_scheme': parsed_base_url.scheme,
        }

    def is_a_param(self, param):
        return param in self.required_params or param in self.optional_params

    def get_defaults(self):
        if self.defaults:
            return {
                param: value for param, value in six.iteritems(self.defaults)
                if self.is_a_param(param)
            }
        return {}

    def build_payload(self, data, files):
        """
        """

        if not (data or files) and self.required_payload:
            raise errors.SporeMethodCallError('Payload is required for '
                                              'this function')

        return data

    def build_params(self, **kwargs):
        """ Check arguments passed to call method and build the spore
        parameters value
        """

        req_params = frozenset(self.required_params)
        all_params = req_params | frozenset(self.optional_params)
        passed_args = set(six.iterkeys(kwargs))
        if self.defaults:
            default_args = set(six.iterkeys(self.get_defaults()))
            all_args = set(passed_args).union(default_args)
        else:
            all_args = set(passed_args)

        # nothing to do here
        if not all_params and not all_args:
            return []

        # some required parameters are missing
        if not req_params.issubset(all_args):
            expected = req_params - passed_args
            raise errors.SporeMethodCallError(
                'Required parameters are missing', expected=expected
            )

        # too much arguments passed to func
        if all_args - all_params:
            expected = passed_args - all_params
            raise errors.SporeMethodCallError('Too much parameter',
                                              expected=expected)

        kwargs.update(**self.get_defaults())
        return list(six.iteritems(kwargs))

    def check_status(self, response):
        """ Checks response status in fact of the *expected_status*
        attribute

        :param response: the response from the REST service
        :type response: requests.Response
        :raises: ~britney.errors.SporeMethodStatusError
        """
        status = response.status_code
        if 200 <= status <= 299:
            return
        if status not in self.expected_status:
            raise errors.SporeMethodStatusError(response)

    def __call__(self, **kwargs):
        """ Calls the method with required parameters
        :raises: ~britney.errors.SporeMethodStatusError
        :raises: ~britney.errors.SporeMethodCallError
        """

        hooks = []
        data = kwargs.pop('payload', None)
        files = kwargs.pop('files', None)

        environ = self.base_environ()
        environ.update({
            'spore.payload': self.build_payload(data, files),
            'spore.params': self.build_params(**kwargs),
            'spore.files': files
        })

        for predicate, middleware in self.middlewares:
            if predicate(environ):
                callback = middleware(environ)
                if callback is not None:
                    if isinstance(callback, requests.models.Response):
                        return callback
                    hooks.append(callback)

        prepared_request = RequestBuilder(environ)

        with requests.session() as session:
            response = session.send(prepared_request(), verify=True)
            response.environ = environ

        self.check_status(response)

        res = reduce(lambda r, hook: hook(r), reversed(hooks), response)
        if res and isinstance(res, requests.models.Response):
            response = res

        return response
