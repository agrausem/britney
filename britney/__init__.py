# -*- coding: utf-8 -*-

"""
britney
~~~~~~~

The Python implementation of SPORE (Specifications to a POrtable Rest
Environment)

This project is based on spyre
"""

import urllib
import json
from .errors import SporeMethodStatusError as HTTPError


def new(spec_uri, base_url=None):
    """
    """
    from .core import Spore

    if spec_uri.startswith('http'):
        func = _new_from_url
    else:
        func = _new_from_file

    api_description = func(spec_uri)
    if base_url is not None:
        api_description.update({'base_url': base_url})

    return Spore(**api_description)


def _new_from_file(spec_uri):
    """
    """
    with open(spec_uri, 'r') as spec_file:
        spec = json.loads(spec_file.read())

    return spec


def _new_from_url(spec_uri):
    """
    """
    try:
        response = urllib.urlopen(spec_uri)
    except AttributeError:
        response = urllib.request.urlopen(spec_uri)
    return json.loads(response.read())


spyre = new