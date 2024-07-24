"""air_source_heat_pump.py - simulation"""

import logging
import random

from .utils import random_sequence, get_factory_from_fields
from ...models import AirSourceHeatPump

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "7/22/20 11:04"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def air_source_heat_pump_factory(simulation, _result_number, **kwargs):
    kwrgs = get_factory_from_fields(AirSourceHeatPump)
    kwrgs["cooling_efficiency"] = random.choice(range(100)) + random.random()
    kwrgs["heating_efficiency"] = random.choice(range(100)) + random.random()
    kwrgs.update(kwargs)

    kwrgs.pop("_result_number", None)
    return AirSourceHeatPump.objects.get_or_create(
        simulation=simulation, _result_number=_result_number, defaults=kwrgs
    )[0]
