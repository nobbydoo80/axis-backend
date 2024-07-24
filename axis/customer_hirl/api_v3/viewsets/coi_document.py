__author__ = "Artem Hruzd"
__date__ = "04/22/2021 17:01"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from rest_framework import viewsets
from django.apps import apps
from rest_framework.permissions import IsAuthenticated
from rest_framework_extensions.mixins import NestedViewSetMixin

from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend
from axis.core.api_v3.viewsets import NestedHistoryViewSet
from axis.customer_hirl.api_v3 import COI_DOCUMENT_SEARCH_FIELDS, COI_DOCUMENT_ORDERING_FIELDS
from axis.customer_hirl.api_v3.filters import COIDocumentFilter
from axis.customer_hirl.api_v3.serializers import COIDocumentSerializer, ClientCOIDocumentSerializer
from axis.customer_hirl.models import COIDocument


customer_hirl_app = apps.get_app_config("customer_hirl")


class COIDocumentViewSet(
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    model = COIDocument
    permission_classes = (IsAuthenticated,)
    queryset = model.objects.all()
    filterset_class = COIDocumentFilter
    serializer_class = COIDocumentSerializer
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = COI_DOCUMENT_SEARCH_FIELDS
    ordering_fields = COI_DOCUMENT_ORDERING_FIELDS

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter_by_user(user=self.request.user)

    def get_serializer_class(self):
        if self.request.user.company and (
            self.request.user.company.slug == customer_hirl_app.CUSTOMER_SLUG
            or self.request.user.is_superuser
        ):
            return COIDocumentSerializer

        return ClientCOIDocumentSerializer


class NestedCOIDocumentViewSet(
    NestedViewSetMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    model = COIDocument
    permission_classes = (IsAuthenticated,)
    queryset = model.objects.all()
    filter_class = COIDocumentFilter
    serializer_class = COIDocumentSerializer
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = COI_DOCUMENT_SEARCH_FIELDS
    ordering_fields = COI_DOCUMENT_ORDERING_FIELDS

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter_by_user(user=self.request.user)

    def get_serializer_class(self):
        if (
            self.request.user.is_authenticated
            and self.request.user.company
            and self.request.user.company.slug != customer_hirl_app.CUSTOMER_SLUG
        ):
            return ClientCOIDocumentSerializer

        return COIDocumentSerializer

    def perform_create(self, serializer):
        serializer.save(company_id=self.get_parents_query_dict().get("company_id"))


class COIDocumentNestedHistoryViewSet(NestedHistoryViewSet):
    model = COIDocument.history.model
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = COI_DOCUMENT_SEARCH_FIELDS
    ordering_fields = COI_DOCUMENT_ORDERING_FIELDS
