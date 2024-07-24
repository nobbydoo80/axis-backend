"""duct_system.py - simulation"""

import logging
import random

from .utils import get_factory_from_fields, pop_kwargs
from ...models import DuctSystem, Duct

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "9/14/20 14:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def duct_factory(simulation, duct_system, **kw):
    kwargs = get_factory_from_fields(Duct)
    kwargs["building"] = simulation.building
    kwargs["area"] = random.choice(range(99))
    # DUCT_LOCATIONS Note remove 0.
    kwargs["location"] = random.choice([1, 2, 3, 4, 5, 16, 6, 7, 8, 10, 14, 13, 9, 15, 12])
    kwargs.update(**kw)

    return Duct.objects.create(simulation=simulation, duct_system=duct_system, **kwargs)


def duct_system_factory(simulation, heating_equipment_number=-1, cooling_equipment_number=-1, **kw):
    duct_kwargs = pop_kwargs("duct__", kw)
    duct_pair_count = kw.pop("duct_pair_count", random.choice([0, 0, 1, 2, 3]))

    kwargs = get_factory_from_fields(DuctSystem)
    kwargs["building"] = simulation.building
    kwargs["distribution_system_efficiency"] = random.random()
    kwargs["supply_area"] = random.choice(range(500)) + random.random()
    kwargs["return_area"] = random.choice(range(500)) + random.random()
    kwargs["leakage_unit"] = random.choice([2, 12, 11, 10, 1, 5, 7])
    kwargs["number_of_return_registers"] = random.choice(range(20))
    kwargs["conditioned_floor_area"] = random.choice(range(2000)) + random.random()
    kwargs.pop("heating_equipment_number", None)
    kwargs.pop("cooling_equipment_number", None)
    kwargs.update(**kw)
    ds = DuctSystem.objects.create(
        simulation=simulation,
        heating_equipment_number=heating_equipment_number,
        cooling_equipment_number=cooling_equipment_number,
        **kwargs,
    )

    duct_qty = 0
    while True:
        if duct_qty >= duct_pair_count:
            break
        area = int(round(100.0 / float(duct_pair_count)))
        supply_kw = duct_kwargs.copy()
        supply_kw["type"] = 1
        supply_kw["area"] = area
        supply_d = duct_factory(simulation=simulation, duct_system=ds, **supply_kw)
        return_kw = duct_kwargs.copy()
        return_kw["type"] = 2
        return_kw["area"] = area
        return_kw["location"] = supply_d.location
        duct_factory(simulation=simulation, duct_system=ds, **return_kw)
        duct_qty += 1

    return ds
