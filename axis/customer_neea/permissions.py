"""permissions.py: Django customer_neea"""

from axis.core.management.commands.set_permissions import AppPermission
from .models import LegacyNEEAPartner, LegacyNEEAContact, LegacyNEEAHome, StandardProtocolCalculator

__author__ = "Steven Klass"
__date__ = "4/6/16 12:57"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class NEEAPermissions(AppPermission):
    models = [
        LegacyNEEAPartner,
        LegacyNEEAContact,
        LegacyNEEAHome,
    ]

    def get_neea_permissions(self):
        return ["view"]


class RTFCalculatorPermissions(AppPermission):
    models = [
        StandardProtocolCalculator,
    ]

    def get_neea_permissions(self):
        return ["view"]
