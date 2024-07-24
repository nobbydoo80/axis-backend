"""numbers.py: Django core"""


import logging

__author__ = "Steven Klass"
__date__ = "10/11/13 8:09 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

from django import template

register = template.Library()


@register.filter
def percentage(value, precision=2):
    """
    Returns Percentage representation of number types.
    Takes an optional integer argument for decimal point accuracy.
    Upon failure returns value.
    """
    try:
        precision = int(precision)
        value = float(value)
    except (TypeError, ValueError):
        return value
    places = ":.{precision}%".format(precision=precision)
    perc_holder = "{" + places + "}"
    return perc_holder.format(value)
