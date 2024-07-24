"""filters.py: """

__author__ = "Artem Hruzd"
__date__ = "11/19/2021 7:29 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.utils import timezone
from django_filters import rest_framework as filters

from axis.eep_program.models import EEPProgram
from axis.user_management.models import Accreditation, InspectionGrade


class AccreditationFilter(filters.FilterSet):
    date_initial_gte = filters.DateFilter(
        field_name="date_initial",
        lookup_expr="gte",
    )
    date_initial_lte = filters.DateFilter(field_name="date_initial", lookup_expr="lte")
    date_initial_range = filters.DateRangeFilter(field_name="date_initial")

    date_last_gte = filters.DateFilter(
        field_name="date_last",
        lookup_expr="gte",
    )
    date_last_lte = filters.DateFilter(field_name="date_last", lookup_expr="lte")
    date_last_range = filters.DateRangeFilter(field_name="date_last")

    expiration_date_gte = filters.DateFilter(method="expiration_gte_filter")
    expiration_date_lte = filters.DateFilter(method="expiration_lte_filter")
    expiration_within_days = filters.NumberFilter(method="expiration_within_days_filter")
    is_expired = filters.BooleanFilter(method="is_expired_filter")

    class Meta:
        model = Accreditation
        fields = ["name", "state", "role", "trainee__company"]

    def expiration_gte_filter(self, queryset, name, value):
        return queryset.annotate_expiration_date().filter(expiration_date__gte=value)

    def expiration_lte_filter(self, queryset, name, value):
        return queryset.annotate_expiration_date().filter(expiration_date__lte=value)

    def is_expired_filter(self, queryset, name, value):
        if value:
            return queryset.annotate_expiration_date().filter(expiration_date__lt=timezone.now())
        return queryset.annotate_expiration_date().filter(expiration_date__gt=timezone.now())

    def expiration_within_days_filter(self, queryset, name, value):
        queryset = queryset.annotate_expiration_date().filter(
            expiration_date__range=(
                timezone.now(),
                timezone.now() + timezone.timedelta(days=int(value)),
            )
        )
        return queryset


class InspectionGradeFilter(filters.FilterSet):
    graded_date__gte = filters.DateFilter(
        field_name="graded_date",
        lookup_expr="gte",
    )
    graded_date__lte = filters.DateFilter(
        field_name="graded_date",
        lookup_expr="lte",
    )
    qa_status__home_status__eep_program = filters.ModelMultipleChoiceFilter(
        field_name="qa_status__home_status__eep_program",
        to_field_name="id",
        queryset=EEPProgram.objects.all(),
    )

    class Meta:
        model = InspectionGrade
        fields = [
            "user__company",
            "letter_grade",
            "numeric_grade",
            "approver",
            "qa_status__requirement__type",
        ]
