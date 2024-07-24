"""test_task.py - axis"""

__author__ = "Steven K"
__date__ = "3/14/23 11:06"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import json
import logging
import random
from unittest import mock

from celery import states
from django.urls import reverse_lazy

from axis.core.tests.factories import general_user_factory
from axis.core.tests.testcases import ApiV3Tests

log = logging.getLogger(__name__)


class MockAsyncResult:
    def __init__(self, id: str, *kwargs):
        self.id = id

    @property
    def status(self):
        if self.id.startswith("30"):
            return states.RECEIVED
        if self.id.startswith("32"):
            return states.STARTED
        elif self.id.startswith("25"):
            return states.SUCCESS
        elif self.id.startswith("26"):
            return states.SUCCESS
        elif self.id.startswith("27"):
            return states.SUCCESS
        elif self.id.startswith("66"):
            return states.FAILURE
        return states.PENDING

    @property
    def result(self):
        if self.status == states.SUCCESS:
            if self.id.startswith("25"):
                return {"some": "random", "data": None, "foo": 2.2}
            elif self.id.startswith("26"):
                return 3.14
            elif self.id.startswith("27a"):
                # This is used for ETO PT Submission Fail
                return {
                    "status": states.FAILURE,
                    "project_type": "ENH",
                    "result": f"Fastrack submission Error: Something",
                    "source": "<XML>",
                    "count": 2,
                    "response": "<XML>",
                }
            elif self.id.startswith("27b"):
                # This is used for ETO PT Submission Fail
                return {
                    "status": states.SUCCESS,
                    "project_type": "ENH",
                    "result": f"ENH Project P00001685498 ETO submission to https://services-stg.energytrust.org/etoimport/service.asmx?op=FTImportXML took 11.413 s",
                    "source": "<XML>",
                    "count": 2,
                    "response": "<XML>",
                }
            elif self.id.startswith("27c"):
                # This is used for ETO PT Submission Fail
                return {
                    "status": states.SUCCESS,
                    "project_type": "SLE",
                    "result": f"SLE Project P00001685498 ETO submission to https://services-stg.energytrust.org/etoimport/service.asmx?op=FTImportXML took 11.413 s",
                    "source": "<XML>",
                    "count": 2,
                    "response": "<XML>",
                }

        if self.status == states.STARTED:
            return {"pid": 123, "hostname": "celery@celery_worker"}
        if self.status == states.FAILURE:
            return ValueError("Some Error")

    @property
    def args(self):
        return "('123',)"

    @property
    def kwargs(self):
        if self.id.endswith("688"):
            return "{'user_id': 123, 'project_type': 'ENH'}"
        if self.id.endswith("689"):
            return "{'user_id': 123, 'project_type': 'SLE'}"

    @property
    def date_done(self):
        if self.status in [states.SUCCESS, states.FAILURE]:
            return datetime.datetime.now() - datetime.timedelta(seconds=random.uniform(0, 5.0))


@mock.patch(
    "axis.core.api_v3.serializers.task.CeleryAsyncResultSerializer.get_async_result",
    MockAsyncResult,
)
class TestCeleryTaskViewSet(ApiV3Tests):
    def test_pending(self):
        user = general_user_factory()
        uuid = "10bc50f6-b24c-4f9e-a08c-c0435495c688"
        url = reverse_lazy("api_v3:task-status", kwargs=dict(uuid=uuid))

        self.client.force_authenticate(user=user)
        response = self.client.get(url)
        data = response.data
        self.assertEqual(data["id"], uuid)
        self.assertEqual(data["status"], states.PENDING)
        self.assertIsNone(data["result"]["content"])
        self.assertIsNone(data["date_done"])

    def test_received(self):
        user = general_user_factory()
        uuid = "30bc50f6-b24c-4f9e-a08c-c0435495c688"
        url = reverse_lazy("api_v3:task-status", kwargs=dict(uuid=uuid))

        self.client.force_authenticate(user=user)
        response = self.client.get(url)
        data = response.data
        self.assertEqual(data["id"], uuid)
        self.assertEqual(data["status"], states.RECEIVED)
        self.assertIsNone(data["result"]["content"])
        self.assertIsNone(data["date_done"])

    def test_success(self):
        user = general_user_factory()
        uuid = "25bc50f6-b24c-4f9e-a08c-c0435495c688"
        url = reverse_lazy("api_v3:task-status", kwargs=dict(uuid=uuid))
        self.client.force_authenticate(user=user)
        response = self.client.get(url)
        data = response.data

        self.assertEqual(data["id"], uuid)
        self.assertEqual(data["status"], states.SUCCESS)
        self.assertEqual(data["result"], {"some": "random", "data": None, "foo": 2.2})
        self.assertIsNotNone(data["date_done"])

    def test_success_2(self):
        user = general_user_factory()
        uuid = "26bc50f6-b24c-4f9e-a08c-c0435495c688"
        url = reverse_lazy("api_v3:task-status", kwargs=dict(uuid=uuid))
        self.client.force_authenticate(user=user)
        response = self.client.get(url)
        data = response.data

        self.assertEqual(data["id"], uuid)
        self.assertEqual(data["status"], states.SUCCESS)
        self.assertEqual(data["result"]["content"], 3.14)
        self.assertIsNotNone(data["date_done"])

    def test_failure(self):
        user = general_user_factory()
        uuid = "66bc50f6-b24c-4f9e-a08c-c0435495c688"
        url = reverse_lazy("api_v3:task-status", kwargs=dict(uuid=uuid))
        self.client.force_authenticate(user=user)
        response = self.client.get(url)
        data = response.data

        self.assertEqual(data["id"], uuid)
        self.assertEqual(data["status"], states.FAILURE)
        self.assertEqual(data["result"]["error"], str(ValueError("Some Error")))
        self.assertIsNotNone(data["date_done"])
