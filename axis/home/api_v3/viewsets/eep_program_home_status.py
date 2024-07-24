"""eep_program_home_status.py - Axis"""

__author__ = "Steven K"
__date__ = "7/16/21 12:23"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
    "Naruhito Kaide",
]

import logging

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, F, Sum
from django.db.models.functions import TruncMonth, Coalesce
from django.http import HttpResponse
from django.utils.functional import cached_property
from hashid_field import Hashid
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from axis.core.api_v3.filters import (
    AxisFilterBackend,
    AxisSearchFilter,
    AxisOrderingFilter,
)
from axis.core.utils import query_params_to_dict
from axis.customer_hirl.api_v3.permissions import HIRLCompanyMemberPermission
from axis.customer_hirl.api_v3.serializers import (
    CustomerHIRLTopStatesStatsSerializer,
    CertificationMetricSerializer,
    CustomerHIRLTopBuilderStatsSerializer,
    HIRLAggregateDashboardSerializer,
    CustomerHIRLTopCompanyStatsSerializer,
    CustomerHIRLTopVerifierStatsSerializer,
)
from axis.customer_hirl.reports.certificate import CustomerHIRLCertificate
from axis.customer_hirl.tasks import customer_hirl_bulk_certificate_task
from axis.filehandling.api_v3.serializers import AsynchronousProcessedDocumentSerializer
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.home.api_v3 import (
    EEP_PROGRAM_HOME_STATUS_SEARCH_FIELDS,
    EEP_PROGRAM_HOME_STATUS_ORDERING_FIELDS,
)
from axis.home.api_v3.filters import (
    EEPProgramHomeStatusFilter,
    CustomerHIRLCertifiedProjectsByMonthMetricsFilter,
)
from axis.home.api_v3.serializers import (
    EEPProgramHomeStatusSerializer,
    BasicEEPProgramHomeStatusSerializer,
    CustomerHIRLCertifiedProjectsByMonthMetricsSerializer,
    CustomerHIRLCertifiedUnitsByMonthMetricsSerializer,
    CustomerHIRLBulkCertificateEEPProgramHomeStatusList,
    CustomerHIRLCertificateLookupListSerializer,
)
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")
User = get_user_model()


