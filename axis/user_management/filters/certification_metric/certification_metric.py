"""certification_metric.py: """


import django_filters
from axis.home.models import EEPProgramHomeStatus

__author__ = "Artem Hruzd"
__date__ = "12/16/2019 17:01"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class CertificationMetricFilter(django_filters.FilterSet):
    company = django_filters.NumberFilter(field_name="rater_of_record__company__pk")
    date_start = django_filters.DateFilter(
        field_name="certification_date",
        lookup_expr="gt",
    )
    date_end = django_filters.DateFilter(field_name="certification_date", lookup_expr="lt")
    date_range = django_filters.DateRangeFilter(field_name="certification_date")

    class Meta:
        model = EEPProgramHomeStatus
        fields = [
            "eep_program",
        ]
