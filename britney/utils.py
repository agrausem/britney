"""
britney.utils
~~~~~~~~~~~~~

"""
from sys import version


VERSION = '0.3.2'


def get_user_agent():
    py_version = version.partition(' ')[0]
    return 'Britney/%s Python/%s SPORE/1.0' % (VERSION, py_version)