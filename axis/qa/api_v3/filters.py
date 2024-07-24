"""filters.py: """

__author__ = "Artem Hruzd"
__date__ = "07/16/2020 20:48"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from axis.qa.api_v3 import QA_STATUS_FILTER_FIELDS, OBSERVATION_FILTER_FIELDS, QA_NOTE_FILTER_FIELDS
from axis.qa.models import QAStatus, Observation, QANote

User = get_user_model()


class QAStatusFilter(filters.FilterSet):
    created_date__gte = filters.DateFilter(
        field_name="created_date", lookup_expr="gte", label="Date Created is greater then or equal"
    )
    created_date__lte = filters.DateFilter(
        field_name="created_date", lookup_expr="lte", label="Date Created is less then or equal"
    )
    created_date__range = filters.DateRangeFilter(
        field_name="created_date", label="Date Created range"
    )
    qa_designee = filters.ModelMultipleChoiceFilter(
        field_name="qa_designee",
        to_field_name="pk",
        queryset=User.objects.filter(hirluserprofile__is_qa_designee=True),
    )

    class Meta:
        model = QAStatus
        fields = QA_STATUS_FILTER_FIELDS


class ObservationFilter(filters.FilterSet):
    class Meta:
        model = Observation
        fields = OBSERVATION_FILTER_FIELDS


class QANoteFilter(filters.FilterSet):
    class Meta:
        model = QANote
        fields = QA_NOTE_FILTER_FIELDS
