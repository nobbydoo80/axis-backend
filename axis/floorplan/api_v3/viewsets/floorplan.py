__author__ = "Artem Hruzd"
__date__ = "08/27/2020 22:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


import rest_framework.status
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Count
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.decorators import action
from rest_framework.response import Response

from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend
from axis.core.api_v3.mixins import RecentlyViewedMixin
from axis.core.api_v3.viewsets import NestedHistoryViewSet
from axis.filehandling.api_v3.viewsets import NestedCustomerDocumentViewSet
from axis.floorplan.api_v3 import FLOORPLAN_SEARCH_FIELDS, FLOORPLAN_ORDERING_FIELDS
from axis.floorplan.api_v3.filters import FloorplanFilter
from axis.floorplan.api_v3.serializers import (
    BasicFloorplanSerializer,
    FloorplanSerializer,
    FloorplanFlatListSerializer,
    FloorplanFromBlgSerializer,
)
from axis.floorplan.models import Floorplan
from axis.relationship.api_v3.viewsets import NestedRelationshipViewSet
from axis.home.api_v3.viewsets import NestedEEPProgramHomeStatusViewSet
from axis.floorplan.api_v3.serializers.eep_program_home_status import (
    EEPProgramHomeStatusSerializer,
)
from axis.filehandling.api_v3.viewsets import CustomerDocumentAccessLevelMixin
from axis.company.api_v3.permissions import (
    RaterCompanyMemberPermission,
    ProviderCompanyMemberPermission,
)
from axis.core.api_v3.permissions import IsAdminUserOrSuperUserPermission


class FloorplanViewSet(RecentlyViewedMixin, viewsets.ModelViewSet):
    """
    retrieve:
        Get floorplan by ID


        Returns a floorplan
    list:
        Get all floorplans


        Returns all floorplans available for user
    create:
        Create a new floorplan


        Returns created floorplan
    partial_update:
        Update one or more fields on an existing floorplan


        Returns updated floorplan
    update:
        Update floorplan


        Returns updated floorplan
    delete:
        Delete floorplan and all related objects


        Delete floorplan and all related objects
    """

    model = Floorplan
    serializer_class = BasicFloorplanSerializer
    queryset = model.objects.all()
    filterset_class = FloorplanFilter
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = FLOORPLAN_SEARCH_FIELDS
    ordering_fields = FLOORPLAN_ORDERING_FIELDS
    ordering = ("-id",)

    @property
    def permission_classes(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return (
                IsAdminUserOrSuperUserPermission
                | RaterCompanyMemberPermission
                | ProviderCompanyMemberPermission,
            )

        return (IsAuthenticated,)

    def get_queryset(self):
        queryset = super(FloorplanViewSet, self).get_queryset()
        queryset = queryset.filter_by_user(user=self.request.user, show_attached=True)
        queryset = queryset.annotate(
            homes_count=Count("homestatuses__home"),
        )
        return queryset

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return FloorplanSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=["get"], serializer_class=FloorplanFlatListSerializer)
    def flat_list(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.company)

    @transaction.atomic
    @swagger_auto_schema(
        responses={
            400: "Invalid data in uploaded file",
            201: FloorplanSerializer,
        },
    )
    @action(
        detail=False,
        methods=["post"],
        parser_classes=[
            MultiPartParser,
        ],
        serializer_class=FloorplanFromBlgSerializer,
    )
    def create_from_blg(self, request: Request, **kwargs) -> Response:
        """Upload a Rem BLG file and create a floorplan with BLG as the Simulation."""
        serializer = FloorplanFromBlgSerializer(
            data=request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        floorplan = serializer.create(validated_data=serializer.validated_data)
        return Response(
            FloorplanSerializer(instance=floorplan).data,
            status=rest_framework.status.HTTP_201_CREATED,
        )


class NestedFloorplanViewSet(
    NestedViewSetMixin, viewsets.mixins.ListModelMixin, viewsets.GenericViewSet
):
    model = Floorplan
    permission_classes = (IsAuthenticated,)
    queryset = Floorplan.objects.all()
    filterset_class = FloorplanFilter
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = FLOORPLAN_SEARCH_FIELDS
    ordering_fields = FLOORPLAN_ORDERING_FIELDS

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return FloorplanSerializer
        return BasicFloorplanSerializer


class FloorplanNestedHistoryViewSet(NestedHistoryViewSet):
    model = Floorplan.history.model
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = FLOORPLAN_SEARCH_FIELDS
    ordering_fields = FLOORPLAN_ORDERING_FIELDS


class FloorplanNestedRelationshipViewSet(NestedRelationshipViewSet):
    ct_model = Floorplan


class FloorplanNestedDocumentViewSet(
    NestedCustomerDocumentViewSet, CustomerDocumentAccessLevelMixin
):
    model = Floorplan

    def create(self, request, *args, **kwargs) -> Response:
        data = self.get_pruned_request_data(request.data)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(
            content_type=ContentType.objects.get_for_model(self.model),
            object_id=self.get_parents_query_dict().get("object_id"),
            company=self.request.user.company,
        )


class FloorplanNestedHomeStatusViewSet(NestedEEPProgramHomeStatusViewSet):
    """Provides Home status, EEP Program and Subdivision info for given Floorplan"""

    def get_serializer_class(self):
        return EEPProgramHomeStatusSerializer

    def get_queryset(self):
        return super().get_queryset().order_by("-id")

    def get_serializer_context(self):
        data = super().get_serializer_context()
        data["user"] = self.request.user
        return data
