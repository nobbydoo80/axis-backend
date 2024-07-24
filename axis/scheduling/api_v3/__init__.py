# -*- coding: utf-8 -*-
"""__init__.py: """

__author__ = "Artem Hruzd"
__date__ = "10/10/2022 19:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


TASK_SEARCH_FIELDS = [
    "id",
    "task_type__name",
    "assigner__first_name",
    "assigner__last_name",
    "assigner__company__name",
    "assignees__first_name",
    "assigner__last_name",
    "assigner__company__name",
    "status",
    "home__street_line1",
    "home__city__name",
    "home__city__county__name",
    "note",
]
TASK_ORDERING_FIELDS = [
    "id",
]
TASK_FILTER_FIELDS = [
    "status",
    "approval_state",
]
