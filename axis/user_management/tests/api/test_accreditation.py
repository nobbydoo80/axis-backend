"""accreditation.py: """


import json
from unittest import mock

from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.user_management.models import Accreditation
from axis.user_management.tests.mixins import AccreditationTestMixin

__author__ = "Artem Hruzd"
__date__ = "12/24/2019 13:40"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class AccreditationViewSetTest(AccreditationTestMixin, AxisTestCase):
    client_class = AxisClient

    def test_login_required(self):
        url = reverse("apiv2:accreditation-create-approver-report")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)

    @mock.patch("axis.user_management.tasks.accreditation_report_task.delay")
    def test_create_approver_report(self, accreditation_report_task):
        provider_user = self.get_admin_user("provider")
        self.assertTrue(
            self.client.login(username=provider_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login"
            % (provider_user.username, provider_user.pk),
        )

        accreditation_ids = list(Accreditation.objects.values_list("pk", flat=True))
        url = reverse("apiv2:accreditation-create-approver-report")
        response = self.client.get(url, data={"accreditation_ids": accreditation_ids})

        asynchronous_process_document = AsynchronousProcessedDocument.objects.first()

        self.assertEqual(
            response.json()["asynchronous_process_document_url"],
            response.wsgi_request.build_absolute_uri(
                asynchronous_process_document.get_absolute_url()
            ),
        )

        accreditation_report_task.assert_called_once_with(
            asynchronous_process_document_id=asynchronous_process_document.id,
            accreditation_ids=accreditation_ids,
            user_id=provider_user.id,
        )

    @mock.patch("axis.user_management.tasks.customer_hirl_accreditation_report_task.delay")
    def test_create_customer_hirl_report(self, customer_hirl_accreditation_report_task):
        provider_user = self.get_admin_user("provider")
        self.assertTrue(
            self.client.login(username=provider_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login"
            % (provider_user.username, provider_user.pk),
        )

        url = reverse("apiv2:accreditation-create-customer-hirl-report")
        response = self.client.get(url)

        asynchronous_process_document = AsynchronousProcessedDocument.objects.first()

        self.assertEqual(
            response.json()["asynchronous_process_document_url"],
            response.wsgi_request.build_absolute_uri(
                asynchronous_process_document.get_absolute_url()
            ),
        )

        customer_hirl_accreditation_report_task.assert_called_once_with(
            asynchronous_process_document_id=asynchronous_process_document.id,
            user_id=provider_user.id,
        )

    def test_change_state(self):
        """
        Changing state with provider
        """
        # get an approver user that have an accreditation with INACTIVE STATE
        accreditation = Accreditation.objects.filter(state=Accreditation.INACTIVE_STATE).first()
        neea_user = accreditation.approver

        self.assertTrue(
            self.client.login(username=neea_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (neea_user.username, neea_user.pk),
        )

        url = reverse("apiv2:accreditation-change-state")
        response = self.client.patch(
            url,
            data=json.dumps(
                {
                    "accreditation_ids": [
                        accreditation.pk,
                    ],
                    "new_state": Accreditation.ACTIVE_STATE,
                }
            ),
            content_type="application/json",
        )
        accreditation.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(accreditation.state, Accreditation.ACTIVE_STATE)

        # try to use unknown state
        response = self.client.patch(
            url,
            data=json.dumps(
                {
                    "accreditation_ids": [
                        accreditation.pk,
                    ],
                    "new_state": "unknown",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["new_state"][0], '"unknown" is not a valid choice.')

    def test_change_state_without_permission(self):
        accreditation = Accreditation.objects.filter(state=Accreditation.INACTIVE_STATE).first()
        trainee = accreditation.trainee

        self.assertTrue(
            self.client.login(username=trainee.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (trainee.username, trainee.pk),
        )

        url = reverse("apiv2:accreditation-change-state")
        response = self.client.patch(
            url,
            data=json.dumps(
                {
                    "accreditation_ids": [
                        accreditation.pk,
                    ],
                    "new_state": Accreditation.ACTIVE_STATE,
                }
            ),
            content_type="application/json",
        )
        accreditation.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(accreditation.state, Accreditation.INACTIVE_STATE)
