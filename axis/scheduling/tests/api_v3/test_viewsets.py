"""test_viewsets.py: """

__author__ = "Artem Hruzd"
__date__ = "10/11/2022 12:28"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import json
from unittest import mock

from django.urls import reverse

from axis.core.tests.testcases import ApiV3Tests
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.scheduling.models import Task
from axis.scheduling.tests.factories import task_factory
from axis.scheduling.tests.mixins import SchedulingTaskMixin


class TaskViewSetTests(SchedulingTaskMixin, ApiV3Tests):
    @mock.patch("axis.scheduling.tasks.scheduling_task_report_task.delay")
    def test_create_scheduling_task_report(self, scheduling_task_report_task):
        provider_user = self.get_admin_user("provider")
        self.assertTrue(
            self.client.login(username=provider_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login"
            % (provider_user.username, provider_user.pk),
        )

        task_ids = list(
            Task.objects.filter(assigner__company=provider_user.company).values_list(
                "pk", flat=True
            )
        )
        url = reverse("api_v3:scheduling_tasks-create-scheduling-task-report")
        response = self.client.get(url, data={"task_ids": task_ids})

        asynchronous_process_document = AsynchronousProcessedDocument.objects.first()

        self.assertEqual(
            response.json()["asynchronous_process_document_url"],
            response.wsgi_request.build_absolute_uri(
                asynchronous_process_document.get_absolute_url()
            ),
        )

        scheduling_task_report_task.assert_called_once_with(
            asynchronous_process_document_id=asynchronous_process_document.id,
            task_ids=task_ids,
            user_id=provider_user.id,
        )

    @mock.patch("axis.messaging.messages.ModernMessage.send")
    def test_change_state(self, send_message):
        provider_user = self.get_admin_user("provider")
        task = Task.objects.filter(
            assigner__company=provider_user.company, approval_state=Task.APPROVAL_STATE_NEW
        ).first()

        self.client.force_authenticate(user=provider_user)

        url = reverse("api_v3:scheduling_tasks-change-state")
        response = self.client.patch(
            url,
            data=json.dumps(
                {
                    "task_ids": [
                        task.pk,
                    ],
                    "new_state": Task.APPROVAL_STATE_APPROVED,
                    "approval_annotation": "some note",
                }
            ),
            content_type="application/json",
        )
        task.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(task.approval_state, Task.APPROVAL_STATE_APPROVED)
        self.assertEqual(task.approval_annotation, "some note")
        self.assertEqual(send_message.call_count, 1)

        with self.subTest("Use unknown state"):
            response = self.client.patch(
                url,
                data=json.dumps(
                    {
                        "task_ids": [
                            task.pk,
                        ],
                        "new_state": "unknown",
                        "approval_annotation": "",
                    }
                ),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data["new_state"][0], '"unknown" is not a valid choice.')

        with self.subTest("Un proceed state"):
            response = self.client.patch(
                url,
                data=json.dumps(
                    {
                        "task_ids": [
                            task.pk,
                        ],
                        "new_state": Task.APPROVAL_STATE_NEW,
                        "approval_annotation": "",
                    }
                ),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(
                response.data["state"][0],
                "Change state from {from_state} to "
                "{to_state} for {task} "
                "is not allowed".format(
                    from_state=task.approval_state, to_state=Task.APPROVAL_STATE_NEW, task=task
                ),
            )

        with self.subTest("Change state as user without permissions"):
            provider_user = self.get_admin_user("provider")
            rater_user = self.get_admin_user("rater")

            task = task_factory(
                assignees=[
                    rater_user,
                ],
                assigner=provider_user,
                approval_state=Task.APPROVAL_STATE_NEW,
            )

            self.client.force_authenticate(user=provider_user)

            response = self.client.patch(
                url,
                data=json.dumps(
                    {
                        "task_ids": [
                            task.pk,
                        ],
                        "new_state": Task.APPROVAL_STATE_APPROVED,
                        "approval_annotation": "",
                    }
                ),
                content_type="application/json",
            )
            task.refresh_from_db()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(task.approval_state, Task.APPROVAL_STATE_NEW)

    @mock.patch("axis.messaging.messages.ModernMessage.send")
    def test_change_status(self, send_message):
        provider_user = self.get_admin_user("provider")
        # NEW approval_state tasks are not allowed for status changing
        task = Task.objects.filter(
            assigner__company=provider_user.company, status=Task.COMPLETED_STATUS
        ).first()
        task.approval_state = Task.APPROVAL_STATE_APPROVED
        task.save()

        self.client.force_authenticate(user=provider_user)
        url = reverse("api_v3:scheduling_tasks-change-status")
        status_annotation = "new annotation"
        status_changed_at = task.status_changed_at
        response = self.client.patch(
            url,
            data=json.dumps(
                {
                    "task_ids": [
                        task.pk,
                    ],
                    "new_status": Task.CANCELLED_STATUS,
                    "status_annotation": status_annotation,
                }
            ),
            content_type="application/json",
        )
        task.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(task.status, Task.CANCELLED_STATUS)
        self.assertNotEqual(task.status_changed_at, status_changed_at)
        self.assertEqual(task.status_annotation, status_annotation)
        self.assertEqual(send_message.call_count, 1)

    def test_export_to_cal(self):
        provider_user = self.get_admin_user("provider")
        task = Task.objects.filter(
            assigner__company=provider_user.company, status=Task.COMPLETED_STATUS
        ).first()
        url = reverse("api_v3:scheduling_tasks-export-to-cal")

        self.client.force_authenticate(user=provider_user)
        response = self.client.post(
            url,
            data=json.dumps(
                {
                    "task_ids": [
                        task.pk,
                    ],
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BEGIN:VCALENDAR")
