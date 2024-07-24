"""permissions.py: Django ekotrope"""


import logging

from axis.core.management.commands.set_permissions import AppPermission
from axis.ekotrope.models import Project, HousePlan, Analysis

__author__ = "Steven Klass"
__date__ = "1/9/17 14:15"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class EkotropePermissions(AppPermission):
    models = [Project, HousePlan, Analysis]

    def get_provider_permissions(self):
        return ["view", "change", "delete"], ["view"]

    def get_rater_permissions(self):
        return ["view", "change", "delete"], ["view"]

    def get_trc_permissions(self):
        return [], []

    def get_provider_home_innovation_research_labs_permissions(self):
        return [], []

    def get_sponsored_provider_home_innovation_research_labs_permissions(self):
        return [], []
