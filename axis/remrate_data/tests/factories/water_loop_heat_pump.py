"""water_loop_heat_pump.py - Axis"""

__author__ = "Steven K"
__date__ = "7/27/21 09:20"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import random

from .utils import random_alphanum
from ...models.water_loop_heat_pump import WaterLoopHeatPump

log = logging.getLogger(__name__)


def water_loop_heat_pump_factory(simulation, _result_number, **kwargs):
    kwrgs = {
        "_source_water_loop_heat_pump_number": random.randint(100, 1000),
        "name": f"WLHP - {random_alphanum()}",
        "heating_efficiency": random.randint(3, 10) + random.random(),
        "heating_capacity": random.randint(12, 20) + random.random(),
        "cooling_efficiency": random.randint(12, 20) + random.random(),
        "cooling_capacity": random.randint(8, 12) + random.random(),
        "sensible_heat_fraction": random.random(),
        "note": random.choice([None, "", "WLHP Note", "WLHP Note", "WLHP Note"]),
    }
    kwrgs.update(kwargs)

    source_wlhp = kwrgs.pop("_source_water_loop_heat_pump_number")
    return WaterLoopHeatPump.objects.get_or_create(
        simulation=simulation,
        _result_number=_result_number,
        _source_water_loop_heat_pump_number=source_wlhp,
        defaults=kwrgs,
    )[0]
