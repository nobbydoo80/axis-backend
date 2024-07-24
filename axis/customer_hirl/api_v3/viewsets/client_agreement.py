__author__ = "Artem Hruzd"
__date__ = "10/10/2021 11:40 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import django_auto_prefetching
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django_fsm import can_proceed, has_transition_perm
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from axis.annotation.api_v3.viewsets.annotation import NestedAnnotationViewSet
from axis.company.api_v3.permissions import RaterCompanyMemberPermission
from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend
from axis.core.api_v3.mixins import get_viewset_transition_action_mixin
from axis.core.api_v3.permissions import IsAdminUserOrSuperUserPermission
from axis.core.api_v3.viewsets import NestedHistoryViewSet
from axis.customer_hirl.builder_agreements.messages.owner import NewBuilderEnrollmentMessage
from axis.customer_hirl.api_v3 import (
    CLIENT_AGREEMENT_SEARCH_FIELDS,
    CLIENT_AGREEMENT_ORDERING_FIELDS,
)
from axis.customer_hirl.api_v3.filters import ClientAgreementFilter
from axis.customer_hirl.api_v3.permissions import (
    HIRLCompanyMemberPermission,
    HIRLClientAgreementDeletePermission,
    HIRLClientAgreementEditPermission,
)
from axis.customer_hirl.api_v3.serializers import (
    ClientAgreementSerializer,
    CreateClientAgreementWithoutDocuSignSerializer,
    CreateClientAgreementWithoutUserSerializer,
    ClientAgreementForceStateSerializer,
)
from axis.customer_hirl.tasks import (
    post_agreement_for_builder_signing_task,
    update_extension_request_signed_status_from_docusign_task,
    update_countersigned_extension_request_agreement_status_from_docusign_task,
)
from axis.customer_hirl.models import BuilderAgreement
from django.apps import apps
from axis.customer_hirl.tasks import (
    update_countersigned_status_from_docusign_task,
    update_signed_status_from_docusign_task,
)

from axis.filehandling.api_v3.viewsets import NestedCustomerDocumentViewSet

customer_hirl_app = apps.get_app_config("customer_hirl")


