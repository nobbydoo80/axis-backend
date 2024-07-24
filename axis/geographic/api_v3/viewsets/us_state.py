"""state.py: """

__author__ = "Artem Hruzd"
__date__ = "07/16/2020 21:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter
from ...models import USState
from ..serializers import USStateSerializer


class USStateViewSet(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin):
    """
    list:
        Get all US States


        Returns US State objects
    """

    model = USState
    queryset = model.objects.all()
    permission_classes = [
        AllowAny,
    ]
    serializer_class = USStateSerializer
    filter_backends = [DjangoFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = ["abbr", "name"]
    ordering_fields = ["abbr", "name"]
    pagination_class = None
