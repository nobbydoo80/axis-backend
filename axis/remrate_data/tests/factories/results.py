"""result.py: Django factories"""

import logging
import random

from .utils import random_sequence
from ...models import Results

__author__ = "Steven K"
__date__ = "01/09/2020 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


def results_factory(simulation, _result_number, fuel_summary=None, **kwargs):
    kwrgs = {}
    if fuel_summary:
        fs_data = {
            "total_cost": 0.0,
            "heating_consumption": 0.0,
            "cooling_consumption": 0.0,
            "hot_water_consumption": 0.0,
            "lights_and_appliances_total_consumption": 0.0,
            "photo_voltaic_consumption": 0.0,
        }

        for fs in fuel_summary.all():
            fs_data["total_cost"] += fs.total_cost

            if fs.fuel_type == 1 and fs.fuel_units == 4:

                def convert_therms_to_mmbtu(v):
                    return float(v) / 10.0

                fs_data["heating_consumption"] += convert_therms_to_mmbtu(fs.heating_consumption)
                fs_data["cooling_consumption"] += convert_therms_to_mmbtu(fs.cooling_consumption)
                fs_data["hot_water_consumption"] += convert_therms_to_mmbtu(
                    fs.hot_water_consumption
                )
                fs_data["lights_and_appliances_total_consumption"] += convert_therms_to_mmbtu(
                    fs.lights_and_appliances_consumption
                )
                fs_data["photo_voltaic_consumption"] += convert_therms_to_mmbtu(
                    fs.photo_voltaics_consumption
                )

            elif fs.fuel_type == 4 and fs.fuel_units == 1:

                def convert_kwh_to_mmbtu(v):
                    return (float(v) * 3.412) / 1000.0

                fs_data["heating_consumption"] += convert_kwh_to_mmbtu(fs.heating_consumption)
                fs_data["cooling_consumption"] += convert_kwh_to_mmbtu(fs.cooling_consumption)
                fs_data["hot_water_consumption"] += convert_kwh_to_mmbtu(fs.hot_water_consumption)
                fs_data["lights_and_appliances_total_consumption"] += convert_kwh_to_mmbtu(
                    fs.lights_and_appliances_consumption
                )
                fs_data["photo_voltaic_consumption"] += convert_kwh_to_mmbtu(
                    fs.photo_voltaics_consumption
                )

            else:
                log.error(
                    "Unable to handle Fuel of %s and Units of %s",
                    fs.get_fuel_type_display(),
                    fs.get_fuel_units_display(),
                )

        kwrgs.update(fs_data)

    kwrgs.update(kwargs)

    for f in Results._meta.fields:
        if f.name in kwrgs:
            continue
        if f.__class__.__name__ == "FloatField":
            kwrgs[f.name] = random.random() * random.randint(1, 20)

    return Results.objects.get_or_create(
        simulation=simulation, _result_number=_result_number, defaults=kwrgs
    )[0]
