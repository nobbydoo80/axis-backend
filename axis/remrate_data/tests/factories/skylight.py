"""skylight.py - simulation"""

import logging
import random

from .utils import get_factory_from_fields, pop_kwargs
from .window import window_type_factory
from ...models import Skylight

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "9/30/20 13:14"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def skylight_factory(simulation, building, **kwargs):
    """Window"""
    roof_count = kwargs.pop("roof_count", None)
    window_type = kwargs.pop("window_type", None)
    if window_type is None:
        window_type = window_type_factory(simulation, **pop_kwargs("type__", kwargs))

    kwrgs = get_factory_from_fields(Skylight)
    kwrgs["area"] = random.randint(1, 4) + random.random()
    kwrgs["orientation"] = random.choice([1, 2, 3, 4, 5, 7, 8, 9])
    kwargs["summer_shading_factor"] = random.choice([1.0, 0.70, 0.40, 0.10])
    kwargs["winter_shading_factor"] = random.choice([1.0, 0.70, 0.40, 0.10])
    kwrgs["roof_number"] = None
    kwrgs.update(kwargs)
    kwrgs["name"] = kwrgs["name"] if kwrgs["name"] else "No - Name"
    if roof_count is not None and roof_count > 0:
        kwrgs["roof_number"] = random.randint(1, roof_count)
    return Skylight.objects.get_or_create(
        simulation=simulation, building=building, type=window_type, **kwrgs
    )[0]
