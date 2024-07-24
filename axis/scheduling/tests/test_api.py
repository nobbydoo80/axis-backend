"""test_api.py: """

__author__ = "Artem Hruzd"
__date__ = "02/03/2020 19:39"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import random
from unittest import mock

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone

from axis.core.tests.testcases import ApiV3Tests
from axis.home.models import Home
from axis.scheduling.models import Task, TaskType
from axis.scheduling.tests.mixins import SchedulingTaskMixin


class SchedulingTaskViewSetTest(SchedulingTaskMixin, ApiV3Tests):
    @mock.patch("axis.messaging.messages.ModernMessage.send")
    def test_create_task_home_with_provider(self, send_message):
        provider_user = self.get_nonadmin_user("provider")
        task_type = TaskType.objects.filter(company=provider_user.company).first()
        self.assertTrue(
            self.client.login(username=provider_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login"
            % (provider_user.username, provider_user.pk),
        )
        home = Home.objects.first()
        task_status = random.choice(Task.TASK_STATUS_CHOICES)[0]
        task_data = {
            "task_type": task_type.pk,
            "assigner": provider_user.pk,
            "datetime": "2020-03-16T11:43",
            "content_type": ContentType.objects.get_for_model(Home).pk,
            "object_id": home.pk,
            "home": home.pk,
            "status": task_status,
            "status_changed_at": timezone.now(),
            "status_approver": provider_user.pk,
            "status_annotation": "new annotation",
            "approval_state": Task.APPROVAL_STATE_APPROVED,
            "assignees": [
                provider_user.pk,
            ],
        }

        url = "{}?machinery=TaskHomeMachinery&content_type=home".format(reverse("apiv2:task-list"))

        response = self.client.post(url, data=task_data)
        self.assertEqual(response.status_code, 201)

        created_task = Task.objects.order_by("id").last()
        self.assertEqual(created_task.task_type.pk, task_data["task_type"])
        self.assertEqual(created_task.home, home)
        self.assertEqual(created_task.status, task_data["status"])
        # user can't set status_annotation on creating.
        # Only company admin can do this via scheduling dashboard
        self.assertEqual(created_task.status_annotation, "")
        # check that common user can't set approval state
        self.assertEqual(created_task.approval_state, Task.APPROVAL_STATE_NEW)

        send_message.assert_called_once()
