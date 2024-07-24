"""filters.py: """

__author__ = "Artem Hruzd"
__date__ = "03/03/2021 22:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.db.models import F, Q
from django_filters import rest_framework as filters

from axis.company.models import Company
from axis.customer_hirl.models import BuilderAgreement, HIRLProjectRegistration
from axis.invoicing.api_v3 import INVOICE_FILTER_FIELDS, INVOICE_ITEM_GROUP_FILTER_FIELDS
from axis.invoicing.models import Invoice, InvoiceItemGroup


class InvoiceIsPartiallyPaidChoiceFilter(filters.ChoiceFilter):
    def __init__(self, *args, **kwargs):
        kwargs["choices"] = [
            ("", "All"),
            ("is_partially_paid", "Is Partially Paid"),
            ("is_not_partially_paid", "Is Not Partially Paid"),
        ]
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value == "is_partially_paid":
            qs = qs.filter(total_paid__gt=0, total__gt=F("total_paid"))
        elif value == "is_not_partially_paid":
            qs = qs.exclude(total_paid__gt=0, total__gt=F("total_paid"))
        return qs


class InvoiceContainsFeesByNameMultipleChoiceFilter(filters.MultipleChoiceFilter):
    def __init__(self, *args, **kwargs):
        kwargs["choices"] = [
            ("", "All"),
            ("appeals_fees", "Appeals Fees"),
        ]
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value:
            qs = qs.filter(invoiceitemgroup__category__in=value)
        return qs


class InvoiceFilter(filters.FilterSet):
    partially_paid = InvoiceIsPartiallyPaidChoiceFilter()
    contains_fees_by_name = InvoiceContainsFeesByNameMultipleChoiceFilter()

    class Meta:
        model = Invoice
        fields = INVOICE_FILTER_FIELDS


class CustomerHIRLProjectHaveLegacyNotifiedCertificationChoiceFilter(filters.ChoiceFilter):
    """
    Include/exclude invoice item groups when
    home_status.customer_hirl_project.hirllegacycertification
    have notification sent date
    """

    def __init__(self, *args, **kwargs):
        kwargs["choices"] = [
            ("", "All"),
            ("notified", "Have legacy notification sent date"),
            ("not_notified", "Do not have legacy notification sent date"),
        ]
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        rel_prefix = "home_status__customer_hirl_project__hirllegacycertification"
        if value == "notified":
            qs = qs.filter(
                Q(**{f"{rel_prefix}__data__has_key": "InvoiceSentDate"})
                & ~Q(**{f"{rel_prefix}__data__InvoiceSentDate": None}),
            )
        elif value == "not_notified":
            qs = qs.filter(
                Q(
                    **{
                        f"{rel_prefix}__data__has_key": "InvoiceSentDate",
                        f"{rel_prefix}__data__InvoiceSentDate": None,
                    }
                )
                | ~Q(
                    **{
                        f"{rel_prefix}__data__has_key": "InvoiceSentDate",
                    }
                )
            )
        return qs


class InvoiceItemGroupFilter(filters.FilterSet):
    uninvoiced = filters.BooleanFilter(
        field_name="invoice", lookup_expr="isnull", help_text="Invoice Item Groups without Invoice"
    )
    created_at__gte = filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_at__gt = filters.DateFilter(field_name="created_at", lookup_expr="gt")
    created_at__lte = filters.DateFilter(field_name="created_at", lookup_expr="lte")
    created_at__lt = filters.DateFilter(field_name="created_at", lookup_expr="lt")
    created_at_range = filters.DateRangeFilter(field_name="created_at")
    current_balance_range = filters.RangeFilter(field_name="current_balance")

    class Meta:
        model = InvoiceItemGroup
        fields = INVOICE_ITEM_GROUP_FILTER_FIELDS


class CustomerHIRLInvoiceItemGroupFilter(InvoiceItemGroupFilter):
    customer_hirl_erfp_ca_status = filters.ChoiceFilter(
        choices=BuilderAgreement.STATE_CHOICES
        + (("do_not_have_ca", "Do not have Client Agreement"),),
        method="filter_customer_hirl_erfp_ca_status",
        help_text="Entity Responsible For Payment Client Agreement state. "
        "Use special `do_not_have_ca` to filter by isnull",
    )

    customer_hirl_erfp_company = filters.ModelChoiceFilter(
        queryset=Company.objects.all(), method="filter_customer_hirl_erfp_company"
    )
    customer_hirl_client_company = filters.ModelChoiceFilter(
        queryset=Company.objects.all(), method="filter_customer_hirl_client_company"
    )
    customer_hirl_project_have_legacy_notified_certification = (
        CustomerHIRLProjectHaveLegacyNotifiedCertificationChoiceFilter()
    )

    class Meta:
        model = InvoiceItemGroup
        fields = INVOICE_ITEM_GROUP_FILTER_FIELDS + [
            "home_status__customer_hirl_project__registration__project_type",
        ]

    def filter_customer_hirl_erfp_company(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(
                home_status__customer_hirl_project__registration__builder_organization=value,
                home_status__customer_hirl_project__registration__entity_responsible_for_payment=HIRLProjectRegistration.BUILDER_RESPONSIBLE_ENTITY,
            )
            | Q(
                home_status__customer_hirl_project__registration__architect_organization=value,
                home_status__customer_hirl_project__registration__entity_responsible_for_payment=HIRLProjectRegistration.ARCHITECT_RESPONSIBLE_ENTITY,
            )
            | Q(
                home_status__customer_hirl_project__registration__developer_organization=value,
                home_status__customer_hirl_project__registration__entity_responsible_for_payment=HIRLProjectRegistration.DEVELOPER_RESPONSIBLE_ENTITY,
            )
            | Q(
                home_status__customer_hirl_project__registration__community_owner_organization=value,
                home_status__customer_hirl_project__registration__entity_responsible_for_payment=HIRLProjectRegistration.COMMUNITY_OWNER_RESPONSIBLE_ENTITY,
            )
        )

    def filter_customer_hirl_client_company(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(
                home_status__customer_hirl_project__registration__builder_organization=value,
            )
            | Q(
                home_status__customer_hirl_project__registration__developer_organization=value,
                home_status__customer_hirl_project__registration__project_client=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            )
            | Q(
                home_status__customer_hirl_project__registration__architect_organization=value,
                home_status__customer_hirl_project__registration__project_client=HIRLProjectRegistration.PROJECT_CLIENT_ARCHITECT,
            )
            | Q(
                home_status__customer_hirl_project__registration__developer_organization=value,
                home_status__customer_hirl_project__registration__project_client=HIRLProjectRegistration.PROJECT_CLIENT_DEVELOPER,
            )
            | Q(
                home_status__customer_hirl_project__registration__community_owner_organization=value,
                home_status__customer_hirl_project__registration__project_client=HIRLProjectRegistration.PROJECT_CLIENT_OWNER,
            )
        )

    def filter_customer_hirl_erfp_ca_status(self, queryset, name, value):
        queryset = queryset.annotate_client_ca_status()
        if value == "do_not_have_ca":
            return queryset.filter(client_ca_status__isnull=True)
        return queryset.filter(client_ca_status=value)
