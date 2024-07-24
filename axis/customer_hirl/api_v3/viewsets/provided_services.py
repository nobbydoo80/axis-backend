"""provided_services.py: """

__author__ = "Artem Hruzd"
__date__ = "03/23/2022 20:09"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import django_auto_prefetching
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_extensions.mixins import NestedViewSetMixin

from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend
from axis.customer_hirl.api_v3 import (
    PROVIDED_SERVICE_SEARCH_FIELDS,
    PROVIDED_SERVICE_ORDERING_FIELDS,
)
from axis.customer_hirl.api_v3.filters import ProvidedServiceFilter
from axis.customer_hirl.api_v3.serializers import ProvidedServiceSerializer
from axis.customer_hirl.models import ProvidedService


class NestedProvidedServiceViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    Verifier Agreement Provided Services

    list:
        List of provided services for Verifier Agreement
    """

    model = ProvidedService
    permission_classes = (IsAuthenticated,)
    queryset = model.objects.all()
    filter_class = ProvidedServiceFilter
    serializer_class = ProvidedServiceSerializer
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = PROVIDED_SERVICE_SEARCH_FIELDS
    ordering_fields = PROVIDED_SERVICE_ORDERING_FIELDS

    def get_queryset(self):
        queryset = super(NestedProvidedServiceViewSet, self).get_queryset()
        return django_auto_prefetching.prefetch(queryset, self.get_serializer_class())
