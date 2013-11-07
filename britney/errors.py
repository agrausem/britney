# -*- coding: utf-8 -*-

"""
britney.errors
~~~~~~~~~~~~~~

Core errors made by britney
"""


class SporeClientBuildError(Exception):

    def __init__(self, client_errors, method_errors, *args, **kwargs):
        super(SporeClientBuildError, self).__init__(*args, **kwargs)
        self.errors = client_errors
        if method_errors:
            self.errors['methods'] = method_errors
        
        
class SporeMethodBuildError(Exception):

    def __init__(self, errors, *args, **kwargs):
        super(SporeMethodBuildError, self).__init__(*args, **kwargs)
        self.errors = errors


class SporeMethodCallError(Exception):

    def __init__(self, cause, *args, **kwargs):
        self.expected_values = kwargs.pop('expected', [])
        super(SporeMethodCallError, self).__init__(*args, **kwargs)
        self.cause  = cause

class SporeMethodStatusError(Exception):
    """
    """
    pass
