"""api.py: """


from unittest import mock

from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.user_management.models import Training, TrainingStatus
from axis.user_management.states import TrainingStatusStates
from axis.user_management.tests.factories import training_factory, training_status_factory
from axis.user_management.tests.mixins import TrainingTextMixin

__author__ = "Artem Hruzd"
__date__ = "11/05/2019 20:22"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TrainingViewSetTest(TrainingTextMixin, AxisTestCase):
    client_class = AxisClient

    def test_login_required(self):
        url = reverse("apiv2:training-create-approver-report")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)

    @mock.patch("axis.user_management.tasks.training_report_task.delay")
    def test_create_approver_report(self, training_report_task):
        provider_user = self.get_admin_user("provider")
        self.assertTrue(
            self.client.login(username=provider_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login"
            % (provider_user.username, provider_user.pk),
        )

        training_ids = list(Training.objects.values_list("pk", flat=True))
        url = reverse("apiv2:training-create-approver-report")
        response = self.client.get(url, data={"training_ids": training_ids})

        asynchronous_process_document = AsynchronousProcessedDocument.objects.first()

        self.assertEqual(
            response.json()["asynchronous_process_document_url"],
            response.wsgi_request.build_absolute_uri(
                asynchronous_process_document.get_absolute_url()
            ),
        )

        training_report_task.assert_called_once_with(
            asynchronous_process_document_id=asynchronous_process_document.id,
            training_ids=training_ids,
            user_id=provider_user.id,
        )


class TrainingStatusViewSetTest(TrainingTextMixin, AxisTestCase):
    client_class = AxisClient

    def test_login_required(self):
        url = reverse("apiv2:training_status-change-state")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)

    def test_change_state(self):
        """
        Changing state with provider
        """
        # get a rater user that have an equipment with NEW state
        training_status = TrainingStatus.objects.filter(state=TrainingStatusStates.NEW).first()
        neea_user = training_status.company.users.first()

        self.assertTrue(
            self.client.login(username=neea_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (neea_user.username, neea_user.pk),
        )

        url = reverse("apiv2:training_status-change-state")
        response = self.client.post(
            url,
            data={
                "training_ids": [
                    training_status.training.pk,
                ],
                "new_state": TrainingStatusStates.APPROVED,
                "state_notes": "some note",
            },
        )
        training_status.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(training_status.state, TrainingStatusStates.APPROVED)
        self.assertEqual(training_status.state_notes, "some note")

        # try to use unknown state
        response = self.client.post(
            url,
            data={
                "training_ids": [
                    training_status.training.pk,
                ],
                "new_state": "unknown",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["new_state"][0], '"unknown" is not a valid choice.')

    def test_change_state_for_another_provider_without_permission(self):
        """
        Try to change equipment state with provider for user without relationships
        """
        training_status1 = TrainingStatus.objects.filter(state=TrainingStatusStates.NEW).first()

        other_training = training_factory()
        training_status2 = training_status_factory(
            training=other_training, state=TrainingStatusStates.NEW
        )

        neea_user = training_status1.company.users.first()

        self.assertTrue(
            self.client.login(username=neea_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (neea_user.username, neea_user.pk),
        )

        url = reverse("apiv2:training_status-change-state")
        response = self.client.post(
            url,
            data={
                "training_ids": [
                    training_status2.training.pk,
                ],
                "new_state": TrainingStatusStates.APPROVED,
                "state_notes": "some note",
            },
        )
        training_status2.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(training_status2.state, TrainingStatusStates.NEW)

    def test_change_state_for_another_provider_with_superuser(self):
        """
        Superusers can change state for any user
        """
        training_status = TrainingStatus.objects.filter(state=TrainingStatusStates.NEW).first()
        user = self.super_user

        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        url = reverse("apiv2:training_status-change-state")
        response = self.client.post(
            url,
            data={
                "training_ids": [
                    training_status.training.pk,
                ],
                "new_state": TrainingStatusStates.APPROVED,
                "company_id": training_status.company.id,
                "state_notes": "some note",
            },
        )
        training_status.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(training_status.state, TrainingStatusStates.APPROVED)
