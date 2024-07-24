"""viewsets.py: """

__author__ = "Artem Hruzd"
__date__ = "11/19/2021 7:29 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import django_auto_prefetching
from django.db.models import Count, Q
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend
from axis.core.api_v3.permissions import IsAdminUserOrSuperUserPermission
from axis.core.renderers import BinaryFileRenderer
from axis.customer_hirl.api_v3.permissions import HIRLCompanyAdminMemberPermission
from axis.filehandling.api_v3.serializers import AsynchronousProcessedDocumentSerializer
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.user_management.api_v3 import (
    ACCREDITATION_SEARCH_FIELDS,
    ACCREDITATION_ORDERING_FIELDS,
    INSPECTION_GRADE_SEARCH_FIELDS,
    INSPECTION_GRADE_ORDERING_FIELDS,
)
from axis.user_management.api_v3.filters import AccreditationFilter, InspectionGradeFilter
from axis.user_management.api_v3.serializers import (
    AccreditationSerializer,
    InspectionGradeSerializer,
    InspectionGradeAggregateByLetterGradeSerializer,
    CustomerHIRLInspectionGradeListSerializer,
)
from axis.user_management.tasks import customer_hirl_inspection_grade_quarter_report_task
from axis.user_management.models import Accreditation, InspectionGrade
from axis.user_management.pdf import (
    CustomerHIRLMasterVerifierPDFReport,
    CustomerHIRLNGBS2020PDFReport,
    CustomerHIRLNGBS2015PDFReport,
    CustomerHIRLNGBS2012PDFReport,
    CustomerHIRLWRIVerifierPDFReport,
    CustomerHIRLGreenFieldRepPDFReport,
)
from axis.user_management.tasks import inspection_grade_report_task


class AccreditationViewSet(viewsets.ModelViewSet):
    """
    list:
        Get Accreditations


        Returns accreditations available for user
    create:
        Create Accreditation


        Returns Accreditation
    generate_certificate:
        Generate certificate based on Accreditation name


        Returns pdf certificate
    """

    model = Accreditation
    permission_classes = (IsAuthenticated,)
    queryset = model.objects.all()
    filterset_class = AccreditationFilter
    serializer_class = AccreditationSerializer
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = ACCREDITATION_SEARCH_FIELDS
    ordering_fields = ACCREDITATION_ORDERING_FIELDS

    def get_queryset(self):
        queryset = super(AccreditationViewSet, self).get_queryset()
        return queryset.filter_by_user(user=self.request.user)

    @action(
        detail=True,
        methods=[
            "get",
        ],
        renderer_classes=[
            BinaryFileRenderer,
        ],
    )
    def generate_certificate(self, request, pk):
        accreditation = self.get_object()

        accreditation_cls_map = {
            Accreditation.MASTER_VERIFIER_NAME: CustomerHIRLMasterVerifierPDFReport,
            Accreditation.NGBS_2020_NAME: CustomerHIRLNGBS2020PDFReport,
            Accreditation.NGBS_2015_NAME: CustomerHIRLNGBS2015PDFReport,
            Accreditation.NGBS_2012_NAME: CustomerHIRLNGBS2012PDFReport,
            Accreditation.NGBS_WRI_VERIFIER_NAME: CustomerHIRLWRIVerifierPDFReport,
            Accreditation.NGBS_GREEN_FIELD_REP_NAME: CustomerHIRLGreenFieldRepPDFReport,
        }

        accreditation_cls_map = accreditation_cls_map.get(accreditation.name)

        if not accreditation_cls_map:
            raise ValidationError(
                "Generate certificate is not supported for this accreditation type"
            )

        pdf_report = accreditation_cls_map(accreditation=accreditation)
        pdf_data = pdf_report.generate()

        response = HttpResponse(content_type="application/pdf")
        response.write(pdf_data.read())
        return response


