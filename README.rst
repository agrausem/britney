=======
Britney
=======

Britney is a module that implements the `SPORE specification`_. It is based on `Spyre`_.
This module requires a SPORE description of an API. Some descriptions for known services are available `here`_. You can write your own with `this guide`_.

.. _SPORE specification: https://github.com/SPORE/specifications/blob/master/spore_implementation.pod
.. _Spyre: https://github.com/bl0b/spyre
.. _here: https://github.com/spore/api-description
.. _this guide: https://github.com/SPORE/specifications/blob/master/spore_description.pod

.. image:: https://secure.travis-ci.org/agrausem/britney.png?branch=master
    :target: https://travis-ci.org/agrausem/britney

.. image:: https://coveralls.io/repos/agrausem/britney/badge.png?branch=master
    :target: https://coveralls.io/r/agrausem/britney?branch=master

.. image:: https://pypip.in/v/britney/badge.png
    :target: https://crate.io/packages/britney/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/britney/badge.png
    :target: https://crate.io/packages/britney/
    :alt: Number of PyPI downloads




Install
=======

Britney is working under Python 2.7 and Python >= 3.2. To install the module, you should use pip or easy_install : ::

    $> pip install britney

or ::

    $> easy_install britney


Create your client
==================

Basics
------

You must create your client with the **spyre** method that reads a json file containing the API description or an URI exposing the description. This can be done like that : ::

    import britney

    # from a description file
    client = britney.spyre('/path/to/api_desc.json')

    # from an URI
    client = britney.spyre('http://my-server/ws/api_desc.json')


The base URL
------------

If your API description file doesn't specify the base URL of the service, you can pass it to the **spyre** as the named argument **base_url** : ::

    import britney

    client = britney.spyre('/path/to/api_desc.json', base_url='http://my-server/ws/api/')

Middlewares
-----------

Sometimes, services need credentials to let you access the data or even send data. The client you created can enable middlewares at runtime and also extend his usage, by doing this : ::

    import britney
    from britney.middleware import auth
    
    client = britney.spyre('http://my-server/ws/api_desc.json')
    client.enable(auth.Basic, username='login', password='xxxxxx')

Sometimes, you want to enable middlewares on certain conditions. Another method called **enable_if** can take a callable predicate as argument that can check the environment parameters of the request : ::

    import britney
    from britney.middleware import auth 
    
    client = britney.spyre('http://my-server/ws/api_desc.json')
    client.enable_if(lambda request: request['payload'] != '', auth.Basic, username='login', password='xxxxxx')


Use your client
===============

Access data
-----------

Send data
---------

A full example
--------------

Create your own middleware
==========================

Basics
------

Creating and enabling middlewares let you control how request are send or response are received by adding authentification or formatting data. To create your middleware, you should :

  * inherit from ``britney.middleware.Middleware``
  * define how to instantiate your middleware
  * implement the process_request method to process the request
  * implement the process_response method to process the response

Here is a base class example to perform runtime on request : ::

    from britney.middleware import Middleware


    class Runtime(Middleware):

        def __init__(self, runtime_header):
            self.runtime_header  = runtime_header

        def process_request(self, environ):
            pass

        def process_response(self, response):
            pass


Processing request
------------------

With this method, you can access all of the keys and values of the request's base environment. By the way, you can add keys and values, change them or even delete them. Most of time, this method doesn't return data but if you return a requests.Response object, the process will stop and return this response. The result environment data will be used to build the request : :: 

    import datetime

    [...]

    def process_request(self, environ):
        self.start_time = datetime.datetime.now()
        environ[self.runtime_key] = 0

Processing response
-------------------

With this method, you can access data from the response, change or format content or even check headers or status : ::

    [...]

    def process_response(self, reponse):
        request_time = datetime.datetime.now() - self.start_time
        response.environ[self.runtime_key] = self.request_time.seconds

Use it
------

When you create your client, you only should enable your middleware and pass appopriate **named arguments** to the ``enable`` method : ::

    import britney
    from your_module.middleware import Runtime

    client = britney.spyre('http:://server.org/ws/api.json')
    client.enable(Runtime, runtime_key='X-Spore-Runtime')


That's all !


Test it
-------
A mock middleware and a function to fake ``Requests`` response are available to test the middlewares you created by faking a server. To test the Runtime middleware, you can do as follow : ::

    import datetime
    import unittest
    import britney
    from britney.middleware import utils
    from your_module.middleware import Runtime

    def test_response(request):
        return utils.fake_response(request, 'OK')

    class TestRuntime(unittest.TestCase):
        
        def setUp(self):
            self.fake_server = {'/test', test_response}
            self.client = britney.spyre('/path/to/api.json')
            self.runtime_key = 'X-Spore-Runtime'

        def test_runtime(self):
            self.client.enable(Runtime, runtime_header=self.runtime_header)
            self.client.enable(utils.Mock, fakes=self.fake_server, middlewares=self.client.middlewares)
            start = datetime.datetime.now()
            result = self.client.test()
            stop = datetime.datetime.now()

            self.assertIn(result.environ, self.runtime_key)
            self.assertAlmostEqual(result.environ[self.runtime_key], (stop - start).seconds)
