"""task.py - axis"""

__author__ = "Steven K"
__date__ = "3/14/23 10:09"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging

from celery.result import AsyncResult
from rest_framework import serializers
from celery import states

from axis.customer_eto.enumerations import ProjectTrackerSubmissionStatus

log = logging.getLogger(__name__)


STATE_CHOICES = [
    (ProjectTrackerSubmissionStatus.SUBMITTED, "Submitted"),
    (states.PENDING, "Pending"),
    (states.RECEIVED, "Received"),
    (states.STARTED, "Started"),
    (states.SUCCESS, "Success"),
    (states.FAILURE, "Failure"),
    (states.REVOKED, "Revoked"),
    (states.REJECTED, "Rejected"),
    (states.RETRY, "Retry"),
    (states.IGNORED, "Ignored"),
]


class CeleryAsyncResultSerializer(serializers.Serializer):
    """Get a task result"""

    id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=STATE_CHOICES)
    status_display = serializers.CharField(max_length=32)
    result = serializers.JSONField(default={})
    args = serializers.CharField(max_length=100, allow_null=True)
    kwargs = serializers.CharField(max_length=256, allow_null=True)
    date_done = serializers.DateTimeField(allow_null=True)

    def get_async_result(self, task_id: str) -> AsyncResult:
        return AsyncResult(task_id)

    def transform_result(self, task: AsyncResult) -> dict:
        """This can truely be anything we want it as a dictionary"""
        if task.result and isinstance(task.result, dict):
            return task.result

        key = "content"
        if task.status == "FAILURE" or isinstance(task.result, Exception):
            key = "error"

        if isinstance(task.result, type(None)):
            content = None
        elif isinstance(task.result, (str, int, float, list, tuple)):
            content = task.result
        elif isinstance(task.result, (Exception, datetime.datetime, datetime.date)):
            content = str(task.result)
        else:
            log.error(f"Unhandled Async Result Type: {type(task.result)} forcing str")
            content = str(task.result)

        return {key: content}

    def to_internal_value(self, data: dict) -> dict:
        """We take a task ID as an argument"""
        task = self.get_async_result(data["task_id"])
        internal = {
            "id": task.id,
            "status": task.status,
            "status_display": dict(STATE_CHOICES)[task.status],
            "result": self.transform_result(task),
            "args": task.args,
            "kwargs": task.kwargs,
            "date_done": task.date_done,
        }
        return super().to_internal_value(internal)
