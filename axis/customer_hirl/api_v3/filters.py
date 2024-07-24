"""filters.py: """

__author__ = "Artem Hruzd"
__date__ = "07/23/2020 20:06"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django_filters import rest_framework as filters
from django.apps import apps

from axis.core.utils.utils import YEAR_CHOICES
from axis.customer_hirl.api_v3 import (
    HIRL_PROJECT_FILTER_FIELDS,
    HIRL_GREEN_EENERGY_BADGE_FILTER_FIELDS,
    COI_DOCUMENT_FILTER_FIELDS,
    HIRL_PROJECT_REGISTRATION_FILTER_FIELDS,
    CLIENT_AGREEMENT_FILTER_FIELDS,
    VERIFIER_AGREEMENT_FILTER_FIELDS,
    PROVIDED_SERVICE_FILTER_FIELDS,
)
from axis.customer_hirl.models import (
    HIRLProject,
    HIRLGreenEnergyBadge,
    COIDocument,
    HIRLProjectRegistration,
    BuilderAgreement,
    VerifierAgreement,
    ProvidedService,
)
from axis.eep_program.models import EEPProgram

customer_hirl_app = apps.get_app_config("customer_hirl")


class HIRLProjectFilter(filters.FilterSet):
    registration__epp_program__slug = filters.ModelMultipleChoiceFilter(
        field_name="registration__eep_program__slug",
        to_field_name="slug",
        queryset=EEPProgram.objects.all(),
    )
    created_at__gte = filters.DateFilter(
        field_name="created_at",
        lookup_expr="gte",
    )
    created_at__lte = filters.DateFilter(field_name="created_at", lookup_expr="lte")
    created_at_range = filters.DateRangeFilter(field_name="created_at")

    class Meta:
        model = HIRLProject
        fields = HIRL_PROJECT_FILTER_FIELDS


class HIRLProjectRegistrationFilter(filters.FilterSet):
    eep_program = filters.ModelMultipleChoiceFilter(
        field_name="eep_program",
        to_field_name="pk",
        queryset=EEPProgram.objects.all(),
    )
    eep_program__slug = filters.ModelMultipleChoiceFilter(
        field_name="eep_program__slug",
        to_field_name="slug",
        queryset=EEPProgram.objects.all(),
    )
    without_projects = filters.BooleanFilter(field_name="projects", lookup_expr="isnull")

    class Meta:
        model = HIRLProjectRegistration
        fields = HIRL_PROJECT_REGISTRATION_FILTER_FIELDS


class HIRLProjectRegistrationActivityMetricsByMonthFilter(filters.FilterSet):
    years = filters.MultipleChoiceFilter(choices=YEAR_CHOICES, method="get_years")
    eep_program__slug = filters.ModelMultipleChoiceFilter(
        to_field_name="slug", queryset=EEPProgram.objects.all()
    )

    class Meta:
        model = HIRLProjectRegistration
        fields = ("years", "eep_program__slug", "is_build_to_rent")

    def get_years(self, queryset, field_name, value):
        return queryset.filter(created_at__year__in=value)


class HIRLProjectCycleTimeMetricsFilter(filters.FilterSet):
    years = filters.MultipleChoiceFilter(choices=YEAR_CHOICES, method="get_years")

    class Meta:
        model = HIRLProject
        fields = ("years", "registration__project_type")

    @property
    def qs(self):
        queryset = super(HIRLProjectCycleTimeMetricsFilter, self).qs
        queryset = queryset.filter(home_status__certification_date__isnull=False)
        return queryset

    def get_years(self, queryset, field_name, value):
        return queryset.filter(home_status__certification_date__year__in=value)


class HIRLGreenEnergyBadgeFilter(filters.FilterSet):
    eep_program = filters.ModelChoiceFilter(
        method="get_filter_by_eep_program", queryset=EEPProgram.objects.all()
    )

    class Meta:
        model = HIRLGreenEnergyBadge
        fields = HIRL_GREEN_EENERGY_BADGE_FILTER_FIELDS

    def get_filter_by_eep_program(self, queryset, field_name, eep_program):
        return queryset.filter_by_eep_program(slug=eep_program.slug)


class COIDocumentFilter(filters.FilterSet):
    is_active = filters.BooleanFilter(method="get_is_active")

    class Meta:
        model = COIDocument
        fields = COI_DOCUMENT_FILTER_FIELDS

    def get_is_active(self, queryset, field_name, value):
        return queryset.active()


class ClientAgreementFilter(filters.FilterSet):
    class Meta:
        model = BuilderAgreement
        fields = CLIENT_AGREEMENT_FILTER_FIELDS


class VerifierAgreementFilter(filters.FilterSet):
    class Meta:
        model = VerifierAgreement
        fields = VERIFIER_AGREEMENT_FILTER_FIELDS


class ProvidedServiceFilter(filters.FilterSet):
    class Meta:
        model = ProvidedService
        fields = PROVIDED_SERVICE_FILTER_FIELDS
