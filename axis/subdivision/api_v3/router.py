"""router.py: """

from axis.subdivision.api_v3.viewsets import (
    SubdivisionViewSet,
    SubdivisionNestedRelationshipViewSet,
)

__author__ = "Artem Hruzd"
__date__ = "09/30/2020 17:22"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class SubdivisionRouter:
    @staticmethod
    def register(router):
        subdivision_router = router.register(r"subdivisions", SubdivisionViewSet, "subdivisions")

        subdivision_router.register(
            r"relationships",
            SubdivisionNestedRelationshipViewSet,
            "subdivision-relationships",
            parents_query_lookups=["object_id"],
        )
