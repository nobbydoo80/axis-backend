"""fields.py: Fields definitions leveraging the Select2 tools. """


import re
import operator

from django.db.models import Q

from axis.core.fields import ApiModelSelect2Widget
from .api import (
    CityViewSet,
    SimpleCityViewSet,
    CountyViewSet,
    UnrestrictedCityViewSet,
    UnrestrictedCountyViewSet,
)

__author__ = "Steven Klass"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class CityStateSearchMixin(object):
    page_size = 50


class CityChoiceWidget(CityStateSearchMixin, ApiModelSelect2Widget):
    permission_required = "geographic.view_city"
    viewset_class = CityViewSet
    search_fields = ["name__icontains", "county__state__exact", "country__abbr__exact"]


class UnrestrictedCityChoiceWidget(CityStateSearchMixin, ApiModelSelect2Widget):
    permission_required = "geographic.view_city"
    viewset_class = UnrestrictedCityViewSet
    search_fields = ["name__icontains", "county__state__exact", "country__abbr__exact"]


class CountyChoiceWidget(ApiModelSelect2Widget):
    permission_required = "geographic.view_county"
    viewset_class = CountyViewSet
    search_fields = ["name__icontains", "state__exact"]
