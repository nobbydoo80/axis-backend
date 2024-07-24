"""filters.py: """

from django_filters import rest_framework as filters

from axis.subdivision.api_v3 import SUBDIVISION_FILTER_FIELDS
from axis.subdivision.models import Subdivision

__author__ = "Artem Hruzd"
__date__ = "06/24/2020 10:36"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class SubdivisionFilter(filters.FilterSet):
    class Meta:
        model = Subdivision
        fields = SUBDIVISION_FILTER_FIELDS
