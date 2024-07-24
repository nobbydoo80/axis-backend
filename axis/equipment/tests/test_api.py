"""api.py: """


from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import ApiV3Tests
from axis.equipment.tests.mixins import EquipmentFixtureMixin
from axis.equipment.tests.factories import equipment_factory, equipment_sponsor_status_factory
from ..models import EquipmentSponsorStatus
from ..states import EquipmentSponsorStatusStates

__author__ = "Artem Hruzd"
__date__ = "11/05/2019 20:22"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class EquipmentSponsorStatusViewSetTest(EquipmentFixtureMixin, ApiV3Tests):
    client_class = AxisClient

    def test_login_required(self):
        url = reverse("apiv2:equipment_sponsor_status-change-state")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)

    def test_change_state(self):
        """
        Changing state with provider
        """
        # get a rater user that have an equipment with NEW state
        equipment_status = EquipmentSponsorStatus.objects.filter(
            state=EquipmentSponsorStatusStates.NEW
        ).first()
        neea_user = equipment_status.company.users.first()

        self.assertTrue(
            self.client.login(username=neea_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (neea_user.username, neea_user.pk),
        )

        url = reverse("apiv2:equipment_sponsor_status-change-state")
        response = self.client.post(
            url,
            data={
                "equipment_ids": [
                    equipment_status.equipment.pk,
                ],
                "new_state": EquipmentSponsorStatusStates.ACTIVE,
                "state_notes": "some notes",
            },
        )
        equipment_status.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(equipment_status.state, EquipmentSponsorStatusStates.ACTIVE)
        self.assertEqual(equipment_status.state_notes, "some notes")

        # try to use unknown state
        response = self.client.post(
            url,
            data={
                "equipment_ids": [
                    equipment_status.equipment.pk,
                ],
                "new_state": "unknown",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["new_state"][0], '"unknown" is not a valid choice.')

    def test_change_state_for_another_provider_without_permission(self):
        """
        Try to change equipment state with provider for another company
        """
        equipment_status1 = EquipmentSponsorStatus.objects.filter(
            state=EquipmentSponsorStatusStates.NEW
        ).first()

        other_company_equipment = equipment_factory()
        equipment_status2 = equipment_sponsor_status_factory(
            equipment=other_company_equipment, state=EquipmentSponsorStatusStates.NEW
        )

        neea_user = equipment_status1.company.users.first()

        self.assertTrue(
            self.client.login(username=neea_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (neea_user.username, neea_user.pk),
        )

        url = reverse("apiv2:equipment_sponsor_status-change-state")
        response = self.client.post(
            url,
            data={
                "equipment_ids": [
                    equipment_status2.equipment.pk,
                ],
                "new_state": EquipmentSponsorStatusStates.ACTIVE,
            },
        )
        equipment_status2.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(equipment_status2.state, EquipmentSponsorStatusStates.NEW)

    def test_change_state_for_another_provider_with_superuser(self):
        """
        Superusers can change state for any company
        """
        equipment_status = EquipmentSponsorStatus.objects.filter(
            state=EquipmentSponsorStatusStates.NEW
        ).first()
        user = self.super_user

        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        url = reverse("apiv2:equipment_sponsor_status-change-state")
        response = self.client.post(
            url,
            data={
                "equipment_ids": [
                    equipment_status.equipment.pk,
                ],
                "new_state": EquipmentSponsorStatusStates.ACTIVE,
                "company_id": equipment_status.company.id,
                "state_notes": "some notes",
            },
        )
        equipment_status.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(equipment_status.state, EquipmentSponsorStatusStates.ACTIVE)
