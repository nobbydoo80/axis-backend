"""router.py: """

from axis.relationship.api_v3.viewsets import RelationshipViewSet

__author__ = "Artem Hruzd"
__date__ = "09/30/2020 18:14"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class RelationshipRouter:
    @staticmethod
    def register(router):
        # relationship app
        relationships_router = router.register(
            r"relationships", RelationshipViewSet, "relationships"
        )
