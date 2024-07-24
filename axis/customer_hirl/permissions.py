"""Permissions."""
from axis.core.management.commands.set_permissions import AppPermission
from axis.customer_hirl.models import (
    BuilderAgreement,
    HIRLProject,
    VerifierAgreement,
    Candidate,
    Certification,
)

__author__ = "Steven Klass"
__date__ = "11/28/16 06:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class CustomerHIRLPermissions(AppPermission):
    models = [Candidate, Certification]
    default_abilities = []
    default_admin_abilities = []


class VerifierAgreementPermissions(AppPermission):
    """Permissions for customer and enrollee companies."""

    models = [
        VerifierAgreement,
    ]
    default_abilities = []
    default_admin_abilities = []

    def get_provider_home_innovation_research_labs_permissions(self):
        """Return view/change perms for owner."""
        return ["view", "change"]

    def get_sponsored_provider_home_innovation_research_labs_rater_permissions(self):
        """Return add/view/change perms for enrollees."""
        return ["view", "add", "change"]


class BuilderAgreementPermissions(AppPermission):
    """Permissions for customer and enrollee companies."""

    models = [
        BuilderAgreement,
    ]
    default_abilities = []
    default_admin_abilities = []

    def get_provider_home_innovation_research_labs_permissions(self):
        """Return view/change perms for owner."""
        return ["view", "change"]

    def get_sponsored_provider_home_innovation_research_labs_rater_permissions(self):
        """Return add/view/change perms for enrollees."""
        return ["view", "change"]

    def get_sponsored_provider_home_innovation_research_labs_builder_permissions(self):
        """Return add/view/change perms for enrollees."""
        return ["view", "add", "change"]

    def get_sponsored_provider_home_innovation_research_labs_developer_permissions(self):
        """Return add/view/change perms for enrollees."""
        return ["view", "add", "change"]

    def get_sponsored_provider_home_innovation_research_labs_architect_permissions(self):
        """Return add/view/change perms for enrollees."""
        return ["view", "add", "change"]

    def get_sponsored_provider_home_innovation_research_labs_communityowner_permissions(self):
        """Return add/view/change perms for enrollees."""
        return ["view", "add", "change"]


class ProjectPermissions(AppPermission):
    """Permissions for customer and enrollee companies."""

    models = [
        HIRLProject,
    ]
    default_abilities = []
    default_admin_abilities = []

    def get_provider_home_innovation_research_labs_permissions(self):
        """Return view/change perms for owner."""
        return ["view", "add", "change", "delete"], [
            "view",
        ]
