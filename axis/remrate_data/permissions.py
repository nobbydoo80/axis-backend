"""permissions.py: Django remrate_data"""

__author__ = "Steven Klass"
__date__ = "3/8/13 2:41 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from axis.core.management.commands.set_permissions import AppPermission
from .models import Simulation, Building


class RemRateDataPermissions(AppPermission):
    models = [Simulation, Building]

    def get_provider_permissions(self):
        return ["view", "change", "delete"], self.default_abilities

    def get_rater_permissions(self):
        return ["view", "change", "delete"], self.default_abilities

    def get_provider_home_innovation_research_labs_permissions(self):
        return [], []

    def get_sponsored_provider_home_innovation_research_labs_permissions(self):
        return [], []
