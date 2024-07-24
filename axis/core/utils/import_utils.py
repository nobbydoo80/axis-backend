"""import_utils.py - Axis"""

__author__ = "Steven K"
__date__ = "8/10/21 14:28"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import importlib
import logging
import sys

log = logging.getLogger(__name__)

# Shamelessly stole from Celery / Kombu
#
# NOTE:  These are located in the infrastructure package and will need to go there after the
#        next stack update!!
# TODO: Remove Me


def reraise(_tp, value, tb=None):
    """Reraise exception."""
    if value.__traceback__ is not tb:
        raise value.with_traceback(tb)
    raise value


def symbol_by_name(name, aliases=None, imp=None, package=None, sep=".", default=None, **kwargs):
    """Get symbol by qualified name.

    The name should be the full dot-separated path to the class::

        modulename.ClassName

    Example::

        celery.concurrency.processes.TaskPool
                                    ^- class name

    or using ':' to separate module and symbol::

        celery.concurrency.processes:TaskPool

    If `aliases` is provided, a dict containing short name/long name
    mappings, the name is looked up in the aliases first.

    """
    aliases = {} if not aliases else aliases
    if imp is None:
        imp = importlib.import_module

    if not isinstance(name, str):
        return name  # already a class

    name = aliases.get(name) or name
    sep = ":" if ":" in name else sep
    module_name, _, cls_name = name.rpartition(sep)
    if not module_name:
        cls_name, module_name = None, package if package else cls_name
    try:
        try:
            module = imp(module_name, package=package, **kwargs)
        except ValueError as exc:
            reraise(ValueError, ValueError(f"Couldn't import {name!r}: {exc}"), sys.exc_info()[2])
        return getattr(module, cls_name) if cls_name else module
    except (ImportError, AttributeError):
        if default is None:
            raise
    return default
