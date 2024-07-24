"""permissions.py: Django floorplan"""


import logging

from axis.core.management.commands.set_permissions import AppPermission
from .models import Floorplan

__author__ = "Steven Klass"
__date__ = "2/1/13 6:14 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class FloorplanPermissions(AppPermission):
    models = [Floorplan]

    default_abilities = [
        "view",
    ]
    admin_abilities = [
        "view",
    ]

    def get_rater_permissions(self):
        return ["view", "add", "change", "delete"], [
            "view",
        ]

    def get_provider_permissions(self):
        return ["view", "add", "change", "delete"], [
            "view",
        ]

    def get_trc_permissions(self):
        return [], []

    def get_provider_home_innovation_research_labs_permissions(self):
        return [], []

    def get_sponsored_provider_home_innovation_research_labs_permissions(self):
        return [], []