class NestedAccreditationViewSet(
    NestedViewSetMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    model = Accreditation
    permission_classes = (IsAuthenticated,)
    queryset = model.objects.all()
    filterset_class = AccreditationFilter
    serializer_class = AccreditationSerializer
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = ACCREDITATION_SEARCH_FIELDS
    ordering_fields = ACCREDITATION_ORDERING_FIELDS

    def get_queryset(self):
        queryset = super(NestedAccreditationViewSet, self).get_queryset()
        queryset = queryset.filter_by_user(user=self.request.user)
        return django_auto_prefetching.prefetch(queryset, self.get_serializer_class())

    def perform_create(self, serializer):
        serializer.save(trainee_id=self.get_parents_query_dict().get("trainee_id"))


class InspectionGradeViewSet(viewsets.ModelViewSet):
    model = InspectionGrade
    permission_classes = (IsAuthenticated,)
    queryset = model.objects.all()
    filterset_class = InspectionGradeFilter
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = INSPECTION_GRADE_SEARCH_FIELDS
    ordering_fields = INSPECTION_GRADE_ORDERING_FIELDS

    def get_queryset(self):
        queryset = super(InspectionGradeViewSet, self).get_queryset()
        queryset = queryset.filter_by_user(user=self.request.user)
        if self.action == "customer_hirl_list":
            queryset = queryset.select_related(
                "user",
                "user__company",
                "qa_status",
                "qa_status__requirement",
                "qa_status__home_status__eep_program",
                "qa_status__home_status__home",
                "qa_status__home_status__home__geocode_response",
                "qa_status__home_status__home__geocode_response__geocode",
                "qa_status__home_status__home__geocode_response__geocode__raw_city",
                "qa_status__home_status__home__geocode_response__geocode__raw_city__county",
            )
        return django_auto_prefetching.prefetch(queryset, self.get_serializer_class())

    def get_serializer_class(self):
        if self.action == "customer_hirl_list":
            return CustomerHIRLInspectionGradeListSerializer
        if self.action in [
            "create_approver_report",
        ]:
            return AsynchronousProcessedDocumentSerializer
        if self.action == "aggregate_by_letter_grade":
            return InspectionGradeAggregateByLetterGradeSerializer
        return InspectionGradeSerializer

    @action(
        detail=False,
        methods=[
            "get",
        ],
    )
    def customer_hirl_list(self, request, *args, **kwargs):
        return super(InspectionGradeViewSet, self).list(request, *args, **kwargs)

    @action(
        detail=False,
        methods=[
            "get",
        ],
    )
    def aggregate_by_letter_grade(self, request, *args, **kwargs):
        states = {
            "a_grade": Count("letter_grade", filter=Q(letter_grade=InspectionGrade.A_GRADE)),
            "b_grade": Count("letter_grade", filter=Q(letter_grade=InspectionGrade.B_GRADE)),
            "c_grade": Count("letter_grade", filter=Q(letter_grade=InspectionGrade.C_GRADE)),
            "d_grade": Count("letter_grade", filter=Q(letter_grade=InspectionGrade.D_GRADE)),
            "f_grade": Count("letter_grade", filter=Q(letter_grade=InspectionGrade.F_GRADE)),
        }

        result = self.filter_queryset(self.get_queryset()).aggregate(**states)
        serializer = self.get_serializer(data=result)
        serializer.is_valid()
        return Response(serializer.validated_data)

    @action(detail=False, methods=["get"])
    def create_approver_report(self, request, *args, **kwargs):
        inspection_grade_ids = list(
            self.filter_queryset(self.get_queryset()).values_list("id", flat=True)
        )

        async_document = AsynchronousProcessedDocument.objects.create(
            company=self.request.user.company,
            document=None,
            task_name=inspection_grade_report_task.name,
            task_id="",
            download=True,
        )

        inspection_grade_report_task.delay(
            asynchronous_process_document_id=async_document.id,
            inspection_grade_ids=inspection_grade_ids,
            user_id=self.request.user.id,
        )
        async_document_serializer = self.get_serializer(instance=async_document)
        return Response(async_document_serializer.data)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[HIRLCompanyAdminMemberPermission | IsAdminUserOrSuperUserPermission],
    )
    def customer_hirl_inspection_grade_quarter_report(self, request, *args, **kwargs):
        customer_hirl_inspection_grade_quarter_report_task.delay()
        return Response("Task for sending emails successfully started")
