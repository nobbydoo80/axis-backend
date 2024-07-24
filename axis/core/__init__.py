"""__init__.py: Django core package container"""


from .git_utils import get_stored_version_info
from .messages import AxisSystemMessage  # Ensures that this module gets loaded

__author__ = "Steven Klass"
__version__ = "79.0.1"
__version_info__ = (79, 0, 1)
__date__ = "2011/06/27 10:46:00"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
    "Autumn Valenta",
    "Rajesh Pappula",
    "Mohammad Rafi",
    "Gaurav Kapoor",
    "Etienne Robillard",
    "Eric Walker",
    "Amit Kumar Pathak",
    "Michael Jeffrey",
]
__license__ = "See the file LICENSE.txt for licensing information."

# TODO FIX FOR DJANGO3
# https://github.com/chibisov/drf-extensions/issues/294
from django.db.models.sql import datastructures
from django.core.exceptions import EmptyResultSet

datastructures.EmptyResultSet = EmptyResultSet
