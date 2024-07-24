"""filters.py: """


__author__ = "Rajesh Pethe"
__date__ = "08/20/2021 18:30:53"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
    "Rajesh Pethe",
]

from logging import getLogger
from django.db import models
from django_filters import rest_framework as filters

from axis.remrate.models import RemRateUser


class RemRateUserFilter(filters.FilterSet):
    class Meta:
        model = RemRateUser
        fields = ["username", "password", "company", "is_active", "created_on", "last_used"]
