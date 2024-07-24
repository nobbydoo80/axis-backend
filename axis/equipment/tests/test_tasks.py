"""tasks.py: """


from dateutil.relativedelta import relativedelta
from django.utils import timezone

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import ApiV3Tests
from .mixins import EquipmentFixtureMixin
from ..models import Equipment, EquipmentSponsorStatus
from ..states import EquipmentSponsorStatusStates
from ..tasks import equipment_status_expire_task

__author__ = "Artem Hruzd"
__date__ = "11/04/2019 17:52"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class EquipmentTaskTest(EquipmentFixtureMixin, ApiV3Tests):
    client_class = AxisClient

    def test_equipment_status_expire_task(self):
        all_equipment = Equipment.objects.all()
        active_states_count = EquipmentSponsorStatus.objects.filter(
            state=EquipmentSponsorStatusStates.ACTIVE
        ).count()
        expired_states_count = EquipmentSponsorStatus.objects.filter(
            state=EquipmentSponsorStatusStates.EXPIRED
        ).count()

        self.assertNotEqual(active_states_count, 0)

        for equipment_item in all_equipment:
            equipment_item.calibration_date = timezone.now().date() - relativedelta(years=10)
            equipment_item.calibration_cycle = Equipment.EVERY_2_YEARS_CALIBRATION_CYCLE
            equipment_item.save()

        equipment_status_expire_task()

        new_active_states_count = EquipmentSponsorStatus.objects.filter(
            state=EquipmentSponsorStatusStates.ACTIVE
        ).count()
        new_expired_states_count = EquipmentSponsorStatus.objects.filter(
            state=EquipmentSponsorStatusStates.EXPIRED
        ).count()

        self.assertEqual(new_active_states_count, 0)
        self.assertEqual(new_expired_states_count, active_states_count + expired_states_count)
