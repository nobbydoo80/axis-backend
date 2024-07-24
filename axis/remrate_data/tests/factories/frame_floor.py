"""frame_floor.py - simulation"""

import logging
import random

from .utils import pop_kwargs, get_factory_from_fields
from ...models import FloorType, FrameFloor
from .surface_type import surface_type_factory

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "9/24/20 13:55"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def floor_type_factory(simulation, **kwargs):
    return surface_type_factory(FloorType, simulation, **kwargs)


def frame_floor_factory(simulation, **kwargs):
    floor_type = kwargs.pop("floor_type", None)
    if floor_type is None:
        floor_type = floor_type_factory(simulation, **pop_kwargs("floor_type__", kwargs))

    kwrgs = get_factory_from_fields(FrameFloor)
    kwrgs["u_value"] = floor_type.composite_type.u_value
    kwrgs["area"] = random.randint(200, 1500) + random.random()
    location_choices = [201, 202, 203, 205, 206]
    if simulation.numerical_version >= (16, 1):
        location_choices = [201, 202, 225, 205, 206, 203, 213, 226, 227, 228]
    kwrgs["location"] = random.choice(location_choices)
    kwrgs.update(kwargs)

    building = kwrgs.pop("building", simulation.building)
    return FrameFloor.objects.create(
        simulation=simulation, building=building, type=floor_type, **kwrgs
    )
