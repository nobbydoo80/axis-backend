"""viewsets.py: """

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_extensions.mixins import NestedViewSetMixin

from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend
from axis.core.api_v3.mixins import RecentlyViewedMixin
from axis.relationship.api_v3.viewsets import NestedRelationshipViewSet
from axis.subdivision.api_v3 import SUBDIVISION_SEARCH_FIELDS, SUBDIVISION_ORDERING_FIELDS
from axis.subdivision.api_v3.filters import SubdivisionFilter
from axis.subdivision.api_v3.serializers import BasicSubdivisionSerializer, SubdivisionSerializer
from axis.subdivision.models import Subdivision

__author__ = "Artem Hruzd"
__date__ = "06/24/2020 10:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class SubdivisionNestedRelationshipViewSet(NestedRelationshipViewSet):
    """
    list:
        Get relationships


        Returns all relationships
    create:
        Create a relationship with companies


        Returns relationship
    """

    ct_model = Subdivision


class SubdivisionViewSet(RecentlyViewedMixin, viewsets.ModelViewSet):
    """
    retrieve:
        Return a Subdivision instance.
    list:
        Return all Subdivision's available for user
    create:
        Create a new Subdivision.
    partial_update:
        Update one or more fields on an existing Subdivision.
    update:
        Update Subdivision.
    delete:
        Delete Subdivision.
    """

    model = Subdivision
    permission_classes = (IsAuthenticated,)
    queryset = Subdivision.objects.all()
    filterset_class = SubdivisionFilter
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = SUBDIVISION_SEARCH_FIELDS
    ordering_fields = SUBDIVISION_ORDERING_FIELDS

    def get_queryset(self):
        queryset = super(SubdivisionViewSet, self).get_queryset()
        return queryset.filter_by_user(user=self.request.user, show_attached=True)

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return SubdivisionSerializer
        return BasicSubdivisionSerializer


class NestedSubdivisionViewSet(
    NestedViewSetMixin, viewsets.mixins.ListModelMixin, viewsets.GenericViewSet
):
    model = Subdivision
    permission_classes = (IsAuthenticated,)
    queryset = Subdivision.objects.all()
    filterset_class = SubdivisionFilter
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = SUBDIVISION_SEARCH_FIELDS
    ordering_fields = SUBDIVISION_ORDERING_FIELDS

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return SubdivisionSerializer
        return BasicSubdivisionSerializer
