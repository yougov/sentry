"""
sentry.app
~~~~~~~~~~

:copyright: (c) 2010-2013 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from sentry.conf import settings
from sentry.utils.imports import import_string
from threading import local
from pyelasticsearch import ElasticSearch


class State(local):
    request = None
    data = {}


def get_instance(path, options):
    cls = import_string(path)
    if cls is None:
        raise ImportError('Unable to find module %s' % path)
    return cls(**options)


def get_search(options):
    return ElasticSearch(**options)

env = State()
buffer = get_instance(settings.BUFFER, settings.BUFFER_OPTIONS)
if settings.USE_SEARCH:
    search = get_search(settings.SEARCH_OPTIONS)
else:
    search = None
