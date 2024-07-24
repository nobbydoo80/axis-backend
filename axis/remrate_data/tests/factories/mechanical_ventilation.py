"""mechanical_ventilation.py - simulation"""

__author__ = "Steven K"
__date__ = "7/26/21 08:59"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import random

from .utils import random_alphanum
from ...models import Ventilation

log = logging.getLogger(__name__)


def mechanical_ventilation_factory(simulation, _result_number, _building_number, **kwargs):
    """Mechanical Ventilation Factory"""

    if tuple(simulation.numerical_version) < (16, 1, 0):
        return

    outside_air = random.randint(0, 100)

    kwrgs = {
        "name": f"Ventilation {random_alphanum()}",
        "type": random.choice([1, 2, 3, 4]),
        "rate": random.randint(5, 50),
        "hours_per_day": random.randint(1, 24),
        "fan_power": random.randint(50, 350),
        "ashrae_recovery_efficiency": random.randint(70, 75) + random.random(),
        "atre_recovery_efficiency": random.randint(75, 80) + random.random(),
        "not_measured": random.choice([0, 1]),
        "use_defaults": random.choice([0, 1]),
        "shared_multi_family_system": random.choice([0, 1]),
        "total_shared_system_cfm": 0,
        "uses_ecm_fan": random.choice([0, 1]),
        "duct_system_number": -1,
        "heating_equipment_number": -1,
        "cooling_equipment_number": -1,
        "outside_air_pct": outside_air,
        "recirculated_air_pct": 100.0 - outside_air,
    }
    if kwrgs["shared_multi_family_system"]:
        kwrgs["total_shared_system_cfm"] = random.randint(5, 50) + random.random()

    kwrgs.update(kwargs)

    name = kwrgs.pop("name")

    return Ventilation.objects.get_or_create(
        simulation=simulation,
        name=name,
        _result_number=_result_number,
        _source_building_number=_building_number,
        defaults=kwrgs,
    )
