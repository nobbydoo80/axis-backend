"""lights_and_appliance.py: Django factories"""

import random

from .utils import random_sequence
from ...models import LightsAndAppliance, InstalledLightsAndAppliances

__author__ = "Steven K"
__date__ = "01/09/2020 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def lights_and_appliance_factory(simulation, building, _result_number, _building_number, **kwargs):
    kwrgs = {
        "oven_fuel": 2,
        "clothes_dryer_fuel": 2,
        "default_loads": False,
        "refrigerator_kw_yr": random.uniform(10, 100),
        "dishwasher_energy_factor": random.uniform(10, 100),
        "pct_florescent": random.uniform(1, 10),
        "ceiling_fan_cfm_watt": random.uniform(10, 100),
        "pct_interior_cfl": random.uniform(1, 90),
        "pct_exterior_cfl": random.uniform(1, 90),
        "pct_garage_cfl": random.uniform(1, 90),
        "pct_interior_led": random.uniform(1, 90),
        "pct_exterior_led": random.uniform(1, 90),
        "pct_garage_led": random.uniform(1, 90),
        "refrigerator_location": 1,
        "dishwasher_capacity": random.randint(3, 4),
        "dishwasher_kw_yr": random.uniform(2, 10),
        "oven_induction": random.choice([False, True]),
        "oven_convection": random.choice([False, True]),
        "clothes_dryer_location": 1,
        "clothes_dryer_moisture_sensing": random.choice([False, True]),
        "clothes_dryer_energy_factor": random.uniform(20, 199),
        "clothes_dryer_modified_energy_factor": random.uniform(20, 199),
        "clothes_dryer_gas_energy_factor": random.uniform(20, 199),
        "clothes_washer_location": 1,
        "clothes_washer_label_energy_rating": random.uniform(20, 199),
        "clothes_washer_capacity": random.uniform(1, 4),
        "clothes_washer_electric_rate": random.uniform(20, 199),
        "clothes_washer_gas_rate": random.uniform(20, 199),
        "clothes_washer_gas_cost": random.uniform(20, 199),
        "clothes_washer_efficiency": random.randint(1, 4),
    }
    greater_16p1 = tuple(simulation.numerical_version) >= (16, 1, 0)
    if greater_16p1:
        kwrgs.update(
            {
                "dishwasher_location": random.choice([1, 2]),
                "dishwasher_presets": random.randint(1, 5),
                "shared_hot_water_equipment_number_for_dishwasher": None,
                "dishwasher_electric_rate": random.randint(1, 50) + random.random(),
                "dishwasher_gas_rate": random.randint(0, 1) + random.random(),
                "dishwasher_gas_cost": random.randint(20, 100) + random.random(),
                "dishwasher_loads_per_week": random.randint(1, 20),
                "ceiling_fan_count": random.choice([0, 1, 2, 3, 4, 5, 6, 7]),
                "oven_location": random.choice([1, 2]),
                "clothes_dryer_fuel": random.choice([1, 2, 3, 4]),
                "dwelling_units_per_dryer": 0,
                "clothes_washer_presets": random.choice([1, 2, 3, 4, 5]),
                "dwelling_units_per_clothes_washer": 0,
                "shared_hot_water_equipment_number_for_clothes_washer": None,
                "clothes_washer_iwf": random.randint(8, 15) + random.random(),
                "clothes_washer_loads_per_week": random.randint(1, 20),
            }
        )

    kwrgs.update(kwargs)
    l_and_a = LightsAndAppliance.objects.get_or_create(
        simulation=simulation,
        building=building,
        _result_number=_result_number,
        _building_number=_building_number,
        defaults=kwrgs,
    )[0]

    return l_and_a
