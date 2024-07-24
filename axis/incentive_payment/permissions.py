"""permissions.py: Django incentive_payment"""

from axis.core.management.commands.set_permissions import AppPermission
from .models import IPPItem, IncentivePaymentStatus, IncentiveDistribution

__author__ = "Steven Klass"
__date__ = "2/1/13 6:23 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class IncentivePaymentPermissions(AppPermission):
    default_abilities = []
    default_admin_abilities = []
    models = [IPPItem, IncentivePaymentStatus, IncentiveDistribution]

    def get_aps_permissions(self):
        return ["view", "add", "change", "delete"], ["view"]

    def get_sponsored_aps_builder_permissions(self):
        return ["view"], []

    def get_sponsored_aps_provider_permissions(self):
        return ["view"], []

    def get_sponsored_aps_rater_permissions(self):
        return ["view"], []

    def get_sponsored_eto_permissions(self):
        return ["view"], []

    def get_sponsored_eto_builder_permissions(self):
        return ["view"], []

    def get_sponsored_eto_provider_permissions(self):
        return ["view"], []

    def get_sponsored_eto_rater_permissions(self):
        return ["view"], []

    def get_sponsored_neea_utility_permissions(self):
        return ["view", "change", "delete"], [
            "view",
        ]
