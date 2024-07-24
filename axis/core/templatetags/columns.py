"""columns.py: Django eep.templatetags"""


import logging
from django import template
from itertools import cycle

__author__ = "Steven Klass"
__date__ = "1/21/12 5:57 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

register = template.Library()


@register.filter
def exact_columns(items, number_of_columns):
    """Divides a list in an exact number of columns.
    The number of columns is guaranteed.

    Examples:

        8x3:
        [[1, 2, 3], [4, 5, 6], [7, 8]]

        2x3:
        [[1], [2], []]
    """
    try:
        number_of_columns = int(number_of_columns)
        items = list(items)
    except (ValueError, TypeError):
        return [items]

    columns = [[] for x in range(number_of_columns)]
    actual_column = cycle(range(number_of_columns))
    for item in items:
        columns[actual_column.next()].append(item)

    return columns
