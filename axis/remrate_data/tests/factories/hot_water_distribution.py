"""hot_water_distribution.py - simulation"""

import logging
import random

from .utils import get_factory_from_fields
from ...models import HotWaterDistribution

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "11/4/20 14:19"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def hot_water_distribution_factory(simulation, **kwargs):
    kwrgs = get_factory_from_fields(HotWaterDistribution)
    kwrgs["fix_low_flow"] = random.choice([True, False])
    kwrgs["hot_water_pipe_insulation"] = random.choice([True, False])
    kwrgs["recirculation_type"] = random.randrange(1, 5)
    kwrgs["max_fix_distribution"] = random.randint(10, 100) + random.random()
    kwrgs["max_supply_return_distribution"] = random.randint(10, 100) + random.random()
    kwrgs["hot_water_pipe_length"] = random.randint(10, 100) + random.random()
    kwrgs["hot_water_pipe_recirculation_length"] = random.randint(10, 100) + random.random()
    kwrgs["hot_water_recirculation_pump_power"] = random.randint(10, 50) + random.random()
    kwrgs["has_recirculation_pump"] = random.choice([True, True, False, False, None])
    kwrgs["hot_water_recirculation_pump_efficiency"] = random.randint(10, 99) + random.random()
    kwrgs["hot_water_recirculation_pre_heat_cold"] = random.choice([True, True, False, False, None])
    kwrgs["hot_water_recirculation_pre_heat_hot"] = random.choice([True, True, False, False, None])
    kwrgs["number_shower_heads"] = random.randint(1, 3)
    kwrgs["number_recirculation_shower_heads"] = random.randint(1, 3)
    kwrgs["flow_control_efficiency"] = random.random()
    kwrgs.update(kwargs)

    return HotWaterDistribution.objects.get_or_create(simulation=simulation, **kwrgs)[0]
