"""door.py - simulation"""

import logging
import random

from .utils import get_factory_from_fields, pop_kwargs
from ...models import DoorType, Door

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "9/30/20 13:53"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def door_type_factory(simulation, **kwargs):
    """Door Type Factory"""
    kwrgs = get_factory_from_fields(DoorType)
    kwrgs.update(kwargs)
    kwrgs["name"] = kwrgs["name"] if kwrgs["name"] else "No - Name"
    return DoorType.objects.get_or_create(simulation=simulation, **kwrgs)[0]


def door_factory(simulation, building, **kwargs):
    """Door"""
    wall_count = kwargs.pop("wall_count", None)
    door_type = kwargs.pop("door_type", None)
    if door_type is None:
        door_type = door_type_factory(simulation, **pop_kwargs("type__", kwargs))

    kwrgs = get_factory_from_fields(Door)
    kwrgs["area"] = random.randint(6, 25) + random.random()
    kwrgs["wall_number"] = None
    kwrgs.update(kwargs)
    kwrgs["name"] = kwrgs["name"] if kwrgs["name"] else "No - Name"
    if wall_count is not None and wall_count > 0:
        kwrgs["wall_number"] = random.randint(1, wall_count)
    return Door.objects.get_or_create(
        simulation=simulation, building=building, type=door_type, **kwrgs
    )[0]
