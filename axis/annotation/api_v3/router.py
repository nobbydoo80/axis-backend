__author__ = "Artem Hruzd"
__date__ = "06/03/2023 20:18"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.annotation.api_v3.viewsets import (
    AnnotationTypeViewSet,
    AnnotationViewSet,
    AnnotationNestedHistoryViewSet,
)


class AnnotationRouter:
    @staticmethod
    def register(router):
        annotation_router = router.register(
            "annotations",
            AnnotationViewSet,
            "annotations",
        )

        annotation_router.register(
            "history",
            AnnotationNestedHistoryViewSet,
            "annotation-history",
            parents_query_lookups=["id"],
        )

        annotation_type_router = router.register(
            "annotation_types",
            AnnotationTypeViewSet,
            "annotation_types",
        )
