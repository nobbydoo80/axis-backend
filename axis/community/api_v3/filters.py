"""filters.py: """

from django_filters import rest_framework as filters

from axis.community.api_v3 import COMMUNITY_FILTER_FIELDS
from axis.community.models import Community

__author__ = "Artem Hruzd"
__date__ = "06/23/2020 14:47"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class CommunityFilter(filters.FilterSet):
    class Meta:
        model = Community
        fields = COMMUNITY_FILTER_FIELDS
