"""factory.py: Django equipment factories"""


import logging

from django.utils import timezone

from axis.company.tests.factories import rater_organization_factory, provider_organization_factory
from axis.core.tests.factories import provider_user_factory
from axis.core.utils import random_sequence
from axis.equipment.models import Equipment, EquipmentSponsorStatus
from axis.equipment.states import EquipmentSponsorStatusStates

__author__ = "Steven Klass"
__date__ = "4/17/13 9:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def equipment_factory(**kwargs):
    owner_company = kwargs.pop("owner_company", rater_organization_factory())
    kwrgs = {
        "equipment_type": Equipment.MANOMETER_EQUIPMENT_TYPE,
        "calibration_date": timezone.now(),
        "calibration_cycle": Equipment.ANNUAL_CALIBRATION_CYCLE,
        "calibration_company": f"{random_sequence(4)}",
        "brand": f"{random_sequence(4)}",
        "equipment_model": f"{random_sequence(4)}",
        "serial": f"{random_sequence(4)}",
        "description": f"{random_sequence(4)}",
        "notes": f"{random_sequence(4)}",
    }

    kwrgs.update(kwargs)

    equipment = Equipment.objects.create(owner_company=owner_company, **kwrgs)
    return equipment


def equipment_sponsor_status_factory(**kwargs):
    equipment = kwargs.pop("equipment")
    company = kwargs.pop("company", provider_organization_factory())
    approver = kwargs.pop("approver", provider_user_factory(company=company))
    kwrgs = {"state_changed_at": timezone.now(), "state": EquipmentSponsorStatusStates.NEW}

    kwrgs.update(kwargs)
    equipment_sponsor_status = EquipmentSponsorStatus.objects.create(
        equipment=equipment, company=company, approver=approver, **kwrgs
    )
    return equipment_sponsor_status
