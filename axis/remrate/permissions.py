"""permissions.py: Django remrate"""

from axis.core.management.commands.set_permissions import AppPermission
from .models import RemRateUser

__author__ = "Steven Klass"
__date__ = "2/1/13 6:31 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class RemRateUserPermissions(AppPermission):
    models = [
        RemRateUser,
    ]

    def get_trc_permissions(self):
        return [], []
