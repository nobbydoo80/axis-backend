"""permissions.py: Django customer_aps"""

from axis.core.management.commands.set_permissions import AppPermission
from .models import APSHome, LegacyAPSBuilder, LegacyAPSHome, LegacyAPSSubdivision

__author__ = "Steven Klass"
__date__ = "4/5/16 16:30"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class CustomerAPSPermissions(AppPermission):
    models = [
        APSHome,
    ]
    default_abilities = []
    default_admin_abilities = []

    def get_aps_permissions(self):
        return ["view", "add", "change", "delete"]


class CustomerLegacyAPSPermissions(AppPermission):
    models = [LegacyAPSBuilder, LegacyAPSHome, LegacyAPSSubdivision]
    default_abilities = []
    default_admin_abilities = []

    def get_aps_permissions(self):
        return ["view", "add", "change", "delete"]
