"""shared_equipment.py - Axis"""

__author__ = "Steven K"
__date__ = "7/27/21 09:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import random

from .ground_source_heat_pump import ground_source_heat_pump_factory
from .utils import pop_kwargs, random_alphanum
from .water_loop_heat_pump import water_loop_heat_pump_factory
from ...models import SharedEquipment

log = logging.getLogger(__name__)


def shared_equipment_factory(simulation, _result_number, _source_shared_equipment_number, **kwargs):
    system_type = kwargs.pop("type", random.choice([1, 2, 3, 4]))
    distribution_type = kwargs.pop("distribution_type", random.choice([1, 2, 3, 4, 5, 6, 7, 8]))

    water_loop_heat_pump = kwargs.pop("water_loop_heat_pump", None)
    water_loop_heat_pump_kwargs = pop_kwargs("water_loop_heat_pump__", kwargs)

    ground_source_heat_pump = kwargs.pop("ground_source_heat_pump", None)
    ground_source_heat_pump_kwargs = pop_kwargs("ground_source_heat_pump__", kwargs)

    kwrgs = {
        "_source_shared_equipment_number": random.randint(10, 5000),
        "name": f"Shared Equipment {random_alphanum()}",
        "type": random.choice([1, 2, 3, 4]),
        "units_served": random.choice(range(40)),
        "loop_pump_power": random.randint(50, 300) + random.random(),
        "note": random.choice([None, "", "Shared Eq Note", "Shared Eq Note", "Shared Eq Note"]),
        "fan_coil_watts": 0.0,
        "water_loop_heat_pump": water_loop_heat_pump,
    }

    if system_type == 1:  # Boiler
        kwrgs["fuel_type"] = random.choice([1, 2, 3, 4])
        kwrgs["rated_efficiency"] = random.randint(50, 92) + random.random()
        kwrgs["rated_efficiency_unit"] = 1  # AFUE
        kwrgs["boiler_capacity"] = random.randint(10, 40) + random.random()
    elif system_type == 2:  # Chiller
        kwrgs["fuel_type"] = random.choice([1, 2, 3, 4])
        kwrgs["rated_efficiency"] = random.randint(50, 92) + random.random()
        kwrgs["rated_efficiency_unit"] = 2  # kw/Ton
        kwrgs["chiller_capacity"] = random.randint(10, 40) + random.random()
    elif system_type == 3:  # Cooling Tower
        distribution_type = kwrgs["distribution_type"] = 6
    else:  # GSHP
        distribution_type = kwrgs["distribution_type"] = random.choice([7, 8])
        gshp_number = kwargs.pop("gshp_number", random.randint(10, 5000))
        if ground_source_heat_pump is None:
            ground_source_heat_pump = ground_source_heat_pump_factory(
                simulation, _result_number, **ground_source_heat_pump_kwargs
            )
        kwrgs["gshp_number"] = gshp_number
        kwrgs["ground_source_heat_pump"] = ground_source_heat_pump

    # Distribution Types
    if distribution_type == 5:  # Air → Fan Coil
        kwrgs["fan_coil_watts"] = random.randint(10, 40) + random.random()
    elif distribution_type == 6:  # Air → WLHP
        wlhp_number = kwargs.pop("wlhp_number", random.randint(10, 5000))
        if water_loop_heat_pump is None:
            water_loop_heat_pump = water_loop_heat_pump_factory(
                simulation=simulation,
                _result_number=_result_number,
                _source_water_loop_heat_pump_number=wlhp_number,
                **water_loop_heat_pump_kwargs,
            )
        kwrgs["water_loop_heat_pump"] = water_loop_heat_pump
        kwrgs["wlhp_number"] = wlhp_number

    kwrgs.update(kwargs)

    source_equipment_number = kwrgs.pop("_source_shared_equipment_number")
    return SharedEquipment.objects.get_or_create(
        simulation=simulation,
        _result_number=_result_number,
        _source_shared_equipment_number=source_equipment_number,
        defaults=kwrgs,
    )[0]
