"""permissions.py: Django subdivision"""

from axis.core.management.commands.set_permissions import AppPermission
from .models import Subdivision

__author__ = "Steven Klass"
__date__ = "2/1/13 6:42 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class SubdivisionPermissions(AppPermission):
    models = [
        Subdivision,
    ]

    def get_trc_permissions(self):
        return [], []

    def get_provider_home_innovation_research_labs_permissions(self):
        return self.default_abilities

    def get_sponsored_provider_home_innovation_research_labs_permissions(self):
        return self.default_abilities
