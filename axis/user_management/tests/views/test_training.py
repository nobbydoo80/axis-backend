"""training.py: """


import json
from unittest.mock import patch, Mock

from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.user_management.models import Training, TrainingStatus
from axis.user_management.states import TrainingStatusStates
from ..mixins import TrainingTextMixin

__author__ = "Artem Hruzd"
__date__ = "12/23/2019 20:29"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TrainingControlCenterListViewsTest(TrainingTextMixin, AxisTestCase):
    client_class = AxisClient

    def test_login_required(self):
        url = reverse("user_management:training:control_center_new_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("user_management:training:control_center_approved_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("user_management:training:control_center_rejected_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("user_management:training:control_center_expired_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

    @patch(
        "axis.user_management.views.training.control_center_base_list.user_management_app",
        Mock(TRAINING_APPLICABLE_COMPANIES_SLUGS=["aps", "neea"]),
    )
    def test_new_list_as_provider(self):
        training_status = TrainingStatus.objects.filter(state=TrainingStatusStates.NEW).first()
        user = training_status.company.users.first()
        self.assertEqual(user.company.company_type, "provider")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        url = reverse("user_management:training:control_center_new_list")
        response = self.client.get(url, ajax=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        # get training name from column in datatable
        response_ids = list(map(lambda obj: obj["3"], data))
        trainings = Training.objects.filter(
            trainingstatus__company__users__in=[user],
            trainingstatus__state=TrainingStatusStates.NEW,
        )
        expected_ids = list(map(lambda obj: obj.name, trainings))
        self.assertEqual(list(expected_ids), response_ids)

    @patch(
        "axis.user_management.views.training.control_center_base_list.user_management_app",
        Mock(TRAINING_APPLICABLE_COMPANIES_SLUGS=["aps", "neea"]),
    )
    def test_new_list_as_superuser(self):
        user = self.super_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        url = reverse("user_management:training:control_center_new_list")
        response = self.client.get(url, ajax=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        # get training name from column in datatable
        response_ids = list(map(lambda obj: obj["3"], data))
        training = Training.objects.filter(trainingstatus__state=TrainingStatusStates.NEW)
        expected_ids = list(map(lambda obj: obj.name, training))
        self.assertEqual(list(expected_ids), response_ids)
