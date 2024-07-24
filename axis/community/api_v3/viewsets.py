"""viewsets.py: """

import django_auto_prefetching

from django.db.models import Count
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from axis.community.api_v3 import COMMUNITY_SEARCH_FIELDS, COMMUNITY_ORDERING_FIELDS
from axis.community.api_v3.filters import CommunityFilter
from axis.community.api_v3.permissions import CommunityDeletePermission
from axis.community.api_v3.serializers import (
    BasicCommunitySerializer,
    CommunitySerializer,
    CommunityFlatListSerializer,
)
from axis.community.models import Community
from axis.relationship.models import Relationship
from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend
from axis.core.api_v3.mixins import RecentlyViewedMixin
from axis.core.api_v3.viewsets import NestedHistoryViewSet
from axis.relationship.api_v3.viewsets import NestedRelationshipByCompanyTypeViewSet

__author__ = "Artem Hruzd"
__date__ = "06/23/2020 14:46"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
    "Naruhito Kaide",
]


class CommunityViewSet(RecentlyViewedMixin, viewsets.ModelViewSet):
    """
    Represents Community endpoint
    retrieve:
        Return a Community instance.
    list:
        Return all Community's available for user
    create:
        Create a new Community.
    partial_update:
        Update one or more fields on an existing Community.
    update:
        Update Community.
    delete:
        Delete Community.


        Remove existing community
    view:
        Add to recently viewed list


        Add Community to Recently viewed list
    recently_viewed:
        Get recently viewed list


        Get recently viewed Communities
    """

    model = Community
    queryset = Community.objects.all()
    serializer_class = BasicCommunitySerializer
    filterset_class = CommunityFilter
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = COMMUNITY_SEARCH_FIELDS
    ordering_fields = COMMUNITY_ORDERING_FIELDS

    def get_queryset(self):
        queryset = super(CommunityViewSet, self).get_queryset()
        if self.action != "all_list":
            queryset = queryset.filter_by_user(user=self.request.user, show_attached=True).annotate(
                total_subdivisions=Count("subdivision"),
            )

        return django_auto_prefetching.prefetch(queryset, self.get_serializer_class())

    def get_serializer_class(self):
        # override default actions serializer
        if self.action in ["retrieve", "create", "update"]:
            if self.request.user.is_superuser:
                return CommunitySerializer
            else:
                return self.serializer_class
        else:
            return self.serializer_class

    @property
    def permission_classes(self):
        if self.action == "destroy":
            return (CommunityDeletePermission,)
        return (IsAuthenticated,)

    @action(detail=False, methods=["get"], serializer_class=CommunityFlatListSerializer)
    def flat_list(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(detail=False, methods=["get"], serializer_class=CommunityFlatListSerializer)
    def all_list(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CommunityNestedRelationshipViewSet(NestedRelationshipByCompanyTypeViewSet):
    """
    Nested Relationship management endpoints.
    list:
        Return all Relationship objects
    create:
        Create a relationship between two objects
    builder:
        Get or Create builder relationship


        Create builder relationship for object
    """

    ct_model = Community


class CommunityNestedHistoryViewSet(NestedHistoryViewSet):
    model = Community.history.model
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = COMMUNITY_SEARCH_FIELDS
    ordering_fields = COMMUNITY_ORDERING_FIELDS
