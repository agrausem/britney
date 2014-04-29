# -*- coding: utf-8 -*-

"""
britney.middleware
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2013 by Arnaud Grausem
:license: BSD see LICENSE for details
"""

from .auth import *
from .format import *

from pkg_resources import iter_entry_points

for entry_point in iter_entry_points('britney.plugins.middleware'):
    try:
        locals()[entry_point.name] = entry_point.load()
    except ImportError:
        pass
