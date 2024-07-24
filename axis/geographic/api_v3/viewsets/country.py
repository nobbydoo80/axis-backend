"""country.py - axis"""

__author__ = "Steven K"
__date__ = "7/25/22 14:13"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

import django_auto_prefetching
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter
from axis.core.api_v3.permissions import (
    IsUserIsCompanyAdminPermission,
    IsAdminUserOrSuperUserPermission,
)
from axis.geographic.api_v3.filters import CountryFilter
from axis.geographic.api_v3.serializers import CountrySerializer
from axis.geographic.models import Country

log = logging.getLogger(__name__)


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows County to be viewed
    retrieve:
        Return a County instance.
    list:
        Return all available Counties
    attached:
        Return all Counties that fall into user Company counties
    """

    model = Country
    queryset = model.objects.all()
    filterset_class = CountryFilter
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = ["abbr", "name"]
    ordering_fields = ["abbr", "name"]

    def get_serializer_class(self):
        return CountrySerializer

    def get_queryset(self):
        queryset = super(CountryViewSet, self).get_queryset()
        return django_auto_prefetching.prefetch(queryset, self.get_serializer_class())
