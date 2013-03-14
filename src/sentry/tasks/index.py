"""
sentry.tasks.index
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2013 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from celery.task import task
from collections import defaultdict

# TODO: ensure upgrade creates search schemas
# TODO: optimize group indexing so it only happens when a group is updated
# TODO: only index an event after a group is indexed??
# TODO: confirm replication=async is a good idea
# TODO: determine TTL


def schema_for_event():
    return {
        'group': {
            '_parent': {
                'type': 'group',
            }
        }
    }


def schema_for_group():
    return {
    }


def document_for_group(group):
    doc = {
        'datetime': group.last_seen,
        'project': group.project.id,
        'team': group.team.id,
    }

    return doc


def document_for_event(event):
    doc = defaultdict(list)
    for interface in event.interfaces.itervalues():
        for k, v in interface.get_search_context(event).iteritems():
            doc[k].extend(v)

    doc['text'].extend([
        event.message,
        event.logger,
        event.server_name,
        event.culprit,
    ])

    doc.update({
        'datetime': event.datetime,
        'project': event.project.id,
        'team': event.team.id,
    })

    return doc


@task(ignore_result=True)
def index_event(event, **kwargs):
    from sentry.app import app

    group = event.group

    app.search.index(
        index='sentry',
        doc_type='group',
        doc=document_for_group(group),
        id=group.id,
        replication='async',
    )
    app.search.index(
        index='sentry',
        doc_type='event',
        doc=document_for_event(event),
        id=event.id,
        parent=group.id,
        replication='async',
    )
