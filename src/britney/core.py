# -*- coding: utf-8 -*-

"""
britney.core
~~~~~~~~~~~~

Core objects that builds the whole SPORE client, based on informations defined
in a SPORE description. See https://github.com/SPORE/specifications/blob/master/spore_description.pod for
more informations about SPORE descriptions
"""


from requests.compat import urlparse
from requests.compat import is_py2

from .errors import SporeMethodBuildError
from .errors import SporeMethodCallError
from .errors import SporeClientBuildError


class Spore(object):
    """ Base class generating at run-time the Spore HTTP Client to a REST
    Environnment.

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
    :param meta: meta informations about the description and the service
    """

    def __new__(cls, *args, **kwargs):
        errors = {}

        if not kwargs.get('name', ''):
            errors['name'] = 'A name for this client is required'

        if not kwargs.get('methods', {}):
            errors['methods'] = 'One method is required to create the client'

        if not kwargs.get('base_url', ''):
            errors['base_url'] = 'A base URL to the REST Web Service is '
            'required'

        setattr(cls, 'middlewares', [])

        method_errors = {}
        for method_name, method_description in kwargs['methods'].items():
            try:
                method = SporeMethod(
                    method_name, 
                    base_url=kwargs['base_url'],
                    middlewares=cls.middlewares,
                    global_authentication=kwargs.get('authentication', None),
                    global_formats=kwargs.get('formats', None),
                    **method_description
                )
            except SporeMethodBuildError as method_error:
                method_errors[method_name] = method_error
            else:
                setattr(cls, method_name, method)
            
        if errors or method_errors:
            raise SporeClientBuildError(errors, method_errors)

        return super(Spore, cls).__new__(cls, *args, **kwargs)

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
        """
        if not callable(middleware):
            raise ValueError(middleware)

        self.middlewares.append((predicate, middleware(**kwargs)))


class SporeMethod(object):
    """ A method that handles request and response on the REST Web Service.

    :param name: name of the method (required)
    :param api_base_url: the base url for the REST Web Service (required)
    :param method: the http method to use (eg: 'GET', 'POST', etc) (required)
    :param path: the path to the wanted resource (eg: '/api/users') (required)
    :param required_params: a list parameters that will be used to build the
    url path (defaults to None)
    :param optional_params: a list of parameters that wille be used to build
    the request query
    :param expected_status: a list of expected status for the reponse (defaults
    to None).
    :param description: a short description for the method (defaults to '')
    :param middlewares: a list of the middlewares that will be applied to the
    request and the reponse. See :py:class:~`britney.middleware.BaseMiddleware`
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
        errors = {}

        if not kwargs.get('method', ''):
            errors['method'] = 'A method description should define the HTTP '
            'Method to use'

        if not kwargs.get('path', ''):
            errors['path'] = 'A method description should define the path to '
            'the wanted resource(s)'

        if not kwargs.get('name', ''):
            errors['name'] = 'A method description should define a name'

        if not kwargs.get('api_base_url', '') \
                and not kwargs.get('base_url', ''):
            errors['base_url'] = 'A method description should define a base '
            'url if not defined for the whle client'

        if errors:
            raise SporeMethodBuildError(errors)
        
        documentation = kwargs.get('documentation', '')
        description = kwargs.get('description', '')

        setattr(cls, __doc__, documentation if documentation else description)

        return super(SporeMethod, cls).__new__(cls, *args, **kwargs)

    def __init__(self, name='', api_base_url='', method='', path='', 
            required_params=None, optional_params=None, expected_status=None,
            description='', authentication=None, formats=None, base_url='',
            documentation='', middlewares=None, global_authentication=None,
            global_formats=None):

        self.name = name
        self.method = method
        self.path = path
        self.description = description
        self.required_payload = False

        self.base_url = base_url if base_url else api_base_url
        self.formats = formats if formats else global_formats

        self.required_params = required_params if required_params else []
        self.optional_params = optional_params if optional_params else []
        self.middlewares = middlewares if middlewares else []
        self.expected_status = expected_status if expected_status else []

        self.headers = []

        if authentication is None:
            self.authentication = global_authentication \
                if global_authentication is not None else False
        else:
            self.authentication = authentication

        self.parsed_url = urlparse(self.base_url)

    def __repr__(self):
        return '<SporeMethod [{}]>'.format(self.name)

    def base_environ(self):
        """ Builds the base environment dictionnary describing the request to
        be sent to the REST Web Service. See https://github.com/SPORE/specifications/blob/master/spore_implementation.pod
        for more informations about the keys defined here. You can also check
        the WSGI environnment keys http://wsgi.readthedocs.org/en/latest/definitions.html
        """


        def script_name(path):
            return path.rstrip('/')


        def userinfo(parsed_url):
            if parsed_url.username is None:
                return ''
            return '{0.username}:{0.password}'.format(parsed_url)


        def server_port(parsed_url):
            if parsed_url.scheme == 'http':
                return '80'
            elif parsed_url.scheme == 'https':
                return '443'
            return parsed_url.port


        return {
            'REQUEST_METHOD': self.method,
            'SERVER_NAME': self.parsed_url.hostname,
            'SERVER_PORT': server_port(self.parsed_url), 
            'SCRIPT_NAME': script_name(self.parsed_url.path),
            'PATH_INFO': self.path,
            'QUERY_STRING': '',
            'HTTP_USER_AGENT': 'britney',
            'spore.expected_status': self.expected_status,
            'spore.authentication': self.authentication,
            'spore.params': '',
            'spore.payload': '',
            'spore.errors': '',
            'spore.url_scheme': self.parsed_url.scheme,
            'spore.userinfo': userinfo(self.parsed_url),
            'spore.format': self.formats
        }

    def __call__(self, **kwargs):
        """ Calls the method with required parameters
        """

        def build_payload(self, **kwargs):
            """
            """
            payload = kwargs.pop('payload', None)

            if payload is None and self.required_payload:
                raise SporeMethodCallError('Payload is required for this '
                        'function')

            if payload and self.method in self.PAYLOAD_HTTP_METHODS:
                raise SporeMethodCallError(
                    'Payload requires one of these HTTP Methods: {}'.format(
                        ', '.join(self.PAYLOAD_HTTP_METHODS))
                )

            return payload

        def build_params(self, **kwargs):
            """ Check aguments passed to call method and build the spore
            parameters value
            """

            req_params = frozenset(self.required_params)
            all_params = req_params | frozenset(self.optional_params)
            passed_args = is_py2 and kwargs.viewkeys() or kwargs.keys()

            # nothing to do here
            if not all_params and not passed_args:
                return []

            # some required parameters are missing
            if not req_params.issubset(passed_args):
                raise SporeMethodCallError('Required parameters are missing', 
                        expected=req_params - all_params)
            
            # too much arguments passed to func
            if (passed_args - all_params):
                raise SporeMethodCallError('Too much parameter',
                        expected=passed_args - all_params)
            
            return list(is_py2 and kwargs.viewitems() or kwargs.items())
            

        environ = self.base_environ()
        environ.update({
            'spore.payload': build_payload(self, **kwargs),
            'spore.params': build_params(self, **kwargs)
        })
