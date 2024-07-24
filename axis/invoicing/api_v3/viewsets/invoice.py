"""invoice.py: """

__author__ = "Artem Hruzd"
__date__ = "03/03/2021 22:01"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import itertools
import operator
from functools import reduce

import waffle
import django_auto_prefetching
from django.apps import apps
from django.db import transaction
from django.db.models import Q, Count
from django.http import HttpResponse
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend
from axis.core.api_v3.mixins import get_viewset_transition_action_mixin
from axis.core.renderers import BinaryFileRenderer
from axis.invoicing.api_v3 import INVOICE_SEARCH_FIELDS, INVOICE_ORDERING_FIELDS
from axis.invoicing.api_v3.filters import InvoiceFilter
from axis.invoicing.api_v3.serializers import (
    InvoiceSerializer,
    BasicInvoiceSerializer,
    HIRLCreateInvoiceDataSerializer,
    InvoiceAggregateByStateSerializer,
    CustomerHIRLInvoiceSerializer,
)
from axis.invoicing.messages import InvoiceCreatedNotificationMessage
from axis.invoicing.models import Invoice
from axis.invoicing.pdf import CustomerHIRLInvoicePDFReport
from axis.customer_hirl.api_v3.permissions import HIRLCompanyMemberPermission
from axis.core.api_v3.permissions import (
    IsUserIsCompanyAdminPermission,
    IsAdminUserOrSuperUserPermission,
)
from rest_framework.compat import coreapi, coreschema, distinct

customer_hirl_app = apps.get_app_config("customer_hirl")


class InvoiceAxisSearchFilter(AxisSearchFilter):
    """
    Override backend to add ability to search by case-insensitive HashidAutoField for Invoice
    """

    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        orm_lookups = [self.construct_search(str(search_field)) for search_field in search_fields]

        base = queryset
        conditions = []
        for search_term in search_terms:
            queries = [Q(**{orm_lookup: search_term}) for orm_lookup in orm_lookups]
            # this is custom code, all other stuff is from parent
            if search_term and search_term.startswith("INV"):
                # remove INV prefix to increase performance
                term = search_term[3:]
                # find all upper, lower and mixed case combinations of a string
                invoice_all_possible_id_terms = map(
                    "".join, itertools.product(*zip(term.upper(), term.lower()))
                )
                invoice_all_possible_id_terms = set(
                    [f"INV{t}" for t in invoice_all_possible_id_terms]
                )

                queries = queries + [
                    Q(**{"id__icontains": term}) for term in invoice_all_possible_id_terms
                ]

            conditions.append(reduce(operator.or_, queries))
        queryset = queryset.filter(reduce(operator.and_, conditions))

        if self.must_call_distinct(queryset, search_fields):
            # Filtering against a many-to-many field requires us to
            # call queryset.distinct() in order to avoid duplicate items
            # in the resulting queryset.
            # We try to avoid this if possible, for performance reasons.
            queryset = distinct(queryset, base)
        return queryset


class InvoiceViewSet(
    get_viewset_transition_action_mixin(model=Invoice, field_name="state"),
    viewsets.ReadOnlyModelViewSet,
):
    model = Invoice
    queryset = model.objects.all()
    filterset_class = InvoiceFilter
    filter_backends = [AxisFilterBackend, InvoiceAxisSearchFilter, AxisOrderingFilter]
    search_fields = INVOICE_SEARCH_FIELDS
    ordering_fields = INVOICE_ORDERING_FIELDS

    def get_queryset(self):
        queryset = super(InvoiceViewSet, self).get_queryset()
        queryset = queryset.filter_by_user(user=self.request.user)
        if self.action == "aggregate_by_state":
            # we do not need select_related fields for aggregation
            return queryset
        if self.action == "customer_hirl_list":
            queryset = queryset.select_related(
                "customer", "customer__hirlcompanyclient"
            ).prefetch_related("invoiceitemgroup_set")
        return django_auto_prefetching.prefetch(queryset, self.get_serializer_class())

    @property
    def permission_classes(self):
        if self.action == "hirl_create_invoice":
            return (
                IsAuthenticated,
                IsAdminUserOrSuperUserPermission
                | HIRLCompanyMemberPermission
                | IsUserIsCompanyAdminPermission,
            )
        return (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "aggregate_by_state":
            return InvoiceAggregateByStateSerializer
        if self.action == "customer_hirl_list":
            return CustomerHIRLInvoiceSerializer
        if self.request.user.is_authenticated and (
            self.request.user.is_superuser or self.request.user.is_customer_hirl_company_member()
        ):
            return InvoiceSerializer
        return BasicInvoiceSerializer

    @action(
        detail=False,
        methods=[
            "get",
        ],
    )
    def aggregate_by_state(self, request, *args, **kwargs):
        states = {}
        for state, _ in Invoice.STATE_CHOICES:
            states[state] = Count("state", filter=Q(state=state))

        result = self.get_queryset().aggregate(**states)
        serializer = self.get_serializer(data=result)
        serializer.is_valid()
        return Response(serializer.validated_data)

    @action(
        detail=False,
        methods=[
            "get",
        ],
    )
    def customer_hirl_list(self, request, *args, **kwargs):
        return super(InvoiceViewSet, self).list(request, *args, **kwargs)

    @transaction.atomic
    @action(
        detail=False,
        methods=[
            "post",
        ],
    )
    def hirl_create_invoice(self, request, *args, **kwargs):
        serializer = HIRLCreateInvoiceDataSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save()

        invoice_serializer = self.get_serializer(instance=invoice)

        hirl_company = customer_hirl_app.get_customer_hirl_provider_organization()

        url = invoice.get_absolute_url()
        invoice_created_context = {
            "invoice_detail_url": url,
            "customer": invoice.customer,
            "customer_url": invoice.customer.get_absolute_url(),
            "invoice_item_groups": invoice.invoiceitemgroup_set.all(),
            "invoice_id": invoice.id,
        }

        InvoiceCreatedNotificationMessage(url=url).send(
            company=hirl_company, context=invoice_created_context
        )

        return Response(invoice_serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=[
            "get",
        ],
        renderer_classes=[
            BinaryFileRenderer,
        ],
    )
    def customer_hirl_pdf_invoice_report(self, request, pk):
        invoice = self.get_object()
        pdf_cls = CustomerHIRLInvoicePDFReport(invoice=invoice)
        pdf_data = pdf_cls.generate()

        response = HttpResponse(content_type="application/pdf")
        response.write(pdf_data.read())
        return response
