"""country.py - axis"""

__author__ = "Steven K"
__date__ = "7/25/22 14:16"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django_filters import rest_framework as filters

from axis.company.api_v3.filters import CompanyIsAttachedChoiceFilter
from axis.geographic.models import Country

log = logging.getLogger(__name__)


class CountryFilter(filters.FilterSet):
    is_attached = CompanyIsAttachedChoiceFilter(is_relationship_based=False)

    class Meta:
        model = Country
        fields = ["abbr", "name"]
