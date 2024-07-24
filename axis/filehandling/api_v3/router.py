"""router.py: """

from axis.filehandling.api_v3.viewsets import (
    CustomerDocumentViewSet,
    PublicCustomerDocumentViewSet,
    CustomerDocumentNestedHistoryViewSet,
)

__author__ = "Artem Hruzd"
__date__ = "09/30/2020 18:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class FileHandlingRouter:
    @staticmethod
    def register(router):
        # filehandling app
        customer_document_router = router.register(
            r"customer_document", CustomerDocumentViewSet, "customer_document"
        )
        customer_document_router.register(
            r"history",
            CustomerDocumentNestedHistoryViewSet,
            "customer_document-history",
            parents_query_lookups=["id"],
        )
        router.register(
            r"public_document",
            PublicCustomerDocumentViewSet,
            "public_document",
        )
