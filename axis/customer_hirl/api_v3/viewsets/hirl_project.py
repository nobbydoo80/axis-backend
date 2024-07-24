"""hirl_project.py: """

__author__ = "Artem Hruzd"
__date__ = "04/22/2021 17:00"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import logging

import django_auto_prefetching
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.db.models import F, Func, Count, DateField, IntegerField, ExpressionWrapper, Q
from django.db.models.functions import TruncDay, Cast
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_extensions.mixins import NestedViewSetMixin

from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend
from axis.core.api_v3.viewsets import NestedHistoryViewSet
from axis.core.utils import query_params_to_dict
from axis.customer_hirl.api_v3 import HIRL_PROJECT_SEARCH_FIELDS, HIRL_PROJECT_ORDERING_FIELDS
from axis.customer_hirl.api_v3.filters import HIRLProjectFilter, HIRLProjectCycleTimeMetricsFilter
from axis.customer_hirl.api_v3.permissions import (
    HIRLProjectUpdatePermission,
    HIRLProjectViewPermission,
    HIRLCompanyMemberPermission,
    HIRLProjectDeletePermission,
    HIRLProjectCreatePermission,
)
from axis.customer_hirl.api_v3.serializers import (
    HIRLProjectSerializer,
    BasicHIRLProjectSerializer,
    HIRLGreenEnergyBadgeSerializer,
    HIRLProjectAddressIsUniqueRequestDataSerializer,
    GreenPaymentsImportSerializer,
    ProjectBillingImportSerializer,
    HIRLProjectAddMFSerializer,
    BillingRuleExportQueryParamsSerializer,
    MilestoneExportQueryParamsSerializer,
    ProjectCycleTimeMetricsSerializer,
    VerificationReportUploadSerializer,
    HIRLProjectAddSFSerializer,
)
from axis.customer_hirl.messages.project import (
    MultiFamilyProjectCreatedHIRLNotificationMessage,
    IsAppealsHIRLProjectCreatedNotificationMessage,
    SingleFamilyProjectCreatedHIRLNotificationMessage,
)
from axis.customer_hirl.models import HIRLProject, HIRLProjectRegistration
from axis.customer_hirl.tasks import (
    billing_rule_export_task,
    milestone_export_task,
    customer_hirl_all_projects_report_task,
)
from axis.customer_hirl.utils import hirl_project_address_is_unique
from axis.filehandling.api_v3.serializers import AsynchronousProcessedDocumentSerializer
from axis.filehandling.models import AsynchronousProcessedDocument

User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")
log = logging.getLogger(__name__)


