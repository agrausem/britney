# -*- coding: utf-8 -*-

"""
britney
~~~~~~~

The Python implementation of SPORE (Specifications to a POrtable Rest
Environment)

This project is based on spyre
"""

import requests
from .core import Spore


def spyre(spec_uri, base_url=None):
    """
    """
    if spec_uri.startswith('http'):
        func = _new_from_url
    else:
        func = _new_from_file

    api_description = func(spec_uri)
    api_description.update({'base_url': base_url})

    return Spore(**api_description)

def _new_from_file(spec_uri):
    """
    """
    import json

    with open(spec_uri, 'r') as spec_file:
        spec = json.loads(spec_file.read())

    return spec


def _new_from_url(spec_uri):
    """
    """
    response = requests.get(spec_uri)
    return response.json()
