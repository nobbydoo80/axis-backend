"""window.py - simulation"""

import logging
import random

from .utils import get_factory_from_fields, pop_kwargs
from ...models import WindowType, Window

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "6/1/20 10:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def window_type_factory(simulation, **kwargs):
    """Window Type Factory"""
    kwrgs = get_factory_from_fields(WindowType)
    kwrgs["u_value"] = random.random()
    kwrgs.update(kwargs)
    kwrgs["name"] = kwrgs["name"] if kwrgs["name"] else "No - Name"
    return WindowType.objects.get_or_create(simulation=simulation, **kwrgs)[0]


def window_factory(simulation, building, **kwargs):
    """Window"""
    wall_count = kwargs.pop("wall_count", None)
    window_type = kwargs.pop("window_type", None)
    if window_type is None:
        window_type = window_type_factory(simulation, **pop_kwargs("type__", kwargs))

    kwrgs = get_factory_from_fields(Window)
    kwrgs["area"] = random.randint(1, 4) + random.random()
    kwrgs["wall_number"] = None
    kwargs["adjacent_shading_summer_factor"] = random.choice([1.0, 0.70, 0.40, 0.10])
    kwargs["adjacent_shading_winter_factor"] = random.choice([1.0, 0.70, 0.40, 0.10])
    kwrgs.update(kwargs)
    kwrgs["name"] = kwrgs["name"] if kwrgs["name"] else "No - Name"
    if wall_count is not None and wall_count > 0:
        kwrgs["wall_number"] = random.randint(1, wall_count)
    return Window.objects.get_or_create(
        simulation=simulation, building=building, type=window_type, **kwrgs
    )[0]
