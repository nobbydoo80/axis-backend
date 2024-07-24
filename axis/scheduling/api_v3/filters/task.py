"""task.py: """

__author__ = "Artem Hruzd"
__date__ = "10/10/2022 20:00"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.utils import timezone
from django_filters import rest_framework as filters

from axis.scheduling.api_v3 import TASK_FILTER_FIELDS
from axis.scheduling.models import Task


class TaskDateRangeFilter(filters.DateRangeFilter):
    choices = [
        ("", "Any date"),
        ("1", "Task Scheduled > 7 Days"),
        ("2", "Task Scheduled < 7 days"),
    ]
    filters = {
        "": lambda qs, name: qs,
        "1": lambda qs, name: qs.filter(
            **{
                "%s__lt" % name: timezone.now().date() - timezone.timedelta(days=7),
            }
        ),
        "2": lambda qs, name: qs.filter(
            **{
                "%s__gt" % name: timezone.now().date() - timezone.timedelta(days=7),
            }
        ),
    }


class TaskFilter(filters.FilterSet):
    datetime_range = TaskDateRangeFilter(field_name="datetime")
    datetime__gte = filters.DateFilter(
        field_name="datetime",
        lookup_expr="gte",
    )
    datetime__lte = filters.DateFilter(field_name="datetime", lookup_expr="lte")

    class Meta:
        model = Task
        fields = TASK_FILTER_FIELDS
