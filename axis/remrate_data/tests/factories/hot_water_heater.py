"""hot_water_heater.py: Django factories"""


import random

from .utils import random_sequence
from ...models import HotWaterHeater

__author__ = "Steven K"
__date__ = "01/09/2020 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def hot_water_heater_factory(simulation, _result_number, **kwargs):
    suffix = kwargs.pop("suffix", random_sequence(4))

    blg_data = kwargs.pop("blg_data")
    kwrgs = {
        "_source_hot_water_heater_number": _result_number,
        "name": blg_data.get("name", suffix + "-hot_water"),
        "type": blg_data.get("system_type", 3),
        "fuel_type": blg_data.get("fuel_type", 1),
        "tank_size": blg_data.get("water_tank_size", 10),
        "extra_tank_insulation_r_value": blg_data.get("extra_tank_insulation"),
        "energy_factor": blg_data.get("energy_factor", random.random()),
        "recovery_efficiency": blg_data.get("recovery_efficiency", random.random()),
        "note": blg_data.get("note", "Somthing importang"),
    }
    kwrgs.update(kwargs)
    return HotWaterHeater.objects.get_or_create(
        simulation=simulation, _result_number=_result_number, defaults=kwrgs
    )[0]
