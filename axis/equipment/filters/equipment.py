"""equipment.py: """


import django_filters
from django.utils import timezone

from axis.equipment.models import Equipment

__author__ = "Artem Hruzd"
__date__ = "12/30/2019 18:57"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class CalibrationDateDateRangeFilter(django_filters.DateRangeFilter):
    choices = [
        ("", "Any date"),
        ("1", "Last Calibration Date > 90 Days Ago"),
        ("2", "Last Calibration Date < 90 Days Ago"),
    ]
    filters = {
        "": lambda qs, name: qs,
        "1": lambda qs, name: qs.filter(
            **{
                "%s__lt" % name: timezone.now().date() - timezone.timedelta(days=90),
            }
        ),
        "2": lambda qs, name: qs.filter(
            **{
                "%s__gt" % name: timezone.now().date() - timezone.timedelta(days=90),
            }
        ),
    }


class EquipmentFilter(django_filters.FilterSet):
    company = django_filters.NumberFilter(field_name="owner_company__pk")
    equipment_sponsor_status_state = django_filters.CharFilter(
        field_name="equipmentsponsorstatus__state"
    )
    calibration_date_start = django_filters.DateFilter(
        field_name="calibration_date",
        lookup_expr="gt",
    )
    calibration_date_end = django_filters.DateFilter(
        field_name="calibration_date", lookup_expr="lt"
    )
    calibration_date_range = CalibrationDateDateRangeFilter(field_name="calibration_date")

    expiration_date_start = django_filters.DateFilter(method="expiration_gt_filter")
    expiration_date_end = django_filters.DateFilter(method="expiration_lt_filter")
    expiration_within = django_filters.NumberFilter(method="expiration_within_days_filter")

    class Meta:
        model = Equipment
        fields = [
            "equipment_type",
        ]

    @property
    def qs(self):
        queryset = super(EquipmentFilter, self).qs
        queryset = queryset.filter_by_user(user=self.request.user).prefetch_related("sponsors")
        return queryset
