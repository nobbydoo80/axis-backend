"""ground_source_heat_pump.py - Axis"""

__author__ = "Steven K"
__date__ = "7/27/21 09:58"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import random

from .utils import random_alphanum
from ...models import GroundSourceHeatPump

log = logging.getLogger(__name__)


def ground_source_heat_pump_factory(simulation, _result_number, **kwargs):
    distribution_type = kwargs.pop("distribution_type", random.randint(0, 1))

    kwrgs = {
        "_source_ground_source_heat_pump_number": random.randint(10, 5000),
        "name": f"GSHP {random_alphanum()}",
        "fuel_type": random.choice([1, 2, 3, 4]),
        "is_desuperheater": random.choice([True, False]),
        "heating_coefficient_of_performance_32f": random.randint(8, 12) + random.random(),
        "heating_coefficient_of_performance_50f": random.randint(8, 12) + random.random(),
        "heating_capacity_32f": random.randint(8, 12) + random.random(),
        "backup_capacity": random.choice([0, random.randint(8, 12) + random.random()]),
        "cooling_energy_efficiency_ratio_77f": random.randint(8, 12) + random.random(),
        "cooling_capacity_77f": random.randint(8, 12) + random.random(),
        "sensible_heat_fraction": random.random(),
        "fan_defaults": False,
        "fan_power": random.randint(8, 12) + random.random(),
        "pump_energy": random.randint(10, 50) + random.random(),
        "pump_energy_type": random.randint(0, 1),
        "note": random.choice(["", "GSHP Note", "GSHP Note", "GSHP Note"]),
    }

    if distribution_type == 1:
        kwrgs["fan_power"] = random.randint(10, 50) + random.random()

    kwrgs.update(kwargs)

    source_gshp_number = kwrgs.pop("_source_ground_source_heat_pump_number")
    return GroundSourceHeatPump.objects.get_or_create(
        simulation=simulation,
        _result_number=_result_number,
        _source_ground_source_heat_pump_number=source_gshp_number,
        defaults=kwrgs,
    )[0]
