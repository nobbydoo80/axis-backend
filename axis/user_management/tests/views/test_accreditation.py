"""accreditation.py: """


import json
from unittest.mock import patch, Mock

from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.user_management.models import Accreditation
from ..mixins import AccreditationTestMixin

__author__ = "Artem Hruzd"
__date__ = "12/24/2019 12:44"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class AccreditationControlCenterListViewsTest(AccreditationTestMixin, AxisTestCase):
    client_class = AxisClient

    def test_login_required(self):
        url = reverse("user_management:accreditation:control_center_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

    @patch(
        "axis.user_management.views.accreditation." "control_center_list.user_management_app",
        Mock(ACCREDITATION_APPLICABLE_COMPANIES_SLUGS=["aps", "neea"]),
    )
    def test_list_as_provider(self):
        provider = self.get_admin_user("provider")
        accreditations = Accreditation.objects.filter(approver=provider).all()

        self.assertTrue(
            self.client.login(username=provider.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (provider.username, provider.pk),
        )
        url = reverse("user_management:accreditation:control_center_list")
        response = self.client.get(url, ajax=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        # get accreditation_id from column in datatable
        response_ids = list(map(lambda obj: obj["4"], data))
        expected_ids = list(map(lambda obj: obj.accreditation_id, accreditations))
        self.assertEqual(list(expected_ids), response_ids)

    @patch(
        "axis.user_management.views.accreditation." "control_center_list.user_management_app",
        Mock(ACCREDITATION_APPLICABLE_COMPANIES_SLUGS=["aps", "neea"]),
    )
    def test_list_as_superuser(self):
        user = self.super_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        url = reverse("user_management:accreditation:control_center_list")
        response = self.client.get(url, ajax=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        # get accreditation_id from column in datatable
        response_ids = list(map(lambda obj: obj["4"], data))
        accreditations = Accreditation.objects.all()
        expected_ids = list(map(lambda obj: obj.accreditation_id, accreditations))
        self.assertEqual(list(expected_ids), response_ids)
