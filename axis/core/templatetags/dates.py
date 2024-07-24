"""dates.py: Django core.templatetags"""


import logging

__author__ = "Steven Klass"
__date__ = "9/23/13 10:58 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

from django import template
import datetime

register = template.Library()


def convert_timestamp(timestamp):
    try:
        ts = float(timestamp)
    except ValueError:
        return None
    return datetime.datetime.fromtimestamp(ts)


register.filter(convert_timestamp)


def truncate_timestamp(timestamp):
    try:
        ts = float(timestamp)
    except ValueError:
        return None
    return datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S.%f")[:11]


register.filter(truncate_timestamp)
