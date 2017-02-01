"""
britney.utils
~~~~~~~~~~~~~

"""
from sys import version
import datetime
import time
import wsgiref.handlers


VERSION = '0.5.1'


def get_user_agent():
    py_version = version.partition(' ')[0]
    return 'Britney/%s Python/%s SPORE/1.0' % (VERSION, py_version)

def get_http_date():
    now = datetime.datetime.now()
    stamp = time.mktime(now.timetuple())
    return wsgiref.handlers.format_date_time(stamp)
