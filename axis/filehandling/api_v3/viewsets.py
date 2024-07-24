from django.apps import apps
from django.http import HttpResponseRedirect, Http404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from hashid_field import Hashid
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter
from axis.core.api_v3.viewsets import NestedHistoryViewSet
from axis.filehandling.api_v3 import (
    CUSTOMER_DOCUMENT_SEARCH_FIELDS,
    CUSTOMER_DOCUMENT_ORDERING_FIELDS,
    DOCUMENT_ACCESS_LEVEL_PUBLIC,
    DOCUMENT_ACCESS_LEVEL_GLOBAL,
    DOCUMENT_ACCESS_LEVEL_PRIVATE,
)
from axis.filehandling.api_v3.filters import CustomerDocumentFilterSet
from axis.filehandling.api_v3.serializers import (
    CustomerDocumentSerializer,
    AsynchronousProcessedDocumentSerializer,
)
from axis.filehandling.models import CustomerDocument, AsynchronousProcessedDocument
from axis.filehandling.tasks import download_multiple_customer_documents_task

__author__ = "Artem Hruzd"
__date__ = "03/12/2020 09:47"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

filehandling_app = apps.get_app_config("filehandling")


class CustomerDocumentAccessLevelMixin:
    def get_pruned_request_data(self, request_data: dict) -> dict:
        data = dict(request_data.items())
        doc_access_level = data.get("doc_access_level")
        if doc_access_level:
            del data["doc_access_level"]
        if doc_access_level == DOCUMENT_ACCESS_LEVEL_PUBLIC:
            data["is_public"] = True
            data["login_required"] = True
        elif doc_access_level == DOCUMENT_ACCESS_LEVEL_PRIVATE:
            data["is_public"] = False
            data["login_required"] = True
        elif doc_access_level == DOCUMENT_ACCESS_LEVEL_GLOBAL:
            data["is_public"] = True
            data["login_required"] = False
        return data


class CustomerDocumentViewSet(
    viewsets.mixins.UpdateModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
    CustomerDocumentAccessLevelMixin,
):
    """
    CustomerDocument management endpoints.

    preview:
        AWS document links have expired date. To make them permanent user must use this endpoint.
        This is useful for flatpages and other dynamic
        content where we need to share AXIS Customer document link

    download_all:
        Allow to download all CustomerDocument's attached to object
    """

    permission_classes = (IsAuthenticated,)
    model = CustomerDocument
    queryset = model.objects.all()
    serializer_class = CustomerDocumentSerializer
    filter_backends = [DjangoFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = CUSTOMER_DOCUMENT_SEARCH_FIELDS
    ordering_fields = CUSTOMER_DOCUMENT_ORDERING_FIELDS

    def get_queryset(self):
        qs = super(CustomerDocumentViewSet, self).get_queryset()
        return qs.filter_by_user(user=self.request.user, include_public=True)

    @swagger_auto_schema(
        methods=["get"],
        responses={
            "301": openapi.Response(
                "File Attachment", schema=openapi.Schema(type=openapi.TYPE_FILE)
            ),
            "200": None,
        },
    )
    @action(detail=True)
    def preview(self, request, *args, **kwargs):
        customer_document = self.get_object()
        return HttpResponseRedirect(redirect_to=customer_document.document.url)

    def update(self, request, *args, **kwargs) -> Response:
        """Map out our public / login required"""
        partial = kwargs.pop("partial", False)
        data = self.get_pruned_request_data(request.data)

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class NestedCustomerDocumentViewSet(
    NestedViewSetMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Using in nested router to show resource documents
    list:
        Return all Document objects
    create:
        Create a new Document
    download_all:
        Download All Customer Documents attached to provided object
    """

    permission_classes = (IsAuthenticated,)
    model = CustomerDocument
    queryset = model.objects.all().order_by(*model._meta.ordering)
    serializer_class = CustomerDocumentSerializer
    filter_backends = [DjangoFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = CUSTOMER_DOCUMENT_SEARCH_FIELDS
    ordering_fields = CUSTOMER_DOCUMENT_ORDERING_FIELDS
    filterset_class = CustomerDocumentFilterSet

    def get_queryset(self):
        qs = super(NestedCustomerDocumentViewSet, self).get_queryset()
        return qs.filter_by_user(user=self.request.user, include_public=True)

    def perform_create(self, serializer):
        """
        Override this method by passing content_type, object_id and company
        """
        raise NotImplementedError

    @action(detail=False)
    def download_all(self, request, parent_lookup_object_id):
        async_document = AsynchronousProcessedDocument.objects.create(
            company=self.request.user.company,
            document=None,
            task_name=download_multiple_customer_documents_task.name,
            task_id="",
            download=True,
        )

        download_multiple_customer_documents_task.delay(
            result_object_id=async_document.id,
            customer_documents_ids=list(self.get_queryset().values_list("id", flat=True)),
        )
        async_document.refresh_from_db()
        async_document_serializer = AsynchronousProcessedDocumentSerializer(instance=async_document)
        return Response(async_document_serializer.data)


class CustomerDocumentNestedHistoryViewSet(NestedHistoryViewSet):
    permission_classes = (IsAuthenticated,)
    model = CustomerDocument.history.model
    queryset = model.objects.all()
    filter_backends = [DjangoFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = CUSTOMER_DOCUMENT_SEARCH_FIELDS
    ordering_fields = CUSTOMER_DOCUMENT_ORDERING_FIELDS


class PublicCustomerDocumentViewSet(
    viewsets.mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = ()
    lookup_field = "hash_id"
    model = CustomerDocument
    serializer_class = CustomerDocumentSerializer
    queryset = model.objects.filter(login_required=False)
    """
    Public Document endpoint.

    Any document that needs to be shared with the world will be shared here.  You obtain it via a hash_id.
    """

    def get_object(self):
        try:
            real_id = Hashid(
                self.kwargs["hash_id"], salt=filehandling_app.HASHID_FILE_HANDLING_SALT
            )
            return get_object_or_404(self.queryset, pk=real_id.id)
        except ValueError:
            raise Http404

    @swagger_auto_schema(
        responses={
            "301": openapi.Response(
                "File Attachment", schema=openapi.Schema(type=openapi.TYPE_FILE)
            ),
            "200": None,
        },
    )
    def retrieve(self, request, *args, **kwargs):
        customer_document = self.get_object()
        return HttpResponseRedirect(redirect_to=customer_document.document.url)
