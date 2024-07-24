"""router.py: """

from axis.community.api_v3.viewsets import (
    CommunityViewSet,
    CommunityNestedRelationshipViewSet,
    CommunityNestedHistoryViewSet,
)
from axis.subdivision.api_v3.viewsets import NestedSubdivisionViewSet

__author__ = "Artem Hruzd"
__date__ = "09/30/2020 17:59"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class CommunityRouter:
    @staticmethod
    def register(router):
        community_router = router.register(r"communities", CommunityViewSet, "communities")
        community_router.register(
            r"relationships",
            CommunityNestedRelationshipViewSet,
            "community-relationships",
            parents_query_lookups=["object_id"],
        )
        community_router.register(
            r"subdivisions",
            NestedSubdivisionViewSet,
            "community-subdivisions",
            parents_query_lookups=["community_id"],
        )
        community_router.register(
            r"history",
            CommunityNestedHistoryViewSet,
            "community-history",
            parents_query_lookups=["id"],
        )
