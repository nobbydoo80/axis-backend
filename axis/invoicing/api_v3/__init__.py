"""__init__.py: """

__author__ = "Artem Hruzd"
__date__ = "03/03/2021 17:13"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


INVOICE_SEARCH_FIELDS = [
    "id",
    "state",
    "customer__name",
    "issuer__name",
    "invoiceitemgroup__home_status__customer_hirl_project__id",
    "invoiceitemgroup__home_status__customer_hirl_project__h_number",
    "invoiceitemgroup__home_status__home__street_line1",
    "invoiceitemgroup__home_status__home__city__name",
    "invoiceitemgroup__home_status__home__city__county__name",
    "invoiceitemgroup__home_status__customer_hirl_project__registration__builder_organization__name",
    "invoiceitemgroup__home_status__customer_hirl_project__registration__developer_organization__name",
    "invoiceitemgroup__home_status__customer_hirl_project__registration__community_owner_organization__name",
    "invoiceitemgroup__home_status__customer_hirl_project__registration__architect_organization__name",
]
INVOICE_ORDERING_FIELDS = [
    "id",
    "total",
    "total_paid",
    "updated_at",
    "created_at",
]
INVOICE_FILTER_FIELDS = [
    "state",
]


INVOICE_ITEM_GROUP_SEARCH_FIELDS = [
    "id",
    "home_status__customer_hirl_project__id",
    "home_status__customer_hirl_project__h_number",
    "home_status__customer_hirl_project__registration__id",
    "home_status__home__street_line1",
    "home_status__home__city__name",
    "home_status__home__city__county__name",
    "home_status__customer_hirl_project__registration__builder_organization__name",
    "home_status__customer_hirl_project__registration__developer_organization__name",
    "home_status__customer_hirl_project__registration__community_owner_organization__name",
    "home_status__customer_hirl_project__registration__architect_organization__name",
    "home_status__eep_program__name",
]
INVOICE_ITEM_GROUP_ORDERING_FIELDS = [
    "id",
    "total",
    "home_status__customer_hirl_project__id",
    "home_status_customer_hirl_project__registration__builder_organization__name",
    "home_status__eep_program__name",
    "updated_at",
    "created_at",
]
INVOICE_ITEM_GROUP_FILTER_FIELDS = ["home_status__state", "category"]
