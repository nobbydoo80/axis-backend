"""permissions.py: Django scheduling"""

from axis.core.management.commands.set_permissions import AppPermission
from axis.scheduling.models import ConstructionStage, ConstructionStatus, TaskType, Task

__author__ = "Steven Klass"
__date__ = "2/1/13 6:40 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class SchedulingPermissions(AppPermission):
    models = [ConstructionStage, ConstructionStatus, TaskType, Task]

    def get_provider_home_innovation_research_labs_permissions(self):
        return [], []

    def get_sponsored_provider_home_innovation_research_labs_rater_permissions(self):
        return [], []

    def get_sponsored_provider_home_innovation_research_labs_builder_permissions(self):
        return [], []
