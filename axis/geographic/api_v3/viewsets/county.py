"""county.py: """

__author__ = "Artem Hruzd"
__date__ = "01/03/2020 22:10"
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
from ...models import County
from ..filters import CountyFilter
from ..serializers import CountySerializer, CountyDetailSerializer


class CountyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows County to be viewed
    retrieve:
        Return a County instance.
    list:
        Return all available Counties
    attached:
        Return all Counties that fall into user Company counties
    """

    model = County
    queryset = model.objects.all()
    filterset_class = CountyFilter
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = ["name", "state"]
    ordering_fields = ["name", "state"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CountyDetailSerializer
        return CountySerializer


class NestedCountyViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = County
    queryset = model.objects.all()
    serializer_class = CountySerializer
    filterset_class = CountyFilter
    filter_backends = [DjangoFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = ["name", "state"]
    ordering_fields = ["name", "state"]
