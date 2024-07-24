"""certification.py: """

__author__ = "Artem Hruzd"
__date__ = "05/24/2021 6:59 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.decorators import register
from django.db.models import Count, Case, When, IntegerField

from axis.company.models import Company
from axis.core.admin_utils import DropdownFilter
from axis.customer_hirl.models import HIRLLegacyCertification


class HomeHasRelationshipFilter(SimpleListFilter):
    @property
    def title(self):
        raise NotImplementedError

    @property
    def parameter_name(self):
        raise NotImplementedError

    @property
    def company_type(self):
        raise NotImplementedError

    def lookups(self, request, model_admin):
        return [("true", "Yes"), ("false", "No")]

    def queryset(self, request, queryset):
        if self.value() == "true":
            return queryset.annotate(
                count_builder_relationships=Count(
                    Case(
                        When(home__relationships__company__company_type=self.company_type, then=1),
                        output_field=IntegerField(),
                    )
                )
            ).filter(count_builder_relationships__gte=1)
        if self.value() == "false":
            return queryset.annotate(
                count_builder_relationships=Count(
                    Case(
                        When(home__relationships__company__company_type=self.company_type, then=1),
                        output_field=IntegerField(),
                    )
                )
            ).filter(count_builder_relationships=0)
        return queryset


class HomeHasBuilderRelationshipFilter(HomeHasRelationshipFilter):
    title = "Home has builder association"
    parameter_name = "has_builder"
    company_type = Company.BUILDER_COMPANY_TYPE


class HomeHasRaterRelationshipFilter(HomeHasRelationshipFilter):
    title = "Home has verifier association"
    parameter_name = "has_rater"
    company_type = Company.RATER_COMPANY_TYPE


class HIRLLegacyCertificationByStateFilter(SimpleListFilter):
    title = "Legacy State Ready For Import"
    parameter_name = "legacy_state"

    def lookups(self, request, model_admin):
        statuses = [-7, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        return [(status, status) for status in statuses]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(data__fkCertificationStatus=self.value())
        return queryset


@register(HIRLLegacyCertification)
class HIRLLegacyCertificationAdmin(admin.ModelAdmin):
    search_fields = ["hirl_id", "hirl_project_id", "project__id", "data"]
    list_display = ["hirl_id", "hirl_project_id", "scoring_path_name", "project"]
    list_filter = (
        ("scoring_path_name", DropdownFilter),
        ("project", admin.EmptyFieldListFilter),
        "convert_to_registration_error",
        HIRLLegacyCertificationByStateFilter,
    )
    raw_id_fields = ("project",)
