"""accreditation.py: """


import django_filters
from django.utils import timezone

from axis.user_management.models import Accreditation

__author__ = "Artem Hruzd"
__date__ = "12/16/2019 12:32"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class AccreditationFilter(django_filters.FilterSet):
    company = django_filters.NumberFilter(field_name="trainee__company__pk")
    date_initial_start = django_filters.DateFilter(
        field_name="date_initial",
        lookup_expr="gt",
    )
    date_initial_end = django_filters.DateFilter(field_name="date_initial", lookup_expr="lt")
    date_initial_range = django_filters.DateRangeFilter(field_name="date_initial")

    date_last_start = django_filters.DateFilter(
        field_name="date_last",
        lookup_expr="gt",
    )
    date_last_end = django_filters.DateFilter(field_name="date_last", lookup_expr="lt")
    date_last_range = django_filters.DateRangeFilter(field_name="date_last")

    expiration_date_start = django_filters.DateFilter(method="expiration_gt_filter")
    expiration_date_end = django_filters.DateFilter(method="expiration_lt_filter")
    expiration_within = django_filters.NumberFilter(method="expiration_within_days_filter")

    class Meta:
        model = Accreditation
        fields = ["state", "role"]

    @property
    def qs(self):
        queryset = super(AccreditationFilter, self).qs
        if not self.request.user.is_superuser:
            queryset = queryset.filter(approver__company=self.request.user.company)
        return queryset

    def expiration_gt_filter(self, queryset, name, value):
        return queryset.annotate_expiration_date().filter(expiration_date__gt=value)

    def expiration_lt_filter(self, queryset, name, value):
        return queryset.annotate_expiration_date().filter(expiration_date__lt=value)

    def expiration_within_days_filter(self, queryset, name, value):
        queryset = queryset.annotate_expiration_date().filter(
            expiration_date__range=(
                timezone.now(),
                timezone.now() + timezone.timedelta(days=int(value)),
            )
        )
        return queryset
