"""router.py: """

__author__ = "Artem Hruzd"
__date__ = "03/03/2021 22:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.invoicing.api_v3.viewsets import (
    InvoiceViewSet,
    InvoiceItemGroupViewSet,
    NestedInvoiceItemGroupViewSet,
)


class InvoiceRouter:
    @staticmethod
    def register(router):
        invoice_router = router.register(r"invoices", InvoiceViewSet, "invoices")
        invoice_router.register(
            r"invoice_item_groups",
            NestedInvoiceItemGroupViewSet,
            "invoice-invoice_item_group",
            parents_query_lookups=["invoice__id"],
        )

        invoice_item_group_router = router.register(
            r"invoice_item_groups", InvoiceItemGroupViewSet, "invoice_item_groups"
        )
