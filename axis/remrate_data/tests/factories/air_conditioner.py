"""air_conditioner.py: Django factories"""

import random

from .utils import random_sequence
from ...models import AirConditioner

__author__ = "Steven K"
__date__ = "01/09/2020 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def air_conditioner_factory(simulation, _result_number, **kwargs):
    suffix = kwargs.pop("suffix", random_sequence(4))

    blg_data = kwargs.pop("blg_data")
    kwrgs = {
        "_source_air_conditioner_number": _result_number,
        "name": blg_data.get("name", suffix + "-ac"),
        "type": blg_data.get("system_type", random.choice(range(1, 5))),
        "fuel_type": blg_data.get("fuel_type", random.choice(range(1, 7))),
        "output_capacity": blg_data.get(
            "rated_output", random.choice(range(1000)) + random.random()
        ),
        "efficiency": blg_data.get(
            "seasonal_efficiency", random.choice(range(100)) + random.random()
        ),
        "sensible_heat_fraction": blg_data.get("sensible_heat_fraction", random.random()),
        "efficiency_unit": blg_data.get("seasonal_efficiency_unit", random.choice(range(1, 5))),
        "is_desuperheater": blg_data.get("desuperheater", False),
        "fan_defaults": blg_data.get("auxilary_fan_use_defaults", False),
        "note": blg_data.get("note", "A note"),
        "fan_power": blg_data.get(
            "auxilary_fan_power", random.choice(range(100)) + random.random()
        ),
        "pump_energy": blg_data.get("pump_energy", random.choice(range(100)) + random.random()),
        "pump_energy_units": blg_data.get("pump_energy_units", random.choice(range(2))),
    }
    kwrgs.update(kwargs)
    return AirConditioner.objects.get_or_create(
        simulation=simulation, _result_number=_result_number, defaults=kwrgs
    )[0]
