"""admin.py: Django qa"""


import logging

from django.contrib import admin
from django.contrib.admin.options import TabularInline

from .models import QARequirement, QAStatus, QANote

__author__ = "Steven Klass"
__date__ = "1/20/14 4:51 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class QARequirementAdmin(admin.ModelAdmin):
    model = QARequirement
    search_fields = ["qa_company__name", "eep_program__name", "type", "required_companies__name"]
    list_display = ("qa_company", "eep_program", "type", "gate_certification", "coverage_pct")
    filter_horizontal = ("required_companies",)
    raw_id_fields = ("qa_company", "eep_program")

    actions = [
        "make_type_file",
        "make_type_field",
        "make_type_program_review",
        "make_gate_certification_true",
        "make_gate_certification_false",
    ]

    def _change_type(self, queryset, type):
        for instance in queryset:
            instance.type = type
            instance.save()

    def _change_gate_certification(self, queryset, value):
        for instance in queryset:
            instance.gate_certification = value
            instance.save()

    def make_type_file(self, request, queryset):
        self._change_type(queryset, "file")

    make_type_file.short_description = "Mark selected as Type File"

    def make_type_field(self, request, queryset):
        self._change_type(queryset, "field")

    make_type_field.short_description = "Mark selected as Type Field"

    def make_type_program_review(self, request, queryset):
        self._change_type(queryset, "program_review")

    make_type_program_review.short_description = "Mark selected as Type Program Review"

    def make_gate_certification_true(self, request, queryset):
        self._change_gate_certification(queryset, True)

    make_gate_certification_true.short_description = "Mark selected as Gating Certification"

    def make_gate_certification_false(self, request, queryset):
        self._change_gate_certification(queryset, False)

    make_gate_certification_false.short_description = "Mark selected as not Gating Certification"


class QANoteInlineAdmin(TabularInline):
    """Inline Document"""

    model = QANote
    fk_name = "qa_status"
    fields = ("note", "user")
    readonly_fields = ("content_type", "content_object", "object_id")
    extra = 0

    def has_add_permission(self, request, obj):
        return False


class QAStatusAdmin(admin.ModelAdmin):
    model = QAStatus
    search_fields = [
        "home_status__home__street_line1",
        "home_status__eep_program__name",
        "subdivision__name",
    ]
    list_display = ("home_status", "subdivision", "owner", "result", "state")
    list_filter = ("state",)
    inlines = (QANoteInlineAdmin,)
    raw_id_fields = ("home_status", "subdivision", "owner", "requirement")

    actions = [
        "send_fake_qa_review_fail_email",
    ]

    fieldsets = (
        (
            None,
            {"fields": ("home_status", "subdivision", "owner", ("result", "state"), "requirement")},
        ),
        (
            "Customer Home Innovation Research Labs",
            {
                "classes": ("collapse",),
                "fields": (
                    "hirl_verifier_points_reported",
                    "hirl_verifier_points_awarded",
                    "hirl_certification_level_awarded",
                    "hirl_badges_awarded",
                    "hirl_commercial_space_confirmed",
                    "hirl_reviewer_wri_value_awarded",
                    "hirl_water_sense_confirmed",
                ),
            },
        ),
    )

    def send_fake_qa_review_fail_email(self, request, queryset):
        from axis.qa.tasks import qa_review_fail_daily_email

        qa_review_fail_daily_email(triggered_from_admin_interface=True, queryset=queryset)

    send_fake_qa_review_fail_email.short_description = "Send Fake QA Review Fail Email"


admin.site.register(QARequirement, QARequirementAdmin)
admin.site.register(QAStatus, QAStatusAdmin)
