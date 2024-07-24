"""permissions.py: Django sampleset"""


from axis.core.management.commands.set_permissions import AppPermission
from .models import SampleSet, SampleSetHomeStatus, SamplingProviderApproval

__author__ = "Steven Klass"
__date__ = "9/4/14 9:55 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class SamplingPermissions(AppPermission):
    models = [SampleSet, SampleSetHomeStatus]

    def get_trc_permissions(self):
        return [], []

    def get_provider_home_innovation_research_labs_permissions(self):
        return [], []

    def get_sponsored_provider_home_innovation_research_labs_permissions(self):
        return [], []


class SamplingApprovalPermissions(AppPermission):
    models = [SamplingProviderApproval]

    def get_trc_permissions(self):
        return [], []

    def get_provider_home_innovation_research_labs_permissions(self):
        return [], []

    def get_sponsored_provider_home_innovation_research_labs_permissions(self):
        return [], []
