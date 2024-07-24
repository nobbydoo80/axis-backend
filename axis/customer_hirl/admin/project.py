"""project.py: """

__author__ = "Artem Hruzd"
__date__ = "05/24/2021 6:55 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib import admin

from axis.core.admin_utils import DropdownFilter
from axis.customer_hirl.models import (
    HIRLProject,
    HIRLProjectRegistration,
    HIRLGreenEnergyBadge,
    HIRLLegacyRegistration,
)


@admin.register(HIRLProjectRegistration)
class HIRLProjectRegistrationAdmin(admin.ModelAdmin):
    raw_id_fields = (
        "registration_user",
        "eep_program",
        "builder_organization",
        "subdivision",
        "builder_organization_contact",
        "developer_organization",
        "developer_organization_contact",
        "community_owner_organization",
        "community_owner_organization_contact",
        "architect_organization",
        "architect_organization_contact",
    )
    list_filter = ("state", "project_type")
    list_display = ("id", "state", "eep_program")
    search_fields = (
        "id",
        "projects__id",
    )


@admin.register(HIRLLegacyRegistration)
class HIRLLegacyRegistrationAdmin(admin.ModelAdmin):
    raw_id_fields = ("registration",)
    list_display = (
        "hirl_id",
        "issued_project_id",
        "scoring_path_name",
        "is_accessory_structure",
        "is_commercial_space",
    )
    search_fields = ("hirl_id", "issued_project_id")
    list_filter = (
        "is_accessory_structure",
        "is_commercial_space",
        ("scoring_path_name", DropdownFilter),
        ("registration", admin.EmptyFieldListFilter),
        "convert_to_registration_error",
    )


@admin.register(HIRLProject)
class HIRLProjectAdmin(admin.ModelAdmin):
    raw_id_fields = (
        "registration",
        "home_status",
        "home_address_geocode",
        "home_address_geocode_response",
        "commercial_space_parent",
        "vr_batch_submission_parent_rough",
        "vr_batch_submission_parent_final",
    )
    list_filter = (
        "is_jamis_milestoned",
        ("system_notes", admin.EmptyFieldListFilter),
        ("vr_batch_submission_parent_rough", admin.EmptyFieldListFilter),
        ("vr_batch_submission_parent_final", admin.EmptyFieldListFilter),
    )
    search_fields = (
        "id",
        "registration__id",
        "h_number",
        "home_address_geocode__raw_street_line1",
        "home_address_geocode__raw_street_line2",
        "home_address_geocode__raw_zipcode",
        "home_address_geocode__raw_city__name",
        "home_status__home__street_line1",
        "home_status__home__city__name",
        "home_status__home__city__county__name",
        "registration__registration_user__first_name",
        "registration__registration_user__last_name",
        "registration__eep_program__name",
        "registration__project_name",
        "hirllegacycertification__hirl_id",
        "hirllegacycertification__hirl_project_id",
    )
    filter_horizontal = ("green_energy_badges",)
    readonly_fields = ("certification_counter",)
    list_display = ("id", "h_number", "home_status", "is_jamis_milestoned")


@admin.register(HIRLGreenEnergyBadge)
class HIRLGreenEnergyBadgeAdmin(admin.ModelAdmin):
    list_filter = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
