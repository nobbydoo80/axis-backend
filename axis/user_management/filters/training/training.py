"""training.py: """


import django_filters
from django.utils import timezone
from axis.user_management.models import Training

__author__ = "Artem Hruzd"
__date__ = "12/16/2019 17:01"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TrainingDateRangeFilter(django_filters.DateRangeFilter):
    choices = [
        ("", "Any date"),
        ("1", "Last Training > 90 Days Ago"),
        ("2", "Last Training < 90 Days Ago"),
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


class TrainingFilter(django_filters.FilterSet):
    company = django_filters.NumberFilter(field_name="trainee__company__pk")
    training_date_start = django_filters.DateFilter(
        field_name="training_date",
        lookup_expr="gt",
    )
    training_date_end = django_filters.DateFilter(field_name="training_date", lookup_expr="lt")
    training_date_range = TrainingDateRangeFilter(field_name="training_date")
    training_status_state = django_filters.CharFilter(field_name="trainingstatus__state")

    class Meta:
        model = Training
        fields = ["training_type", "attendance_type"]
