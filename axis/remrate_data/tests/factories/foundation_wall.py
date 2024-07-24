"""foundation_wall.py - simulation"""

import logging
import random

from .utils import pop_kwargs, get_factory_from_fields
from ...models import FoundationWall, FoundationWallType

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "7/8/20 16:39"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def foundation_wall_type_factory(simulation, **kwargs):
    """Foundation Wall Type"""
    kwrgs = get_factory_from_fields(FoundationWallType)
    kwrgs["interior_insulation_top_type"] = random.randint(1, 4)
    kwrgs["interior_insulation_bottom_type"] = random.randint(1, 4)
    kwrgs["exterior_insulation_top_type"] = random.randint(1, 4)
    kwrgs["exterior_insulation_bottom_type"] = random.randint(1, 4)
    kwrgs.update(kwargs)
    return FoundationWallType.objects.create(simulation=simulation, **kwrgs)


def foundation_wall_factory(simulation, **kwargs):
    """Foundation Wall"""
    wall_type = kwargs.pop("wall_type", None)

    if wall_type is None:
        wall_type = foundation_wall_type_factory(simulation, **pop_kwargs("wall_type__", kwargs))

    kwrgs = get_factory_from_fields(FoundationWall)

    location_choices = [201, 202, 203, 205, 206, 207, 208, 209, 210, 211, 212, 214, 215, 216, 213]
    if simulation.numerical_version >= (16, 1):
        location_choices = [
            229,
            230,
            231,
            232,
            233,
            234,
            235,
            236,
            237,
            238,
            214,
            215,
            216,
            239,
            240,
            241,
            242,
            243,
            244,
            207,
            208,
            209,
            245,
            246,
            247,
            248,
            210,
            211,
            212,
            249,
            250,
            251,
            252,
        ]
    kwrgs["location"] = random.choice(location_choices)
    kwrgs.update(kwargs)

    building = kwrgs.pop("building", simulation.building)
    return FoundationWall.objects.create(
        simulation=simulation, building=building, type=wall_type, **kwrgs
    )
