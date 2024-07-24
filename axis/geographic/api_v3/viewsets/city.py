__author__ = "Artem Hruzd"
__date__ = "01/03/2020 21:11"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import django_auto_prefetching
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_extensions.mixins import NestedViewSetMixin

from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter
from axis.core.api_v3.permissions import (
    IsAdminUserOrSuperUserPermission,
    IsUserIsCompanyAdminPermission,
)
from axis.geographic.api_v3.filters import CityFilter
from axis.geographic.api_v3.serializers import (
    CitySerializer,
    CityDetailSerializer,
    BaseCitySerializer,
)
from axis.geographic.models import City


class CityViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows interaction with Cities
    retrieve:
        Return a City instance.
    list:
        Return all available Cities
    attached:
        Return all Cities that fall into user Company counties
    create:
        Adds a city.
    update:
        Update a city.
    """

    model = City
    queryset = model.objects.all()
    filterset_class = CityFilter
    filter_backends = [DjangoFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = ["name", "county__name", "county__state", "country__abbr"]
    ordering_fields = ["country__abbr", "name", "county__name", "county__state"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return BaseCitySerializer
        if self.action == "retrieve":
            return CityDetailSerializer
        return CitySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = (IsAuthenticated,)
        elif self.action in ["create", "update", "partial_update"]:
            self.permission_classes = (
                IsAuthenticated,
                IsUserIsCompanyAdminPermission | IsAdminUserOrSuperUserPermission,
            )
        elif self.action in ["destroy"]:
            self.permission_classes = (IsAdminUserOrSuperUserPermission,)
        elif self.action in ["metadata"]:
            self.permission_classes = (IsAuthenticated,)
        return super(CityViewSet, self).get_permissions()

    def get_queryset(self):
        queryset = super(CityViewSet, self).get_queryset()
        return django_auto_prefetching.prefetch(queryset, self.get_serializer_class())


class NestedCityViewSet(
    NestedViewSetMixin, viewsets.GenericViewSet, viewsets.mixins.ListModelMixin
):
    """
    API endpoint that allows City to be viewed
    list:
        Return all available Cities in County
    """

    model = City
    queryset = model.objects.all()
    serializer_class = CitySerializer
    filterset_class = CityFilter
    filter_backends = [DjangoFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = ["country__abbr", "name", "county__name", "county__state"]
    ordering_fields = ["country__abbr", "name", "county__name", "county__state"]
