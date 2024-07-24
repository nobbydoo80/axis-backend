"""admin.py: Django eep_program"""


import logging
from django.contrib import admin
from django.utils.html import format_html

from axis.eep_program.models import EEPProgram
from axis.eep_program.utils import create_qa_program_from_base
from axis.core.admin_utils import RelatedDropdownFilter

__author__ = "Steven Klass"
__date__ = "7/24/12 7:06 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class EEPProgramAdmin(admin.ModelAdmin):
    model = EEPProgram
    search_fields = ("name", "slug")
    list_filter = (("owner", RelatedDropdownFilter),)
    list_display = (
        "name",
        "program_visibility_date",
        "program_start_date",
        "program_close_date",
        "program_end_date",
    )
    filter_horizontal = [
        "required_annotation_types",
        "opt_in_out_list",
        "certifiable_by",
    ]
    raw_id_fields = ("collection_request", "owner")
    fieldsets = (
        (
            "General",
            {
                "fields": (
                    (
                        "name",
                        "slug",
                        "is_legacy",
                        "is_active",
                        "is_public",
                        "opt_in",
                        "is_qa_program",
                        "is_multi_family",
                    ),
                    "workflow",
                    "owner",
                    "comment",
                    (
                        "builder_incentive_dollar_value",
                        "rater_incentive_dollar_value",
                        "per_point_adder",
                    ),
                    "collection_request",
                    "manual_transition_on_certify",
                    (
                        "require_resnet_sampling_provider",
                        "allow_sampling",
                        "allow_metro_sampling",
                    ),
                    (
                        "program_visibility_date",
                        "program_start_date",
                        "program_close_date",
                        "program_submit_date",
                        "program_end_date",
                    ),
                    ("program_submit_warning_date", "program_submit_warning"),
                    ("program_close_warning_date", "program_close_warning"),
                    "required_annotation_types",
                )
            },
        ),
        (
            "Program Settings",
            {
                "fields": (
                    ("certifiable_by",),
                    ("viewable_by_company_type",),
                    ("opt_in_out_list",),
                )
            },
        ),
        ("Standard Disclosure", {"fields": (("enable_standard_disclosure",),)}),
        (
            "Model Input",
            {
                "fields": (
                    "require_input_data",
                    ("allow_rem_input", "require_rem_data", "require_model_file"),
                    ("min_hers_score", "max_hers_score"),
                ),
            },
        ),
        (
            "Customer HIRL",
            {
                "fields": (
                    ("customer_hirl_certification_fee",),
                    ("customer_hirl_per_unit_fee",),
                )
            },
        ),
        (
            "Relations",
            {
                "fields": (
                    (
                        "require_builder_assigned_to_home",
                        "require_builder_relationship",
                    ),
                    (
                        "require_utility_assigned_to_home",
                        "require_utility_relationship",
                    ),
                    ("require_hvac_assigned_to_home", "require_hvac_relationship"),
                    ("require_rater_assigned_to_home", "require_rater_relationship"),
                    (
                        "require_provider_assigned_to_home",
                        "require_provider_relationship",
                    ),
                    ("require_qa_assigned_to_home", "require_qa_relationship"),
                    (
                        "require_architect_assigned_to_home",
                        "require_architect_relationship",
                    ),
                    (
                        "require_developer_assigned_to_home",
                        "require_developer_relationship",
                    ),
                    (
                        "require_communityowner_assigned_to_home",
                        "require_communityowner_relationship",
                    ),
                    (
                        "require_rater_of_record",
                        "require_energy_modeler",
                        "require_field_inspector",
                    ),
                )
            },
        ),
    )
    actions = (
        "create_qa_program",
        "mark_program_not_participating",
        "enable_standard_disclosure",
        "disable_standard_disclosure",
    )

    def create_qa_program(self, request, queryset):
        for instance in queryset:
            create_qa_program_from_base(instance)

    create_qa_program.short_description = "Create QA Program from selected Program"

    def mark_program_not_participating(self, request, queryset):
        from axis.company.models import Company

        companies = Company.objects.all()
        for instance in queryset:
            instance.companies_ignoring_during_home_status_creation = companies

    mark_program_not_participating.short_description = (
        'Mark program "Not Participating" for all Companies'
    )

    def enable_standard_disclosure(self, request, queryset):
        queryset.update(enable_standard_disclosure=True)

    def disable_standard_disclosure(self, request, queryset):
        queryset.update(enable_standard_disclosure=False)


admin.site.register(EEPProgram, EEPProgramAdmin)
