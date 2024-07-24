"""router.py: """

__author__ = "Artem Hruzd"
__date__ = "09/30/2020 18:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from axis.qa.api_v3.viewsets import (
    QAStatusViewSet,
    ObservationViewSet,
    NestedQANoteViewSet,
    QANoteViewSet,
    QAStatusNestedCustomerDocumentViewSet,
)


class QARouter:
    @staticmethod
    def register(router):
        # qa app
        qa_status_router = router.register(r"qa_statuses", QAStatusViewSet, "qa_statuses")

        qa_status_router.register(
            r"qa_notes",
            NestedQANoteViewSet,
            "qa_status-qa_notes",
            parents_query_lookups=["qa_status__id"],
        )

        qa_status_router.register(
            r"documents",
            QAStatusNestedCustomerDocumentViewSet,
            f"qa_status-documents",
            parents_query_lookups=["object_id"],
        )

        router.register(r"qa_notes", QANoteViewSet, "qa_notes")

        router.register(r"observations", ObservationViewSet, "observations")
