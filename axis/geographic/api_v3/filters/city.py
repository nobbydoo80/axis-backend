"""Api v3 city filter."""


from django_filters import rest_framework as filters

from axis.company.api_v3.filters import CompanyIsAttachedChoiceFilter
from axis.geographic.models import City

__author__ = "Artem Hruzd"
__date__ = "01/03/2020 22:53"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class CityFilter(filters.FilterSet):
    is_attached = CompanyIsAttachedChoiceFilter(is_relationship_based=False)

    class Meta:
        model = City
        fields = ["country__abbr", "name", "county__name", "county__state"]
