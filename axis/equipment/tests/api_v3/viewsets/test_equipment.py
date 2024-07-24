__author__ = "Artem Hruzd"
__date__ = "11/05/2019 20:22"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from unittest import mock
from unittest.mock import patch, Mock

from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.factories import provider_admin_factory
from axis.core.tests.testcases import ApiV3Tests
from axis.equipment.models import Equipment, EquipmentSponsorStatus
from axis.equipment.states import EquipmentSponsorStatusStates
from axis.equipment.tests.mixins import EquipmentFixtureMixin


class EquipmentViewSetTest(EquipmentFixtureMixin, ApiV3Tests):
    client_class = AxisClient

    @mock.patch(
        "axis.equipment.api_v3.viewsets.equipment.EquipmentCreatedSponsorCompanyMessage.send"
    )
    @patch(
        "axis.equipment.api_v3.serializers.equipment.equipment_app",
        Mock(
            EQUIPMENT_APPLICABLE_REQUIREMENTS={
                "neea": [
                    "wa-code-study",
                ]
            }
        ),
    )
    def test_create_equipment(self, create_message):
        rater_user = self.get_admin_user("rater")
        provider_user = self.get_admin_user("provider")
        self.assertTrue(
            self.client.login(username=rater_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (rater_user.username, rater_user.pk),
        )
        equipment_data = {
            "owner_company": rater_user.company.id,
            "equipment_type": Equipment.ANNUAL_CALIBRATION_CYCLE,
            "brand": "brand",
            "equipment_model": "model",
            "serial": "serial",
            "calibration_date": "1993-12-27",
            "calibration_company": "calibration company",
            "description": "test",
            "notes": "test",
        }

        url = reverse("api_v3:equipment-list")

        response = self.client.post(url, data=equipment_data)
        self.assertEqual(response.status_code, 201)

        created_equipment = Equipment.objects.last()
        self.assertEqual(created_equipment.owner_company.id, equipment_data["owner_company"])
        self.assertEqual(created_equipment.equipment_type, equipment_data["equipment_type"])
        self.assertEqual(created_equipment.notes, equipment_data["notes"])

        create_message.assert_called_once()

        equipment_company_status = EquipmentSponsorStatus.objects.filter(
            equipment=created_equipment,
            company=provider_user.company,
            state=EquipmentSponsorStatusStates.NEW,
        ).first()
        self.assertIsNotNone(equipment_company_status)

    @mock.patch(
        "axis.equipment.api_v3.viewsets.equipment.EquipmentCreatedSponsorCompanyMessage.send"
    )
    @mock.patch(
        "axis.equipment.models.equipment_sponsor_status.EquipmentSponsorStatusStateChangedMessage.send"
    )
    @patch(
        "axis.equipment.api_v3.serializers.equipment.equipment_app",
        Mock(
            EQUIPMENT_APPLICABLE_REQUIREMENTS={
                "neea": [
                    "wa-code-study",
                ]
            }
        ),
    )
    def test_create_equipment_with_provider(self, state_changed_message, create_message):
        rater_user = self.get_admin_user("rater")
        provider_user = self.get_admin_user("provider")
        self.assertTrue(
            self.client.login(username=provider_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login"
            % (provider_user.username, provider_user.pk),
        )

        equipment_data = {
            "owner_company": rater_user.company.id,
            "equipment_type": Equipment.ANNUAL_CALIBRATION_CYCLE,
            "brand": "brand",
            "equipment_model": "model",
            "serial": "serial",
            "calibration_date": "1993-12-27",
            "calibration_company": "calibration company",
            "description": "test",
            "notes": "test",
        }

        url = reverse("api_v3:equipment-list")

        response = self.client.post(url, data=equipment_data)
        self.assertEqual(response.status_code, 201)

        created_equipment = Equipment.objects.last()

        self.assertEqual(create_message.call_count, 1)
        self.assertEqual(state_changed_message.call_count, 1)

        equipment_company_status = EquipmentSponsorStatus.objects.filter(
            equipment=created_equipment,
            company=provider_user.company,
            state=EquipmentSponsorStatusStates.ACTIVE,
        ).first()
        self.assertIsNotNone(equipment_company_status)

    def test_copy_expired_equipment(self):
        expired_equipment = (
            Equipment.objects.filter(
                equipmentsponsorstatus__state=EquipmentSponsorStatusStates.EXPIRED
            )
            .select_related("expired_equipment")
            .first()
        )
        user = expired_equipment.owner_company.users.first()

        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        self.assertIsNone(expired_equipment.expired_equipment)

        url = reverse(
            "api_v3:equipment-copy-expired-equipment", kwargs={"pk": expired_equipment.pk}
        )

        response = self.client.post(url)

        expired_equipment.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(expired_equipment.expired_equipment)

    def test_copy_expired_for_another_provider_without_permissions(self):
        expired_equipment = (
            Equipment.objects.filter(
                equipmentsponsorstatus__state=EquipmentSponsorStatusStates.EXPIRED
            )
            .select_related("expired_equipment")
            .first()
        )
        other_provider = provider_admin_factory()

        self.assertTrue(
            self.client.login(username=other_provider.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login"
            % (other_provider.username, other_provider.pk),
        )

        self.assertIsNone(expired_equipment.expired_equipment)

        url = reverse(
            "api_v3:equipment-copy-expired-equipment", kwargs={"pk": expired_equipment.pk}
        )

        response = self.client.post(url)

        expired_equipment.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertIsNone(expired_equipment.expired_equipment)

    def test_copy_expired_equipment_with_superuser(self):
        expired_equipment = (
            Equipment.objects.filter(
                equipmentsponsorstatus__state=EquipmentSponsorStatusStates.EXPIRED
            )
            .select_related("expired_equipment")
            .first()
        )
        user = self.super_user

        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        self.assertIsNone(expired_equipment.expired_equipment)

        url = reverse(
            "api_v3:equipment-copy-expired-equipment", kwargs={"pk": expired_equipment.pk}
        )

        response = self.client.post(url)

        expired_equipment.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(expired_equipment.expired_equipment)
