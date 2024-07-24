"""invoice_item_group.py: """

__author__ = "Artem Hruzd"
__date__ = "03/04/2021 21:40"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import django_auto_prefetching

from django.apps import apps
from django.db.models import Case, When, F

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_extensions.mixins import NestedViewSetMixin

from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend
from axis.core.api_v3.permissions import (
    IsAdminUserOrSuperUserPermission,
    IsUserIsCompanyAdminPermission,
)
from axis.customer_hirl.api_v3.permissions import HIRLCompanyMemberPermission
from axis.invoicing.api_v3 import (
    INVOICE_ITEM_GROUP_SEARCH_FIELDS,
    INVOICE_ITEM_GROUP_ORDERING_FIELDS,
)
from axis.invoicing.api_v3.filters import InvoiceItemGroupFilter, CustomerHIRLInvoiceItemGroupFilter
from axis.invoicing.api_v3.serializers import (
    InvoiceItemGroupSerializer,
    BasicInvoiceItemGroupSerializer,
    CustomerHIRLInvoiceManagementListSerializer,
)
from axis.invoicing.models import InvoiceItemGroup
from axis.customer_hirl.models import HIRLProjectRegistration

customer_hirl_app = apps.get_app_config("customer_hirl")


class InvoiceItemGroupViewSet(viewsets.ModelViewSet):
    model = InvoiceItemGroup
    queryset = model.objects.all()
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = INVOICE_ITEM_GROUP_SEARCH_FIELDS
    ordering_fields = INVOICE_ITEM_GROUP_ORDERING_FIELDS

    def get_queryset(self):
        queryset = super(InvoiceItemGroupViewSet, self).get_queryset()
        queryset = queryset.filter_by_user(user=self.request.user)

        if self.action == "customer_hirl_invoice_management_list":
            queryset = queryset.annotate_client_ca_status()
            queryset = queryset.select_related(
                "home_status__eep_program",
                "home_status__home",
                "home_status__customer_hirl_project",
                "home_status__customer_hirl_project__registration",
                "home_status__customer_hirl_project__registration__builder_organization",
                "home_status__customer_hirl_project__registration__architect_organization",
                "home_status__customer_hirl_project__registration__developer_organization",
                "home_status__customer_hirl_project__registration__community_owner_organization",
                "home_status__customer_hirl_project__home_address_geocode",
                "home_status__customer_hirl_project__home_address_geocode__raw_city",
                "home_status__customer_hirl_project__home_address_geocode__raw_city__county",
                "home_status__customer_hirl_project__home_address_geocode_response",
                "home_status__customer_hirl_project__home_address_geocode_response__geocode",
            )
        return django_auto_prefetching.prefetch(queryset, self.get_serializer_class())

    @property
    def filterset_class(self):
        if self.action == "customer_hirl_invoice_management_list":
            return CustomerHIRLInvoiceItemGroupFilter
        return InvoiceItemGroupFilter

    @property
    def permission_classes(self):
        return (
            IsAuthenticated,
            IsAdminUserOrSuperUserPermission
            | HIRLCompanyMemberPermission
            | IsUserIsCompanyAdminPermission,
        )

    def get_serializer_class(self):
        if self.action == "customer_hirl_invoice_management_list":
            return CustomerHIRLInvoiceManagementListSerializer
        if self.request.user.is_authenticated and (
            self.request.user.is_superuser
            or self.request.user.company
            and self.request.user.company.slug == customer_hirl_app.CUSTOMER_SLUG
        ):
            return InvoiceItemGroupSerializer
        return BasicInvoiceItemGroupSerializer

    @action(detail=False)
    def customer_hirl_invoice_management_list(self, request, *args, **kwargs):
        return super(InvoiceItemGroupViewSet, self).list(request, *args, **kwargs)


class NestedInvoiceItemGroupViewSet(
    NestedViewSetMixin, viewsets.mixins.ListModelMixin, viewsets.GenericViewSet
):
    model = InvoiceItemGroup
    queryset = model.objects.all()
    filterset_class = InvoiceItemGroupFilter
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = INVOICE_ITEM_GROUP_SEARCH_FIELDS
    ordering_fields = INVOICE_ITEM_GROUP_ORDERING_FIELDS

    def get_serializer_class(self):
        if (
            self.request.user.is_superuser
            or self.request.user.company
            and self.request.user.company.slug == customer_hirl_app.CUSTOMER_SLUG
        ):
            return InvoiceItemGroupSerializer
        return BasicInvoiceItemGroupSerializer
