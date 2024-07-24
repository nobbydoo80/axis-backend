"""equipment.py: """


from unittest import mock

from django.db.models import Q
from django_fsm import TransitionNotAllowed

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import ApiV3Tests
from axis.equipment.models import EquipmentSponsorStatus
from axis.equipment.states import EquipmentSponsorStatusStates
from ..mixins import EquipmentFixtureMixin

__author__ = "Artem Hruzd"
__date__ = "11/04/2019 21:48"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class EquipmentSponsorStatusModelTest(EquipmentFixtureMixin, ApiV3Tests):
    client_class = AxisClient

    @mock.patch("axis.messaging.messages.ModernMessage.send")
    def test_active_state_transition(self, send_message):
        """
        Check correct behavior for active() state transition
        :param send_message: mock ModernMessage().send
        """
        new_state_equipment_sponsor_status = EquipmentSponsorStatus.objects.filter(
            state=EquipmentSponsorStatusStates.NEW
        ).first()
        # set state_changed_at to check that date updated after state changing
        new_state_equipment_sponsor_status.state_changed_at = None
        new_state_equipment_sponsor_status.approver = None
        new_state_equipment_sponsor_status.save()

        new_state_equipment_sponsor_status.active(user=self.random_user)
        new_state_equipment_sponsor_status.save()

        new_state_equipment_sponsor_status.refresh_from_db()

        self.assertIsNotNone(new_state_equipment_sponsor_status.approver)
        self.assertIsNotNone(new_state_equipment_sponsor_status.state_changed_at)
        send_message.assert_called_once()

        # check that only new state objects can become active
        not_allowed_equipment_sponsor_statuses = EquipmentSponsorStatus.objects.exclude(
            state=EquipmentSponsorStatusStates.NEW
        )

        self.assertGreater(not_allowed_equipment_sponsor_statuses.count(), 0)

        for not_allowed_equipment_sponsor_status in not_allowed_equipment_sponsor_statuses:
            with self.assertRaises(TransitionNotAllowed):
                not_allowed_equipment_sponsor_status.active()

    @mock.patch("axis.messaging.messages.ModernMessage.send")
    def test_reject_state_transition(self, send_message):
        """
        Check correct behavior for reject() state transition
        :param send_message: mock ModernMessage().send
        """
        new_state_equipment_sponsor_status = EquipmentSponsorStatus.objects.filter(
            state=EquipmentSponsorStatusStates.NEW
        ).first()
        # set state_changed_at to check that date updated after state changing
        new_state_equipment_sponsor_status.state_changed_at = None
        new_state_equipment_sponsor_status.approver = None
        new_state_equipment_sponsor_status.save()

        new_state_equipment_sponsor_status.reject(user=self.random_user)
        new_state_equipment_sponsor_status.save()

        new_state_equipment_sponsor_status.refresh_from_db()

        self.assertIsNotNone(new_state_equipment_sponsor_status.approver)
        self.assertIsNotNone(new_state_equipment_sponsor_status.state_changed_at)
        send_message.assert_called_once()

        # check that only new and active state objects can become rejected
        not_allowed_equipment_sponsor_statuses = EquipmentSponsorStatus.objects.exclude(
            Q(state=EquipmentSponsorStatusStates.NEW) | Q(state=EquipmentSponsorStatusStates.ACTIVE)
        )

        self.assertGreater(not_allowed_equipment_sponsor_statuses.count(), 0)
        for not_allowed_equipment_sponsor_status in not_allowed_equipment_sponsor_statuses:
            with self.assertRaises(TransitionNotAllowed):
                not_allowed_equipment_sponsor_status.active()

    @mock.patch("axis.messaging.messages.ModernMessage.send")
    def test_expire_state_transition(self, send_message):
        """
        Check correct behavior for expire() state transition
        :param send_message: mock ModernMessage().send
        """
        active_state_equipment_sponsor_status = EquipmentSponsorStatus.objects.filter(
            state=EquipmentSponsorStatusStates.ACTIVE
        ).first()
        # set state_changed_at to check that date updated after state changing
        active_state_equipment_sponsor_status.state_changed_at = None
        active_state_equipment_sponsor_status.approver = self.random_user
        active_state_equipment_sponsor_status.save()

        active_state_equipment_sponsor_status.expire()
        active_state_equipment_sponsor_status.save()

        active_state_equipment_sponsor_status.refresh_from_db()

        self.assertIsNone(active_state_equipment_sponsor_status.approver)
        self.assertIsNotNone(active_state_equipment_sponsor_status.state_changed_at)
        send_message.assert_called_once()

        # check that only active state objects can become rejected
        not_allowed_equipment_sponsor_statuses = EquipmentSponsorStatus.objects.exclude(
            Q(state=EquipmentSponsorStatusStates.NEW) | Q(state=EquipmentSponsorStatusStates.ACTIVE)
        )

        self.assertGreater(not_allowed_equipment_sponsor_statuses.count(), 0)
        for not_allowed_equipment_sponsor_status in not_allowed_equipment_sponsor_statuses:
            with self.assertRaises(TransitionNotAllowed):
                not_allowed_equipment_sponsor_status.active()
