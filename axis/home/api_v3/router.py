"""router.py: """

from axis.home.api_v3.viewsets import (
    HomeViewSet,
    HomeProjectStatusViewSet,
    HomeNestedRelationshipViewSet,
    HomeNestedHistoryViewSet,
    HomeNestedCustomerDocumentViewSet,
    NestedEEPProgramHomeStatusViewSet,
)

__author__ = "Artem Hruzd"
__date__ = "09/30/2020 18:09"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class HomeRouter:
    @staticmethod
    def register(router):
        # home app
        home_router = router.register(r"homes", HomeViewSet, "homes")

        home_router.register(
            r"relationships",
            HomeNestedRelationshipViewSet,
            "home-relationships",
            parents_query_lookups=["object_id"],
        )

        home_router.register(
            r"documents",
            HomeNestedCustomerDocumentViewSet,
            "home-documents",
            parents_query_lookups=["object_id"],
        )

        home_router.register(
            r"history", HomeNestedHistoryViewSet, "home-history", parents_query_lookups=["id"]
        )

        home_router.register(
            r"home_project_status",
            NestedEEPProgramHomeStatusViewSet,
            "home-project_status",
            parents_query_lookups=["home"],
        )

        router.register(r"home_project_statuses", HomeProjectStatusViewSet, "home_status")
