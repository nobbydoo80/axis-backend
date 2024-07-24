"""verifier_agreement.py: """

__author__ = "Artem Hruzd"
__date__ = "03/23/2022 17:33"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import django_auto_prefetching
from django.apps import apps
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from axis.company.api_v3.permissions import RaterCompanyMemberPermission
from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend
from axis.core.api_v3.permissions import IsAdminUserOrSuperUserPermission
from axis.customer_hirl.api_v3 import (
    VERIFIER_AGREEMENT_SEARCH_FIELDS,
    VERIFIER_AGREEMENT_ORDERING_FIELDS,
)
from axis.customer_hirl.api_v3.filters import VerifierAgreementFilter
from axis.customer_hirl.api_v3.permissions import (
    HIRLCompanyMemberPermission,
    HIRLVerifierAgreementUpdatePermission,
    HIRLVerifierAgreementDeletePermission,
)
from axis.customer_hirl.api_v3.serializers import (
    VerifierAgreementSerializer,
)
from axis.customer_hirl.models import VerifierAgreement

customer_hirl_app = apps.get_app_config("customer_hirl")


class VerifierAgreementViewSet(viewsets.ModelViewSet):
    model = VerifierAgreement
    queryset = model.objects.all()
    filterset_class = VerifierAgreementFilter
    serializer_class = VerifierAgreementSerializer
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = VERIFIER_AGREEMENT_SEARCH_FIELDS
    ordering_fields = VERIFIER_AGREEMENT_ORDERING_FIELDS

    @property
    def permission_classes(self):
        if self.action == "create":
            return (RaterCompanyMemberPermission,)
        if self.action in ["update", "partial_update"]:
            return (HIRLVerifierAgreementUpdatePermission,)
        if self.action == "destroy":
            return (HIRLVerifierAgreementDeletePermission,)
        if self.action == "resend_docusign_email":
            return (HIRLCompanyMemberPermission | IsAdminUserOrSuperUserPermission,)
        return (
            HIRLCompanyMemberPermission
            | RaterCompanyMemberPermission
            | IsAdminUserOrSuperUserPermission,
        )

    def get_queryset(self):
        queryset = super(VerifierAgreementViewSet, self).get_queryset()
        return django_auto_prefetching.prefetch(queryset, self.get_serializer_class())

    def perform_create(self, serializer):
        serializer.save(owner=customer_hirl_app.get_customer_hirl_provider_organization())

    @action(detail=True, methods=["POST"])
    def resend_docusign_email(self, request, *args, **kwargs):
        va = self.get_object()
        return Response(va.resend_docusign_email())


class NestedVerifierAgreementViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    Verifier Agreements

    list:
        List of verifier agreements
    """

    model = VerifierAgreement
    permission_classes = (IsAuthenticated,)
    queryset = model.objects.all()
    filter_class = VerifierAgreementFilter
    serializer_class = VerifierAgreementSerializer
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = VERIFIER_AGREEMENT_SEARCH_FIELDS
    ordering_fields = VERIFIER_AGREEMENT_ORDERING_FIELDS

    def get_queryset(self):
        queryset = super(NestedVerifierAgreementViewSet, self).get_queryset()
        return django_auto_prefetching.prefetch(queryset, self.get_serializer_class())
