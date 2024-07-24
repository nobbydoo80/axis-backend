"""views.py: """


import json

from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import ApiV3Tests
from .mixins import EquipmentFixtureMixin
from ..models import Equipment
from ..states import EquipmentSponsorStatusStates

__author__ = "Artem Hruzd"
__date__ = "11/05/2019 18:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class ControlCenterListViewsTest(EquipmentFixtureMixin, ApiV3Tests):
    client_class = AxisClient

    def test_login_required(self):
        url = reverse("equipment:control_center_new_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("equipment:control_center_active_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("equipment:control_center_rejected_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("equipment:control_center_expired_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

    def test_new_list_as_superuser(self):
        user = self.super_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        url = reverse("equipment:control_center_new_list")
        response = self.client.get(url, ajax=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        # get pk from first column in datatable
        response_ids = list(map(lambda obj: obj["1"], data))
        equipment = Equipment.objects.filter(
            equipmentsponsorstatus__state=EquipmentSponsorStatusStates.NEW
        )
        expected_ids = list(map(lambda obj: obj.get_equipment_type_display(), equipment))
        self.assertEqual(list(expected_ids), response_ids)