class HIRLProjectViewSet(viewsets.ModelViewSet):
    """
    billing_rule_export:
        Creates a Billing Rule file for JAMIS system
    milestone:
        Creates a Milestone file for JAMIS system
    """

    model = HIRLProject
    queryset = model.objects.all()
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = HIRL_PROJECT_SEARCH_FIELDS
    ordering_fields = HIRL_PROJECT_ORDERING_FIELDS

    def get_queryset(self):
        queryset = super(HIRLProjectViewSet, self).get_queryset()
        # billing info annotation is too heavy, add it only for single object
        if self.action in [
            "retrieve",
        ]:
            queryset = queryset.annotate_billing_info()

        queryset = queryset.filter_by_user(user=self.request.user)
        return django_auto_prefetching.prefetch(queryset, self.get_serializer_class())

    @property
    def filterset_class(self):
        if self.action == "project_cycle_time_metrics":
            return HIRLProjectCycleTimeMetricsFilter
        return HIRLProjectFilter

    @property
    def permission_classes(self):
        if self.action in ["create", "create_bulk"]:
            return (HIRLProjectCreatePermission,)
        if self.action in [
            "list",
            "retrieve",
        ]:
            return (HIRLProjectViewPermission,)
        if self.action in ["update", "partial_update"]:
            return (HIRLProjectUpdatePermission,)
        if self.action in [
            "destroy",
        ]:
            return (HIRLProjectDeletePermission,)
        if self.action in [
            "approve",
        ]:
            return (HIRLCompanyMemberPermission,)
        if self.action in [
            "billing_rule_export",
            "milestone_export",
            "green_payments_import",
            "project_billing_import",
            "all_projects_report",
            "project_cycle_time_metrics",
        ]:
            return (HIRLCompanyMemberPermission,)
        return (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "green_energy_badges":
            return HIRLGreenEnergyBadgeSerializer
        if self.action in [
            "green_payments_import",
            "project_billing_import",
            "billing_rule_export",
            "milestone_export",
            "all_projects_report",
            "verification_report_upload",
        ]:
            return AsynchronousProcessedDocumentSerializer
        if self.action == "project_cycle_time_metrics":
            return ProjectCycleTimeMetricsSerializer
        if self.request.user.is_authenticated and (
            self.request.user.is_superuser or self.request.user.is_customer_hirl_company_member()
        ):
            return HIRLProjectSerializer
        return BasicHIRLProjectSerializer

    @action(detail=True)
    def green_energy_badges(self, request, *args, **kwargs):
        green_energy_badges = self.get_object().green_energy_badges.all()
        serializer = self.get_serializer(green_energy_badges, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=HIRLProjectAddressIsUniqueRequestDataSerializer, responses={200: "Boolean"}
    )
    @action(
        detail=False,
        methods=[
            "POST",
        ],
        filter_backends=[],
        pagination_class=None,
        serializer_class=HIRLProjectAddressIsUniqueRequestDataSerializer,
    )
    def project_address_is_unique(self, request, *args, **kwargs):
        data_serializer = HIRLProjectAddressIsUniqueRequestDataSerializer(data=self.request.data)
        data_serializer.is_valid(raise_exception=True)

        is_unique = hirl_project_address_is_unique(
            street_line1=data_serializer.validated_data["street_line1"],
            street_line2=data_serializer.validated_data["street_line2"],
            project_type=data_serializer.validated_data["is_multi_family"],
            city=data_serializer.validated_data["city"],
            zipcode=data_serializer.validated_data["zipcode"],
            geocode_response=data_serializer.validated_data["geocode_response"],
            project=data_serializer.validated_data["project"],
        )

        if not is_unique:
            return Response(False)
        return Response(True)

    @action(detail=False, methods=["get"])
    def billing_rule_export(self, request, *args, **kwargs):
        query_params_serializer = BillingRuleExportQueryParamsSerializer(
            data=query_params_to_dict(self.request.query_params)
        )
        query_params_serializer.is_valid(raise_exception=True)

        async_document = AsynchronousProcessedDocument.objects.create(
            company=self.request.user.company,
            document=None,
            task_name=billing_rule_export_task.name,
            task_id="",
            download=True,
        )

        billing_rule_export_task.delay(
            user_id=self.request.user.id,
            result_object_id=async_document.id,
            start_date=str(query_params_serializer.validated_data["start_date"]),
            end_date=str(query_params_serializer.validated_data["end_date"]),
            program_slugs=query_params_serializer.validated_data["program_slugs"],
        )
        async_document_serializer = self.get_serializer(instance=async_document)
        return Response(async_document_serializer.data)

    @action(detail=False, methods=["get"])
    def milestone_export(self, request, *args, **kwargs):
        query_params_serializer = MilestoneExportQueryParamsSerializer(
            data=query_params_to_dict(self.request.query_params)
        )
        query_params_serializer.is_valid(raise_exception=True)

        async_document = AsynchronousProcessedDocument.objects.create(
            company=self.request.user.company,
            document=None,
            task_name=milestone_export_task.name,
            task_id="",
            download=True,
        )

        milestone_export_task.delay(
            user_id=self.request.user.id,
            result_object_id=async_document.id,
            start_date=str(query_params_serializer.validated_data["start_date"]),
            end_date=str(query_params_serializer.validated_data["end_date"]),
            program_slugs=query_params_serializer.validated_data["program_slugs"],
        )
        async_document_serializer = self.get_serializer(instance=async_document)
        return Response(async_document_serializer.data)

    @transaction.atomic
    @action(
        detail=False,
        methods=["post"],
        parser_classes=[
            MultiPartParser,
        ],
    )
    def green_payments_import(self, request, *args, **kwargs):
        serializer = GreenPaymentsImportSerializer(
            data=request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        async_document = serializer.create(validated_data=serializer.validated_data)

        async_document_serializer = self.get_serializer(instance=async_document)
        return Response(async_document_serializer.data)

    @transaction.atomic
    @action(
        detail=False,
        methods=["post"],
        parser_classes=[
            MultiPartParser,
        ],
    )
    def project_billing_import(self, request, *args, **kwargs):
        serializer = ProjectBillingImportSerializer(
            data=request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        async_document = serializer.create(validated_data=serializer.validated_data)

        async_document_serializer = self.get_serializer(instance=async_document)
        return Response(async_document_serializer.data)

    @action(
        detail=False,
    )
    def all_projects_report(self, request, *args, **kwargs):
        async_document = AsynchronousProcessedDocument.objects.create(
            company=self.request.user.company,
            document=None,
            task_name=customer_hirl_all_projects_report_task.name,
            task_id="",
            download=True,
        )

        customer_hirl_all_projects_report_task.delay(
            user_id=self.request.user.id,
            result_object_id=async_document.id,
            query_params=query_params_to_dict(self.request.query_params),
        )
        async_document_serializer = self.get_serializer(instance=async_document)
        return Response(async_document_serializer.data)

    @action(
        detail=False,
    )
    def project_cycle_time_metrics(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        qs = (
            qs.annotate(
                registration_date_day=TruncDay("created_at"),
                certification_date_day=TruncDay("home_status__certification_date"),
                cycle_time=Func(
                    F("certification_date_day")
                    - Cast("registration_date_day", output_field=DateField()),
                    function="ABS",
                    output_field=IntegerField(),
                ),
                # in SQLite and cannot use ExtractDay, but you can use microseconds
                # and convert them manually to days by dividing by 86400000000
                cycle_days=ExpressionWrapper(
                    F("cycle_time") / 86400000000, output_field=IntegerField()
                ),
            )
            .values("cycle_days")
            .annotate(projects_count=Count("id"))
            .values("cycle_days", "projects_count")
            .order_by("-cycle_days")
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @transaction.atomic
    @action(
        detail=False,
        methods=["post"],
        parser_classes=[
            MultiPartParser,
        ],
    )
    def verification_report_upload(self, request, *args, **kwargs):
        serializer = VerificationReportUploadSerializer(
            data=request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        async_document = serializer.save()

        async_document_serializer = self.get_serializer(instance=async_document)
        return Response(async_document_serializer.data)


class HIRLProjectNestedViewSet(
    NestedViewSetMixin, viewsets.mixins.ListModelMixin, viewsets.GenericViewSet
):
    model = HIRLProject
    serializer_class = BasicHIRLProjectSerializer
    queryset = model.objects.all()
    filterset_class = HIRLProjectFilter
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = HIRL_PROJECT_SEARCH_FIELDS
    ordering_fields = HIRL_PROJECT_ORDERING_FIELDS

    def get_queryset(self):
        queryset = super(HIRLProjectNestedViewSet, self).get_queryset()
        queryset = queryset.filter_by_user(user=self.request.user)
        return django_auto_prefetching.prefetch(queryset, self.get_serializer_class())

    @property
    def permission_classes(self):
        return (HIRLProjectViewPermission,)

    def get_serializer_class(self):
        if self.request.user.is_superuser or self.request.user.is_customer_hirl_company_member():
            return HIRLProjectSerializer
        return super(HIRLProjectNestedViewSet, self).get_serializer_class()

    def _get_registration(self) -> HIRLProjectRegistration:
        registration = get_object_or_404(
            HIRLProjectRegistration,
            ~Q(state=HIRLProjectRegistration.REJECTED_STATE),
            id=self.get_parents_query_dict().get("registration_id"),
        )
        return registration

    @action(detail=False, methods=["post"])
    def create_single_family(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = HIRLProjectAddSFSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            registration = self._get_registration()
            projects = serializer.save(registration=registration)
        hirl_company = customer_hirl_app.get_customer_hirl_provider_organization()

        notify_users = User.objects.filter(
            company__in=[hirl_company, registration.registration_user.company]
        )
        for project in projects:
            SingleFamilyProjectCreatedHIRLNotificationMessage().send(
                users=notify_users,
                context={
                    "url": project.get_absolute_url(),
                    "verifier": registration.registration_user,
                    "project_address": f"{project.home_address_geocode.raw_address}",
                    "project": project,
                    "site": get_current_site(self.request),
                },
            )

        projects_serializer = self.get_serializer(projects, many=True)
        headers = self.get_success_headers(projects_serializer.data)
        return Response(projects_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=["post"])
    def create_multi_family(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = HIRLProjectAddMFSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            registration = self._get_registration()
            projects = serializer.save(registration=registration)
        hirl_company = customer_hirl_app.get_customer_hirl_provider_organization()

        notify_users = User.objects.filter(
            company__in=[hirl_company, registration.registration_user.company]
        )
        for project in projects:
            MultiFamilyProjectCreatedHIRLNotificationMessage().send(
                users=notify_users,
                context={
                    "url": project.get_absolute_url(),
                    "verifier": registration.registration_user,
                    "project_address": f"{project.home_address_geocode.raw_address}",
                    "project": project,
                    "site": get_current_site(self.request),
                },
            )
            if project.is_appeals_project:
                IsAppealsHIRLProjectCreatedNotificationMessage().send(
                    company=hirl_company,
                    context={
                        "url": project.get_absolute_url(),
                        "verifier": registration.registration_user,
                        "project_address": f"{project.home_address_geocode.raw_address}",
                        "h_number": project.h_number,
                        "project": project,
                        "site": get_current_site(self.request),
                    },
                )

        projects_serializer = self.get_serializer(projects, many=True)
        headers = self.get_success_headers(projects_serializer.data)
        return Response(projects_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_success_headers(self, data):
        try:
            return {"Location": str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class HIRLProjectNestedHistoryViewSet(NestedHistoryViewSet):
    model = HIRLProject.history.model
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = HIRL_PROJECT_SEARCH_FIELDS
    ordering_fields = HIRL_PROJECT_ORDERING_FIELDS

    def filter_queryset_by_parents_lookups(self, queryset):
        """History Model do not support HashidAutoField"""
        parents_query_dict = self.get_parents_query_dict()
        if parents_query_dict:
            try:
                project_ids = HIRLProject.objects.filter(**parents_query_dict).values_list(
                    "id", flat=True
                )
                return queryset.filter(id__in=project_ids)
            except ValueError:
                raise Http404
        else:
            return queryset
