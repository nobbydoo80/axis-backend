import os.path

from django import template

__author__ = "Steven Klass"
__date__ = "1/20/12 1:28 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

register = template.Library()


@register.filter
def filefieldname(field):
    """Retrieves the ``os.path.basename`` version of the field's current path."""
    if field and hasattr(field, "name"):
        return os.path.basename(field.name)
    return ""
