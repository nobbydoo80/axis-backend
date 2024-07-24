"""permissions.py: Django customer_neea"""

from axis.core.management.commands.set_permissions import AppPermission
from .models import ResoHome

__author__ = "Steven Klass"
__date__ = "4/6/16 12:57"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class ResoHomePermissions(AppPermission):
    models = [
        ResoHome,
    ]
