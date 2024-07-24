"""router.py: """

from axis.eep_program.api_v3.viewsets import EEPProgramViewSet, EEPProgramNestedHistoryViewSet

__author__ = "Artem Hruzd"
__date__ = "09/30/2020 18:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class EEPProgramRouter:
    @staticmethod
    def register(router):
        eep_program_router = router.register(r"eep_programs", EEPProgramViewSet, "eep_programs")
        eep_program_router.register(
            r"history",
            EEPProgramNestedHistoryViewSet,
            "eep_program-history",
            parents_query_lookups=["id"],
        )
