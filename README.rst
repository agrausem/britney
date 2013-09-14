=======
Britney
=======

Britney is a module that implements the `SPORE specification`_. It is based on Spyre.
This module requires a SPORE description of an API. Some descriptions for known services are available `here`_. You can write your own with `this guide`_.

.. _SPORE specification: https://github.com/SPORE/specifications/blob/master/spore_implementation.pod
.. _here: https://github.com/spore/api-description
.. _this guide: https://github.com/SPORE/specifications/blob/master/spore_description.pod

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
    client.enable(auth.Basic, 'login', 'xxxxxx')

Sometimes, you want to enable middlewares on certain conditions. Another method called **enable_if** can take a callable predicate as argument that can check the environment parameters of the request : ::

    import britney
    from britney.middleware import auth 
    
    client = britney.spyre('http://my-server/ws/api_desc.json')
    client.enable_if(lamba environ: environ['payload'] != '', auth.Basic, 'login', 'xxxxxx')