class HomeProjectStatusViewSet(viewsets.ModelViewSet):
    """
    Represents Programs attached to homes
    list:
        Return all programs on homes

    hirl_program_stats:
        Return Home Innovations Statistics

    customer_hirl_top_states_stats:
        Return Home Innovations top states for SF and MF(units)

    customer_hirl_top_builder_stats:
        Return Home Innovations top builders for SF and MF(units)

    customer_hirl_top_verifier_stats:
        Return Home Innovations top verifiers

    customer_hirl_top_company_stats:
        Return Home Innovations top companies

    customer_hirl_certified_projects_by_month_metrics:
        Customer HIRL certified Home Statuses by month

    customer_hirl_certified_units_by_month_metrics:
        Customer HIRL certified Units by month

    customer_hirl_bulk_certicate_list:
        Special list for bulk certificate download page

    customer_hirl_certificate_lookup_list:
        Certified project list for lookup search
    """

    model = EEPProgramHomeStatus
    queryset = EEPProgramHomeStatus.objects.order_by("id")
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = EEP_PROGRAM_HOME_STATUS_SEARCH_FIELDS
    ordering_fields = EEP_PROGRAM_HOME_STATUS_ORDERING_FIELDS

    def get_queryset(self):
        queryset = super(HomeProjectStatusViewSet, self).get_queryset()
        if self.action in [
            "hirl_program_stats",
            "customer_hirl_top_states_stats",
            "hirl_aggregate_dashboard_stats",
            "customer_hirl_top_builder_stats",
            "customer_hirl_top_verifier_stats",
            "customer_hirl_top_company_stats",
        ]:
            # do not auto-prefetch
            return queryset.filter(
                eep_program__owner__slug=customer_hirl_app.CUSTOMER_SLUG,
                customer_hirl_project__isnull=False,
            ).annotate_customer_hirl_unit_count()
        elif self.action in [
            "customer_hirl_certified_projects_by_month_metrics",
            "customer_hirl_certified_units_by_month_metrics",
        ]:
            queryset = queryset.filter(eep_program__owner__slug=customer_hirl_app.CUSTOMER_SLUG)
        elif self.action == "customer_hirl_bulk_certicate_list":
            queryset = (
                queryset.filter_by_user(user=self.request.user)
                .filter(state=EEPProgramHomeStatus.COMPLETE_STATE)
                .annotate_customer_hirl_legacy_project_id()
            )
        elif self.action == "customer_hirl_certificate_lookup_list":
            queryset = queryset.filter(
                eep_program__owner__slug=customer_hirl_app.CUSTOMER_SLUG,
                certification_date__isnull=False,
            ).annotate_customer_hirl_certification_level()

        else:
            queryset = queryset.filter_by_user(user=self.request.user)
        return queryset

    @cached_property
    def permission_classes(self):
        if self.action in [
            "certificate",
            "customer_hirl_homes_report",
        ]:
            return (AllowAny,)

        if self.action in [
            "hirl_program_stats",
            "customer_hirl_top_states_stats",
            "customer_hirl_certified_projects_by_month_metrics",
            "customer_hirl_certified_units_by_month_metrics",
        ]:
            return (HIRLCompanyMemberPermission,)
        return (IsAuthenticated,)

    @property
    def filterset_class(self):
        if self.action in [
            "customer_hirl_certified_projects_by_month_metrics",
            "customer_hirl_certified_units_by_month_metrics",
        ]:
            return CustomerHIRLCertifiedProjectsByMonthMetricsFilter
        return EEPProgramHomeStatusFilter

    def get_serializer_class(self):
        if self.action == "hirl_program_stats":
            return CertificationMetricSerializer
        if self.action == "hirl_aggregate_dashboard_stats":
            return HIRLAggregateDashboardSerializer
        if self.action == "customer_hirl_top_states_stats":
            return CustomerHIRLTopStatesStatsSerializer
        if self.action == "customer_hirl_top_builder_stats":
            return CustomerHIRLTopBuilderStatsSerializer
        if self.action == "customer_hirl_certified_projects_by_month_metrics":
            return CustomerHIRLCertifiedProjectsByMonthMetricsSerializer
        if self.action == "customer_hirl_certified_units_by_month_metrics":
            return CustomerHIRLCertifiedUnitsByMonthMetricsSerializer
        if self.action == "customer_hirl_bulk_certicate_list":
            return CustomerHIRLBulkCertificateEEPProgramHomeStatusList
        if self.action == "customer_hirl_certificate_lookup_list":
            return CustomerHIRLCertificateLookupListSerializer
        if self.action == "bulk_certificate_download":
            return AsynchronousProcessedDocumentSerializer
        if self.request.user.is_superuser:
            return EEPProgramHomeStatusSerializer
        return BasicEEPProgramHomeStatusSerializer

    @action(detail=False, pagination_class=None)
    def hirl_program_stats(self, request, *args, **kwargs):
        """
        Returns a table of homes that are certified / in progress by Home Innovations groups
        """
        serializer = self.get_serializer_class()(self.filter_queryset(self.get_queryset()))
        return Response(serializer.data)

    @action(detail=False, pagination_class=None)
    def hirl_aggregate_dashboard_stats(self, request, *args, **kwargs):
        """
        Returns aggregated results for different HIRL stats
        """
        serializer = self.get_serializer_class()(self.filter_queryset(self.get_queryset()))
        return Response(serializer.data)

    @action(detail=False, pagination_class=None)
    def customer_hirl_top_states_stats(self, request, *args, **kwargs):
        """
        Return top states statistics for different Customer HIRL projects
        """
        serializer = self.get_serializer_class()(self.filter_queryset(self.get_queryset()))
        return Response(serializer.data)

    @action(detail=False, pagination_class=None)
    def customer_hirl_top_builder_stats(self, request, *args, **kwargs):
        """
        Return top builder statistics for different Customer HIRL projects
        """
        serializer = self.get_serializer_class()(self.filter_queryset(self.get_queryset()))
        return Response(serializer.data)

    @action(
        detail=False, pagination_class=None, serializer_class=CustomerHIRLTopVerifierStatsSerializer
    )
    def customer_hirl_top_verifier_stats(self, request, *args, **kwargs):
        """
        Return top verifier statistics for different Customer HIRL projects
        """
        serializer = self.serializer_class(self.filter_queryset(self.get_queryset()))
        return Response(serializer.data)

    @action(
        detail=False, pagination_class=None, serializer_class=CustomerHIRLTopCompanyStatsSerializer
    )
    def customer_hirl_top_company_stats(self, request, *args, **kwargs):
        """
        Return top company statistics for different Customer HIRL projects
        """
        serializer = self.serializer_class(self.filter_queryset(self.get_queryset()))
        return Response(serializer.data)

    @action(detail=False, pagination_class=None)
    def customer_hirl_homes_report(self, request, *args, **kwargs):
        customer_document = (
            AsynchronousProcessedDocument.objects.filter(
                task_name="customer_hirl_homes_report_task"
            )
            .order_by("-created_date")
            .first()
        )

        if customer_document:
            filename = "homes_list_{}.xlsx".format(
                customer_document.created_date.strftime("%Y%m%d")
            )

            response = HttpResponse(
                content=customer_document.document.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = "attachment; filename={}".format(filename)
            return response
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
    )
    def customer_hirl_certified_projects_by_month_metrics(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        qs = (
            qs.annotate(
                certification_date_month=TruncMonth("certification_date"),
            )
            .values("certification_date_month")
            .annotate(home_status_count=Count("id"))
            .values(
                "certification_date_month",
                "home_status_count",
            )
            .order_by("-certification_date_month")
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
    )
    def customer_hirl_certified_units_by_month_metrics(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        qs = (
            qs.annotate(
                certification_date_month=TruncMonth("certification_date"),
            )
            .values("certification_date_month")
            .annotate(home_status_count=Count("id"))
            .annotate(
                units_count=Coalesce(Sum("customer_hirl_project__number_of_units"), 0)
                + F("home_status_count")
            )
            .order_by("-certification_date_month")
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=[
            "get",
        ],
    )
    def customer_hirl_bulk_certicate_list(self, request, *args, **kwargs):
        return super(HomeProjectStatusViewSet, self).list(request, *args, **kwargs)

    @action(
        detail=False,
        methods=[
            "get",
        ],
        permission_classes=[AllowAny],
    )
    def customer_hirl_certificate_lookup_list(self, request, *args, **kwargs):
        return super(HomeProjectStatusViewSet, self).list(request, *args, **kwargs)

    @action(
        detail=False,
    )
    def bulk_certificate_download(self, request, *args, **kwargs):
        async_document = AsynchronousProcessedDocument.objects.create(
            company=self.request.user.company,
            document=None,
            task_name=customer_hirl_bulk_certificate_task.name,
            task_id="",
            download=True,
        )

        customer_hirl_bulk_certificate_task.delay(
            user_id=self.request.user.id,
            result_object_id=async_document.id,
            query_params=query_params_to_dict(self.request.query_params),
        )
        async_document_serializer = self.get_serializer(instance=async_document)
        return Response(async_document_serializer.data)

    @action(
        detail=True,
        methods=[
            "get",
        ],
        url_path="certificate/(?P<shared_by>[^/.]+)",
    )
    def certificate(self, request, pk=None, shared_by=None):
        """Return download-type response of the rendered pdf."""
        integer_cert_id = Hashid(pk, salt=f"certificate{settings.HASHID_FIELD_SALT}")
        integer_user_id = Hashid(shared_by, salt=f"user{settings.HASHID_FIELD_SALT}")
        home_status_object = EEPProgramHomeStatus.objects.get(id=integer_cert_id)
        user = User.objects.get(id=integer_user_id)
        customer_hirl_certificate = CustomerHIRLCertificate(
            home_status=home_status_object, user=user
        )
        output_stream = customer_hirl_certificate.generate()

        response = HttpResponse(content_type="application/pdf")
        response.write(output_stream.read())
        return response


class NestedEEPProgramHomeStatusViewSet(
    NestedViewSetMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    model = EEPProgramHomeStatus
    permission_classes = (IsAuthenticated,)
    queryset = EEPProgramHomeStatus.objects.all()
    filterset_class = EEPProgramHomeStatusFilter
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = EEP_PROGRAM_HOME_STATUS_SEARCH_FIELDS
    ordering_fields = EEP_PROGRAM_HOME_STATUS_ORDERING_FIELDS

    def get_queryset(self):
        queryset = super(NestedEEPProgramHomeStatusViewSet, self).get_queryset()
        # TODO: this query slows down even swagger
        return queryset.filter_by_user(user=self.request.user)

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return EEPProgramHomeStatusSerializer
        return BasicEEPProgramHomeStatusSerializer
