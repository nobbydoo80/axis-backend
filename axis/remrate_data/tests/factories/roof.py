"""roof.py - simulation"""

import logging
import random

from .utils import get_factory_from_fields, pop_kwargs
from ...models import CeilingType, Roof, Simulation as RemSimulation
from .surface_type import surface_type_factory

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "9/28/20 13:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def ceiling_type_factory(simulation, **kwargs):
    return surface_type_factory(CeilingType, simulation, **kwargs)


def roof_factory(simulation: RemSimulation, **kwargs) -> Roof:
    ceiling_type = kwargs.pop("ceiling_type", None)
    if ceiling_type is None:
        ceiling_type = ceiling_type_factory(simulation, **pop_kwargs("ceiling_type__", kwargs))

    kwrgs = get_factory_from_fields(Roof)
    kwrgs["area"] = random.uniform(1000, 4000)
    kwrgs["color"] = random.randint(1, 3)
    kwrgs["u_value"] = ceiling_type.composite_type.u_value
    kwrgs.update(kwargs)

    building = kwrgs.pop("building", simulation.building)
    return Roof.objects.create(simulation=simulation, building=building, type=ceiling_type, **kwrgs)
