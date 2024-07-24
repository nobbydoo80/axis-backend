"""accreditation.py: """


__author__ = "Artem Hruzd"
__date__ = "12/25/2019 18:36"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import copy
import json
import random
from unittest import mock

from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.user_management.models import Accreditation
from axis.user_management.tests.mixins import AccreditationTestMixin


class UserAccreditationViewSetTest(AccreditationTestMixin, AxisTestCase):
    client_class = AxisClient

    @mock.patch("axis.messaging.messages.ModernMessage.send")
    def test_create_accreditation_with_provider(self, send_message):
        provider_user = self.get_admin_user("provider")
        rater_user = self.get_admin_user("rater")
        self.assertTrue(
            self.client.login(username=provider_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login"
            % (provider_user.username, provider_user.pk),
        )
        accreditation_data = {
            "trainee_id": rater_user.id,  # specify trainee_id as region dependency
            "name": Accreditation.NGBS_2020_NAME,
            "accreditation_id": "Random address",
            "role": random.choice(Accreditation.ROLE_CHOICES)[0],
            "state": random.choice(Accreditation.STATE_CHOICES)[0],
            "accreditation_cycle": random.choice(Accreditation.ACCREDITATION_CYCLE_CHOICES)[0],
            "date_initial": "1993-11-27",
            "date_last": "1999-11-27",
            "notes": "test",
        }

        url = "{}?machinery=UserAccreditationExamineMachinery".format(
            reverse("apiv2:user_accreditation-list")
        )

        response = self.client.post(url, data=accreditation_data)
        self.assertEqual(response.status_code, 201)

        created_accreditation = Accreditation.objects.order_by("id").last()
        self.assertEqual(Accreditation.NGBS_2020_NAME, accreditation_data["name"])
        self.assertEqual(created_accreditation.trainee.id, accreditation_data["trainee_id"])
        self.assertEqual(created_accreditation.approver, provider_user)
        self.assertEqual(created_accreditation.state, accreditation_data["state"])
        self.assertEqual(created_accreditation.notes, accreditation_data["notes"])

        send_message.assert_called_once()

    def test_update_accreditation_with_provider(self):
        provider_user = self.get_admin_user("provider")
        self.assertTrue(
            self.client.login(username=provider_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login"
            % (provider_user.username, provider_user.pk),
        )
        accreditation = Accreditation.objects.filter(
            approver=provider_user, state=Accreditation.INACTIVE_STATE
        ).first()

        old_state_changed_at = copy.copy(accreditation.state_changed_at)
        accreditation_data = {
            "name": Accreditation.NGBS_2012_NAME,
            "state": Accreditation.ACTIVE_STATE,
        }

        url = "{}?machinery=UserAccreditationExamineMachinery".format(
            reverse("apiv2:user_accreditation-detail", args=(accreditation.id,))
        )

        response = self.client.patch(
            url, data=json.dumps(accreditation_data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        accreditation.refresh_from_db()
        self.assertEqual(accreditation.state, accreditation_data["state"])
        self.assertEqual(accreditation.name, accreditation_data["name"])
        self.assertNotEqual(accreditation.state_changed_at, old_state_changed_at)
