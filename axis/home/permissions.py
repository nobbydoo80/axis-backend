"""permissions.py: Django home"""

import logging

from axis.core.management.commands.set_permissions import AppPermission
from .models import Home, EEPProgramHomeStatus, StandardDisclosureSettings

__author__ = "Steven Klass"
__date__ = "2/1/13 6:22 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class HomePermissions(AppPermission):
    models = [
        Home,
    ]

    def get_trc_permissions(self):
        return []

    def get_provider_home_innovation_research_labs_permissions(self):
        return ["view", "change"]

    def get_sponsored_provider_home_innovation_research_labs_permissions(self):
        return ["view", "change"]

    def get_sponsored_aps_provider_permissions(self):
        return [
            "view",
        ]

    # No idea why this isnt allowed.
    def get_sponsored_eto_rater_permissions(self):
        return ["view", "add", "change", "delete"]

    def get_sponsored_eto_provider_permissions(self):
        return ["view", "add", "change", "delete"]


class EEPProgramHomeStatusPermissions(AppPermission):
    models = [
        EEPProgramHomeStatus,
    ]
    default_admin_abilities = ["view"]

    def get_rater_permissions(self):
        return ["view", "add", "change", "delete"]

    def get_provider_permissions(self):
        return ["view", "add", "change", "delete"]

    def get_qa_permissions(self):
        return ["view", "add", "change", "delete"]

    def get_trc_permissions(self):
        return []

    def get_sponsored_aps_provider_permissions(self):
        return [
            "view",
        ]


class StandardDisclosureSettingsPermissions(AppPermission):
    models = [
        StandardDisclosureSettings,
    ]
