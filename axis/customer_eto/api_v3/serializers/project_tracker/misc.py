# -*- coding: utf-8 -*-
"""misc.py - axis"""

__author__ = "Steven K"
__date__ = "3/15/23 11:14"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from rest_framework import serializers

from axis.core.api_v3.serializers.task import STATE_CHOICES, CeleryAsyncResultSerializer

log = logging.getLogger(__name__)


class ProjectTrackerSubmitSerializer(serializers.Serializer):
    """Submitting a project to ETO will return this data"""

    id = serializers.IntegerField(help_text="Home Status ID")
    content = serializers.CharField(help_text="Submission message")
    project_types = serializers.ListSerializer(
        child=serializers.CharField(), required=False, help_text="PT Submission Type"
    )
    task_ids = serializers.ListSerializer(
        child=serializers.UUIDField(),
        help_text="Submission Task IDs",
        required=False,
    )


class ProjectTrackerStatusSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="Home Status ID")

    status = serializers.ChoiceField(choices=STATE_CHOICES)
    status_display = serializers.CharField(max_length=32)
    result = serializers.CharField(max_length=1000)

    task_ids = serializers.ListSerializer(
        child=serializers.UUIDField(),
        help_text="Submission Task IDs",
        required=False,
    )

    task_statuses = serializers.ListSerializer(child=CeleryAsyncResultSerializer())
