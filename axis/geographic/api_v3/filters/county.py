"""Api v3 county filter."""


from django_filters import rest_framework as filters

from axis.company.api_v3.filters import CompanyIsAttachedChoiceFilter
from ...models import County

__author__ = "Autumn Valenta"
__date__ = "01/03/2020 22:53"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
    "Steven Klass",
]


class CountyFilter(filters.FilterSet):
    is_attached = CompanyIsAttachedChoiceFilter(is_relationship_based=False)

    class Meta:
        model = County
        fields = ["name", "state"]
