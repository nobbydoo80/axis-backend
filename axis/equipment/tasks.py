from celery import shared_task
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from .models import Equipment
from .states import EquipmentSponsorStatusStates

__author__ = "Artem Hruzd"
__date__ = "11/04/2019 17:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


@shared_task
def equipment_status_expire_task():
    """
    Equipment should transition to "Expired" based on a calculation of
    "Calibration Date" plus the "Calibration Cycle" value.
    So if cycle is set to "Every 2 Years",
    the equipment should transition to expired 2 years from the "Calibration Date"
    """
    equipment = Equipment.objects.filter(
        equipmentsponsorstatus__state=EquipmentSponsorStatusStates.ACTIVE
    ).prefetch_related("sponsors")

    calibration_cycle_timedelta_map = {
        Equipment.ANNUAL_CALIBRATION_CYCLE: relativedelta(years=1),
        Equipment.EVERY_2_YEARS_CALIBRATION_CYCLE: relativedelta(years=2),
        Equipment.EVERY_3_YEARS_CALIBRATION_CYCLE: relativedelta(years=3),
    }

    for equipment_item in equipment:
        calibration_date = equipment_item.calibration_date
        calibration_cycle = equipment_item.calibration_cycle
        date_diff = timezone.now().date() - calibration_cycle_timedelta_map[calibration_cycle]
        if calibration_date < date_diff:
            for expire_equipment_sponsor_status in equipment_item.equipmentsponsorstatus_set.all():
                expire_equipment_sponsor_status.expire()
                expire_equipment_sponsor_status.save()
