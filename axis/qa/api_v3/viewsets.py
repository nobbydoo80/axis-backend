"""viewsets.py: """

__author__ = "Artem Hruzd"
__date__ = "07/16/2020 20:48"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from axis.annotation.models import Annotation
from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend
from axis.filehandling.api_v3.viewsets import NestedCustomerDocumentViewSet
from axis.qa.api_v3 import (
    QA_STATUS_SEARCH_FIELDS,
    QA_STATUS_ORDERING_FIELDS,
    OBSERVATION_SEARCH_FIELDS,
    OBSERVATION_ORDERING_FIELDS,
    QA_NOTE_SEARCH_FIELDS,
    QA_NOTE_ORDERING_FIELDS,
)
from axis.qa.api_v3.filters import QAStatusFilter, ObservationFilter, QANoteFilter
from axis.qa.api_v3.serializers import (
    QAStatusSerializer,
    BasicQAStatusSerializer,
    ObservationSerializer,
    HIRLQAStatusListSerializer,
    QANoteSerializer,
    QANoteListSerializer,
    CreateQANoteForMultipleQAStatusesSerializer,
    HIRLQAStatusUserFilterBadgesCountSerializer,
)
from axis.qa.models import QAStatus, Observation, QANote, QARequirement


class QAStatusViewSet(viewsets.ModelViewSet):
    model = QAStatus
    permission_classes = (IsAuthenticated,)
    filterset_class = QAStatusFilter
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = QA_STATUS_SEARCH_FIELDS
    ordering = [
        "-created_on",
    ]

    @property
    def ordering_fields(self):
        if self.action == "customer_hirl_list":
            return QA_STATUS_ORDERING_FIELDS + [
                "verifier_name",
            ]
        return QA_STATUS_ORDERING_FIELDS

    def get_queryset(self):
        queryset = self.model.objects.all()

        if self.action == "customer_hirl_list":
            queryset = (
                queryset.filter_by_user(user=self.request.user)
                .annotate_last_state_cycle_time_duration()
                .annotate_customer_hirl_verifier()
                .prefetch_related(
                    "state_history",
                    Prefetch(
                        "home_status__annotations",
                        queryset=Annotation.objects.filter(type__slug="note").select_related(
                            "user", "user__company", "user__company__hirlcompanyclient"
                        ),
                    ),
                )
            )
        else:
            queryset = queryset.filter_by_user(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == "customer_hirl_list":
            return HIRLQAStatusListSerializer
        if self.action == "customer_hirl_user_filter_badges_count":
            return HIRLQAStatusUserFilterBadgesCountSerializer
        if self.request.user.is_superuser:
            return QAStatusSerializer
        return BasicQAStatusSerializer

    @action(
        detail=False,
        methods=[
            "get",
        ],
    )
    def customer_hirl_list(self, request, *args, **kwargs):
        return super(QAStatusViewSet, self).list(request, *args, **kwargs)

    @action(
        detail=False,
        methods=[
            "get",
        ],
    )
    def customer_hirl_user_filter_badges_count(self, request, *args, **kwargs):
        """
        Return special aggregated Count values for different user filters on QA Dashboard list page
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(
            data={
                "all_projects": queryset.count(),
                "my_projects": queryset.filter(qa_designee=self.request.user).count(),
                "rough_qa_projects": queryset.filter(
                    qa_designee=self.request.user,
                    requirement__type=QARequirement.ROUGH_INSPECTION_QA_REQUIREMENT_TYPE,
                ).count(),
                "final_qa_projects": queryset.filter(
                    qa_designee=self.request.user,
                    requirement__type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE,
                ).count(),
                "desktop_audit_projects": queryset.filter(
                    qa_designee=self.request.user,
                    requirement__type=QARequirement.DESKTOP_AUDIT_REQUIREMENT_TYPE,
                ).count(),
                "qa_correction_received_projects": queryset.filter(
                    qa_designee=self.request.user, state="correction_received"
                ).count(),
                "qa_correction_required_projects": queryset.filter(
                    qa_designee=self.request.user, state="correction_required"
                ).count(),
            }
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class ObservationViewSet(viewsets.ReadOnlyModelViewSet):
    model = Observation
    queryset = Observation.objects.all()
    permission_classes = (IsAuthenticated,)
    filterset_class = ObservationFilter
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = OBSERVATION_SEARCH_FIELDS
    ordering_fields = OBSERVATION_ORDERING_FIELDS
    ordering = [
        "-created_on",
    ]

    def get_queryset(self):
        qs = self.model.objects.filter_by_user(self.request.user)
        return qs

    @property
    def serializer_class(self):
        return ObservationSerializer


class QANoteViewSet(viewsets.ModelViewSet):
    model = QANote
    serializer_class = QANoteSerializer
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)
    filterset_class = QANoteFilter
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = QA_NOTE_SEARCH_FIELDS
    ordering_fields = QA_NOTE_ORDERING_FIELDS
    ordering = [
        "-created_on",
    ]

    @action(
        detail=False, methods=["post"], serializer_class=CreateQANoteForMultipleQAStatusesSerializer
    )
    def create_note_for_multiple_qa_statuses(self, request, *args, **kwargs):
        create_serializer = self.get_serializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)

        notes = create_serializer.save()

        serializer = QANoteSerializer(notes, many=True)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class NestedQANoteViewSet(
    NestedViewSetMixin,
    viewsets.GenericViewSet,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.ListModelMixin,
):
    model = QANote
    serializer_class = QANoteSerializer
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)
    filterset_class = QANoteFilter
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = QA_NOTE_SEARCH_FIELDS
    ordering_fields = QA_NOTE_ORDERING_FIELDS
    ordering = [
        "-created_on",
    ]

    def get_queryset(self):
        qs = super(NestedQANoteViewSet, self).get_queryset()
        if self.action == "flat_list":
            qs = qs.prefetch_related("observation_set")
        return qs

    @action(detail=False, methods=["get"], serializer_class=QANoteListSerializer)
    def flat_list(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class QAStatusNestedCustomerDocumentViewSet(NestedCustomerDocumentViewSet):
    def perform_create(self, serializer):
        serializer.save(
            content_type=ContentType.objects.get_for_model(QAStatus),
            object_id=self.get_parents_query_dict().get("object_id"),
            company=self.request.user.company,
        )
