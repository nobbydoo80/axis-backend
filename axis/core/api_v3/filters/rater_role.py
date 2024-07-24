"""rater_role.py: """

__author__ = "Artem Hruzd"
__date__ = "05/11/2022 16:58"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model
from axis.core.api_v3 import RATER_ROLE_FILTER_FIELDS
from axis.core.models import RaterRole


User = get_user_model()


class RaterRoleFilter(filters.FilterSet):
    user = filters.ModelChoiceFilter(queryset=User.objects.all(), method="get_user")

    class Meta:
        model = RaterRole
        fields = RATER_ROLE_FILTER_FIELDS

    def get_user(self, queryset, name, user):
        return queryset.filter(id__in=user.rater_roles.all().values("id"))