class ClientAgreementViewSet(
    viewsets.ModelViewSet,
    get_viewset_transition_action_mixin(model=BuilderAgreement, field_name="state"),
    get_viewset_transition_action_mixin(
        model=BuilderAgreement, field_name="extension_request_state"
    ),
):
    model = BuilderAgreement
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)
    filterset_class = ClientAgreementFilter
    serializer_class = ClientAgreementSerializer
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = CLIENT_AGREEMENT_SEARCH_FIELDS
    ordering_fields = CLIENT_AGREEMENT_ORDERING_FIELDS

    def get_permissions(self):
        if self.action == "update":
            return [
                HIRLClientAgreementEditPermission(),
            ]
        if self.action == "delete":
            return [
                HIRLClientAgreementDeletePermission(),
            ]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super(ClientAgreementViewSet, self).get_queryset()
        queryset = queryset.filter_by_user(user=self.request.user)
        return django_auto_prefetching.prefetch(
            queryset,
            self.get_serializer_class(),
            # exclude duplicate JOINs
            excluded_fields=[
                "shipping_geocode__raw_city__county__climate_zone",
                "owner__shipping_geocode__raw_city__county__climate_zone",
                "mailing_geocode__raw_city__county__climate_zone",
                "mailing_geocode__raw_city__country",
                "shipping_geocode__raw_city__country",
                "certifying_document__company",
                "signed_agreement__company",
                "extension_request_certifying_document__company",
                "extension_request_signed_agreement__company",
                "data",
            ],
        )

    def perform_create(self, serializer):
        client_agreement = serializer.save(
            owner=customer_hirl_app.get_customer_hirl_provider_organization(),
            company=self.request.user.company,
            created_by=self.request.user,
        )

        customer_document = client_agreement.generate_unsigned_customer_document()
        post_agreement_for_builder_signing_task.delay(
            agreement_id=client_agreement.id, customer_document_id=customer_document.id
        )

        url = client_agreement.get_absolute_url()

        NewBuilderEnrollmentMessage(url=url).send(
            company=client_agreement.owner,
            context={
                "company": client_agreement.company,
                "url": url,
                "list_url": reverse("hirl:agreements:list"),
            },
        )

    @action(
        detail=False,
        methods=["post"],
        permission_classes=(HIRLCompanyMemberPermission | RaterCompanyMemberPermission,),
    )
    def create_without_docusign(self, request, *args, **kwargs):
        serializer = CreateClientAgreementWithoutDocuSignSerializer(
            data=request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        client_agreement = serializer.save(
            owner=customer_hirl_app.get_customer_hirl_provider_organization(),
        )

        client_agreement_serializer = self.get_serializer(client_agreement)

        headers = self.get_success_headers(client_agreement_serializer.data)
        return Response(
            client_agreement_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(
        detail=False,
        methods=["post"],
        permission_classes=(HIRLCompanyMemberPermission | RaterCompanyMemberPermission,),
    )
    def create_without_user(self, request, *args, **kwargs):
        from axis.customer_hirl.tasks import post_agreement_for_builder_signing_task

        serializer = CreateClientAgreementWithoutUserSerializer(
            data=request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        client_agreement = serializer.save(
            owner=customer_hirl_app.get_customer_hirl_provider_organization(),
        )

        client_agreement_serializer = self.get_serializer(client_agreement)

        customer_document = serializer.instance.generate_unsigned_customer_document()
        post_agreement_for_builder_signing_task.delay(
            agreement_id=serializer.instance.id, customer_document_id=customer_document.id
        )

        headers = self.get_success_headers(client_agreement_serializer.data)
        return Response(
            client_agreement_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[
            HIRLClientAgreementEditPermission,
        ],
    )
    def resend_docusign_email(self, request, *args, **kwargs):
        ca = self.get_object()
        return Response(ca.resend_docusign_email())

    @action(detail=True, methods=["post"])
    def update_docusign_status(self, *args, **kwargs):
        """Get the status from docusign"""

        client_agreement = self.get_object()

        update_signed_status_from_docusign_task(client_agreement.pk)
        update_countersigned_status_from_docusign_task(client_agreement.pk)
        update_extension_request_signed_status_from_docusign_task(client_agreement.pk)
        update_countersigned_extension_request_agreement_status_from_docusign_task(
            client_agreement.pk
        )

        return super().retrieve(*args, **kwargs)

    @swagger_auto_schema(
        responses={"200": ClientAgreementSerializer},
    )
    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[
            HIRLCompanyMemberPermission | IsAdminUserOrSuperUserPermission,
        ],
        serializer_class=ClientAgreementForceStateSerializer,
    )
    def force_state(self, request, **kwargs):
        """
        Manually change Client Agreement state without any side effects
        :param request:
        :param kwargs:
        :return:
        """
        super().partial_update(request, **kwargs)
        instance = self.get_object()
        serializer = ClientAgreementSerializer(instance, context=self.get_serializer_context())
        return Response(serializer.data)

    @action(
        detail=True,
        methods=[
            "post",
        ],
    )
    def reject_extension_request(self, request, *args, **kwargs):
        client_agreement = self.get_object()
        transition_method = getattr(client_agreement, "reject_extension_request")

        if not can_proceed(transition_method):
            raise PermissionDenied("You cannot move to this state")

        if not has_transition_perm(transition_method, request.user):
            raise PermissionDenied("You do not have permission to move to this state")

        reason = self.request.data.get("reason")
        if not reason:
            reason = ""
        transition_method(reason=reason)
        client_agreement.save()
        serializer = self.get_serializer(client_agreement)
        return Response(serializer.data)


class ClientAgreementNestedCustomerDocumentViewSet(NestedCustomerDocumentViewSet):
    def get_queryset(self):
        return (
            super(ClientAgreementNestedCustomerDocumentViewSet, self)
            .get_queryset()
            .filter(content_type=ContentType.objects.get_for_model(BuilderAgreement))
            .filter_by_user(self.request.user, include_public=True)
            .order_by("-pk")
        )

    def perform_create(self, serializer):
        serializer.save(
            content_type=ContentType.objects.get_for_model(BuilderAgreement),
            object_id=self.get_parents_query_dict().get("object_id"),
            company=self.request.user.company,
        )


class ClientAgreementNestedHistoryViewSet(NestedHistoryViewSet):
    model = BuilderAgreement.history.model
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = CLIENT_AGREEMENT_SEARCH_FIELDS
    ordering_fields = CLIENT_AGREEMENT_ORDERING_FIELDS


class ClientAgreementAnnotationViewSet(NestedAnnotationViewSet):
    parent_model = BuilderAgreement
