"""infiltration.py: Django factories"""

import random

from .utils import random_digits
from ...models import Infiltration

__author__ = "Steven K"
__date__ = "01/09/2020 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def infiltration_factory(simulation, _result_number, building, _building_number, **kwargs):
    blg_data = kwargs.pop("blg_data", {})
    kw = {
        "testing_type": blg_data.get("measurement_type", random.choice([1, 3, 4, 5, 6])),
        "heating_value": blg_data.get(
            "heating_season_infiltration_value",
            random.randint(1, 100) + random.random(),
        ),
        "cooling_value": blg_data.get(
            "cooling_season_infiltration_value",
            random.randint(1, 100) + random.random(),
        ),
        "units": blg_data.get("infiltration_unit", random.randint(1, 6)),
        "mechanical_vent_type": blg_data.get("mechanical_ventilation_type", random.randint(1, 4)),
        "mechanical_vent_cfm": blg_data.get(
            "mechanical_ventilation_fan_rate",
            random.randint(500, 2500) + random.random(),
        ),
        "sensible_recovery_efficiency": blg_data.get(
            "sensible_recovery_efficiency", random.randint(1, 99) + random.random()
        ),
        "hours_per_day": blg_data.get(
            "mechanical_ventilation_hours_per_day",
            random.randint(0, 23) + random.random(),
        ),
        "mechanical_vent_power": blg_data.get(
            "mechanical_ventilation_fan_watts", random.randint(0, 100) + random.random()
        ),
        "total_recovery_efficiency": blg_data.get(
            "total_recovery_efficiency", random.randint(0, 99) + random.random()
        ),
        "verification_type": blg_data.get("iecc_code_verification", random.choice([1, 2])),
        "shelter_class": blg_data.get("shelter_class", random.randint(1, 5)),
        "cooling_type": blg_data.get("cooling_season_strategy", random.randint(1, 4)),
        "ecm_fan_motor": blg_data.get("ecm_fan_motor", random.choice([True, False])),
        "annual_filtration": blg_data.get(
            "annual_infiltration_value", random.randint(1, 100) + random.random()
        ),
        "use_fan_watts_defaults": random.choice([True, False]),
        "no_mechanical_vent_measured": random.choice([True, False]),
        "field_tested_value": blg_data.get(
            "field_test_value", random.randint(0, 100) + random.random()
        ),
        "rating_number": "",
    }
    kw.update(kwargs)

    if tuple(simulation.numerical_version) >= (16, 1, 0):
        # These moved to a separate table.
        kw.update(
            {
                "mechanical_vent_type": None,
                "mechanical_vent_cfm": None,
                "sensible_recovery_efficiency": None,
                "hours_per_day": None,
                "mechanical_vent_power": None,
                "total_recovery_efficiency": None,
                "ecm_fan_motor": None,
                "multi_family_good_air_exchange": None,
                "no_mechanical_vent_measured": None,
                "use_fan_watts_defaults": None,
            }
        )

    return Infiltration.objects.get_or_create(
        simulation=simulation,
        _result_number=_result_number,
        building=building,
        _building_number=_building_number,
        _source_infiltration_number=int(random_digits(6)),
        defaults=kw,
    )[0]
