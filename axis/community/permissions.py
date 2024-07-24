"""permissions.py: Django community"""


import logging

from axis.core.management.commands.set_permissions import AppPermission
from .models import Community

__author__ = "Steven Klass"
__date__ = "2/1/13 4:33 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CommunityPermissions(AppPermission):
    models = [
        Community,
    ]

    def get_trc_permissions(self):
        return [], []

    def get_sponsored_provider_home_innovation_research_labs_permissions(self):
        return [
            "view",
        ]

    def get_provider_home_innovation_research_labs_permissions(self):
        return [
            "view",
        ]
