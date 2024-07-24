"""permissions.py: Django company"""

from axis.company.models import (
    BuilderOrganization,
    RaterOrganization,
    ProviderOrganization,
    EepOrganization,
    HvacOrganization,
    QaOrganization,
    UtilityOrganization,
    GeneralOrganization,
    AltName,
    ArchitectOrganization,
    DeveloperOrganization,
    CommunityOwnerOrganization,
)
from axis.core.management.commands.set_permissions import AppPermission

__author__ = "Steven Klass"
__date__ = "1/31/13 12:02 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class AltNamePermissions(AppPermission):
    models = [
        AltName,
    ]


class BuilderOrganizationPermissions(AppPermission):
    models = [
        BuilderOrganization,
    ]

    def get_builder_permissions(self):
        return [
            "change",
        ], []

    def get_trc_permissions(self):
        return []


class RaterOrganizationPermissions(AppPermission):
    models = [
        RaterOrganization,
    ]

    def get_rater_permissions(self):
        return [
            "change",
        ], []

    def get_trc_permissions(self):
        return []

    def get_sponsored_aps_builder_permissions(self):
        return []


class ProviderOrganizationPermissions(AppPermission):
    models = [
        ProviderOrganization,
    ]

    def get_provider_permissions(self):
        return [
            "change",
        ], []

    def get_trc_permissions(self):
        return []

    def get_sponsored_provider_home_innovation_research_labs_permissions(self):
        return []

    def get_provider_home_innovation_research_labs_permissions(self):
        return []

    def get_sponsored_eto_qa_permissions(self):
        return []

    def get_sponsored_provider_washington_state_university_extension_ene_qa_permissions(
        self,
    ):
        return []

    def get_sponsored_provider_washington_state_university_extension_ene_utility_permissions(
        self,
    ):
        return []

    def get_sponsored_neea_provider_permissions(self):
        return []

    def get_sponsored_eto_utility_permissions(self):
        return []

    def get_peci_permissions(self):
        return []

    def get_e3_energy_llc_permissions(self):
        return []


class EepOrganizationPermissions(AppPermission):
    models = [
        EepOrganization,
    ]

    def get_eep_permissions(self):
        return [
            "change",
        ], []

    def get_aps_permissions(self):
        return []

    def get_sponsored_permissions(self):
        return []

    def get_sponsored_neea_qa_permissions(self):
        return [
            "view",
        ], [
            "view",
        ]


class HvacOrganizationPermissions(AppPermission):
    models = [
        HvacOrganization,
    ]

    def get_hvac_permissions(self):
        return [
            "change",
        ], []

    def get_sponsored_provider_home_innovation_research_labs_permissions(self):
        return []

    def get_provider_home_innovation_research_labs_permissions(self):
        return []


class QaOrganizationPermissions(AppPermission):
    models = [
        QaOrganization,
    ]

    def get_qa_permissions(self):
        return [
            "change",
        ], []

    def get_sponsored_provider_home_innovation_research_labs_permissions(self):
        return []

    def get_provider_home_innovation_research_labs_permissions(self):
        return []


class UtilityOrganizationPermissions(AppPermission):
    models = [
        UtilityOrganization,
    ]

    def get_utility_permissions(self):
        return [
            "change",
        ], []

    def get_sponsored_provider_home_innovation_research_labs_permissions(self):
        return []

    def get_provider_home_innovation_research_labs_permissions(self):
        return []

    def get_sponsored_neea_utility_permissions(self):
        return []

    def get_aps_permissions(self):
        return []


class ArchitectOrganizationPermissions(AppPermission):
    models = [
        ArchitectOrganization,
    ]
    default_abilities = []
    default_admin_abilities = []

    def get_sponsored_provider_home_innovation_research_labs_permissions(self):
        return [
            "view",
            "add",
            "change",
        ]

    def get_provider_home_innovation_research_labs_permissions(self):
        return ["view", "add", "change", "delete"]


class DeveloperOrganizationPermissions(AppPermission):
    models = [
        DeveloperOrganization,
    ]
    default_abilities = []
    default_admin_abilities = []

    def get_sponsored_provider_home_innovation_research_labs_permissions(self):
        return [
            "view",
            "add",
            "change",
        ]

    def get_provider_home_innovation_research_labs_permissions(self):
        return ["view", "add", "change", "delete"]


class CommunityOwnerOrganizationPermissions(AppPermission):
    models = [
        CommunityOwnerOrganization,
    ]
    default_abilities = []
    default_admin_abilities = []

    def get_sponsored_provider_home_innovation_research_labs_permissions(self):
        return [
            "view",
            "add",
            "change",
        ]

    def get_provider_home_innovation_research_labs_permissions(self):
        return ["view", "add", "change", "delete"]


class GeneralOrganizationPermissions(AppPermission):
    models = [
        GeneralOrganization,
    ]

    def get_general_permissions(self):
        return [
            "change",
        ], []

    def get_aps_permissions(self):
        return []

    def get_eto_permissions(self):
        return []

    def get_sponsored_permissions(self):
        return []
