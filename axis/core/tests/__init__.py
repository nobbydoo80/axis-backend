"""__init__.py: Django core.tests package container"""


__author__ = "Steven Klass"
__date__ = "04/17/13 5:00 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]
__license__ = "See the file LICENSE.txt for licensing information."


def pop_kwargs(prefix, kwargs):
    """In place pop and split out kwargs"""
    data = dict()
    for k, v in list(kwargs.items()):
        if k.startswith(prefix):
            data[k.replace(prefix, "")] = kwargs.pop(k)
    return data
