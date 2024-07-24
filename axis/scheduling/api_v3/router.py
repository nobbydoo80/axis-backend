# -*- coding: utf-8 -*-
"""router.py: """

__author__ = "Artem Hruzd"
__date__ = "10/10/2022 19:52"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.scheduling.api_v3.viewsets import (
    SchedulingTaskViewSet,
    SchedulingTaskNestedHistoryViewSet,
)


class SchedulingRouter:
    @staticmethod
    def register(router):
        task_router = router.register(
            r"scheduling_tasks",
            SchedulingTaskViewSet,
            "scheduling_tasks",
        )

        task_router.register(
            r"history",
            SchedulingTaskNestedHistoryViewSet,
            "scheduling_tasks-history",
            parents_query_lookups=["id"],
        )
