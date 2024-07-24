"""home.py - Axis"""

__author__ = "Steven K"
__date__ = "7/16/21 12:23"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import itertools
import logging

from django.db.models import F
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from axis.core.api_v3.filters import AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter
from axis.core.api_v3.mixins import RecentlyViewedMixin
from axis.core.api_v3.viewsets import NestedHistoryViewSet
from axis.filehandling.api_v3.viewsets import NestedCustomerDocumentViewSet
from axis.home.api_v3 import HOME_SEARCH_FIELDS, HOME_ORDERING_FIELDS
from axis.home.api_v3.filters import HomeFilter
from axis.home.api_v3.serializers import (
    HomeRecentlyUpdatedFileObservationSerializer,
    HomeSerializer,
    BasicHomeSerializer,
    HomeAddressIsUniqueRequestDataSerializer,
)
from axis.home.models import Home
from axis.qa.models import QARequirement
from axis.relationship.api_v3.viewsets import NestedRelationshipByCompanyTypeViewSet

log = logging.getLogger(__name__)


class HomeViewSet(RecentlyViewedMixin, viewsets.ModelViewSet):
    """
    home_address_is_unique:
    Check if home with provided address already exists


    Returns Home instance in case home already exists or None
    recently_updated_file_observations:
    List of homes with recently added file observations


    Returns list of homes data with recently added file observations
    """

    model = Home
    permission_classes = (IsAuthenticated,)
    queryset = Home.objects.all()
    filterset_class = HomeFilter
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = HOME_SEARCH_FIELDS
    ordering_fields = HOME_ORDERING_FIELDS

    def get_serializer_class(self):
        if self.action == "recently_updated_file_observations":
            return HomeRecentlyUpdatedFileObservationSerializer
        if self.request.user.is_superuser:
            return HomeSerializer
        return BasicHomeSerializer

    def get_queryset(self):
        # swagger hack
        if not self.request.user.is_authenticated:
            return self.model.objects.none()
        qs = self.model.objects.filter_by_user(user=self.request.user)
        if self.action == "recently_updated_file_observations":
            qs = qs.filter(
                homestatuses__qastatus__requirement__type=QARequirement.FILE_QA_REQUIREMENT_TYPE,
                homestatuses__qastatus__subdivision=None,
            )
            return qs
        return qs

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "limit",
                required=False,
                description="Limit results size",
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
            )
        ]
    )
    @action(detail=False, filter_backends=[], pagination_class=None)
    def recently_updated_file_observations(self, request, *args, **kwargs):
        try:
            limit = int(self.request.query_params.get("limit"))
            if limit < 1:
                limit = None
        except (ValueError, TypeError):
            limit = None

        qs = self.get_queryset()
        qs = (
            self.filter_queryset(queryset=qs)
            .values(
                home_id=F("id"),
                home_street_line1=F("street_line1"),
                home_street_line2=F("street_line2"),
                observation_user=F("homestatuses__qastatus__observation__user__id"),
                observation_user_first_name=F(
                    "homestatuses__qastatus__observation__user__first_name"
                ),
                observation_user_last_name=F(
                    "homestatuses__qastatus__observation__user__last_name"
                ),
                observation_type=F("homestatuses__qastatus__observation__observation_type__name"),
                observation_created_on=F("homestatuses__qastatus__observation__created_on"),
            )
            .order_by("-homestatuses__qastatus__observation__created_on")
        )
        results = []
        for group, values in itertools.groupby(qs, lambda obj: obj["home_id"]):
            data = next(values)
            result = {
                "home_id": data["home_id"],
                "home_street_line1": data["home_street_line1"],
                "home_street_line2": data["home_street_line2"],
                "observation_user": data["observation_user"],
                "observation_user_first_name": data["observation_user_first_name"],
                "observation_user_last_name": data["observation_user_last_name"],
                "observations": [value["observation_type"] for value in values],
                "observation_created_on": data["observation_created_on"],
            }
            results.append(result)

        if limit:
            results = results[:limit]
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=HomeAddressIsUniqueRequestDataSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "is_unique": openapi.Schema(
                        title="Is Unique",
                        description="Is the address unique",
                        type=openapi.TYPE_BOOLEAN,
                    ),
                    "home_id": openapi.Schema(
                        title="Home ID",
                        description="Corresponding Home ID (if it's not unique)",
                        type=openapi.TYPE_INTEGER,
                    ),
                },
            )
        },
    )
    @action(
        detail=False,
        methods=[
            "POST",
        ],
        filter_backends=[],
        pagination_class=None,
        serializer_class=HomeAddressIsUniqueRequestDataSerializer,
    )
    def home_address_is_unique(self, request, *args, **kwargs):
        data_serializer = HomeAddressIsUniqueRequestDataSerializer(data=self.request.data)
        data_serializer.is_valid(raise_exception=True)
        is_unique, home = data_serializer.get_home_is_unique()
        return Response({"is_unique": is_unique, "home_id": home.id if home else None})


class HomeNestedRelationshipViewSet(NestedRelationshipByCompanyTypeViewSet):
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

    ct_model = Home


class HomeNestedHistoryViewSet(NestedHistoryViewSet):
    model = Home.history.model
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = HOME_SEARCH_FIELDS
    ordering_fields = HOME_ORDERING_FIELDS


class HomeNestedCustomerDocumentViewSet(NestedCustomerDocumentViewSet):
    def perform_create(self, serializer):
        """
        Override this method by passing content_type, object_id and company
        """
        raise NotImplementedError
