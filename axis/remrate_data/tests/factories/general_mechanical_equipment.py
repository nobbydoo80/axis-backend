"""general_mechanical_equipment.py: Django factories"""


from .utils import random_sequence
from ...models import GeneralMechanicalEquipment

__author__ = "Steven K"
__date__ = "01/09/2020 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def general_mechanical_equipment_factory(
    simulation, _result_number, _building_number, _source_equipment_number, **kwargs
):
    blg_data = kwargs.pop("blg_data", {})
    kw = {
        "heating_set_point": blg_data.get("heating_setpoint"),
        "cooling_set_point": blg_data.get("cooling_setpoint"),
        "setback_thermostat": blg_data.get("setback_thermostat", False),
        "setup_thermostat": blg_data.get("setup_thermostat", False),
    }
    kw.update(kwargs)
    return GeneralMechanicalEquipment.objects.get_or_create(
        simulation=simulation,
        _result_number=_result_number,
        _source_equipment_number=_source_equipment_number,
        _building_number=_building_number,
        defaults=kw,
    )[0]
