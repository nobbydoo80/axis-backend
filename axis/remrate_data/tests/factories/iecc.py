"""iecc.py: Django factories"""


import re

from .utils import random_digits
from ...models import IECC

__author__ = "Steven K"
__date__ = "01/09/2020 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def iecc_factory(**kwargs):
    simulation = kwargs.pop("simulation", None)

    kwrgs = {
        "_result_number": int(random_digits(6)),
        "meets_iecc98_consumption_compliance": True,
        "passes_iecc98_ducts_overall_u0": True,
        "passes_iecc98_overall_u0": True,
        "meets_iecc00_consumption_compliance": True,
        "passes_iecc00_ducts_overall_u0": True,
        "passes_iecc00_overall_u0": True,
        "meets_iecc01_consumption_compliance": True,
        "passes_iecc01_ducts_overall_u0": True,
        "passes_iecc01_overall_u0": True,
        "passes_iecc03_consumption_compliance": False,
        "passes_iecc03_ducts_overall_u0": False,
        "passes_iecc03_overall_u0": False,
        "passes_iecc04_consumption_compliance": True,
        "passes_iecc04_ducts_overall_u0": True,
        "passes_iecc04_overall_ua_compliance": True,
        "passes_iecc04_code": True,
        "passes_iecc06_consumption_compliance": False,
        "passes_iecc06_ducts_overall_u0": False,
        "passes_iecc06_overall_ua_compliance": False,
        "passes_iecc06_code": False,
        "passes_iecc09_consumption_compliance": True,
        "passes_iecc09_ducts_overall_u0": True,
        "passes_iecc09_overall_ua_compliance": True,
        "passes_iecc09_code": False,
        "passes_iecc12_consumption_compliance": True,
        "passes_iecc12_ducts_overall_u0": True,
        "passes_iecc12_overall_ua_compliance": False,
        "passes_iecc12_code": False,
        "iecc98_reference_heating_consumption": 1.1,
        "iecc98_reference_cooling_consumption": 1.1,
        "iecc98_reference_hot_water_consumption": 1.1,
        "iecc98_reference_lights_appliance_consumption": 1.1,
        "iecc98_reference_photo_voltaic_consumption": 1.1,
        "iecc98_reference_total_consumption": 1.1,
        "iecc98_designed_heating_consumption": 1.1,
        "iecc98_designed_cooling_consumption": 1.1,
        "iecc98_designed_hot_water_consumption": 1.1,
        "iecc98_designed_lights_appliance_consumption": 1.1,
        "iecc98_designed_photo_voltaic_consumption": 1.1,
        "iecc98_designed_total_consumption": 1.1,
        "iecc98_reference_overall_u0": 1.1,
        "iecc98_designed_overall_u0": 1.1,
        "iecc00_reference_heating_consumption": 1.1,
        "iecc00_reference_cooling_consumption": 1.1,
        "iecc00_reference_hot_water_consumption": 1.1,
        "iecc00_reference_lights_appliance_consumption": 1.1,
        "iecc00_reference_photo_voltaic_consumption": 1.1,
        "iecc00_reference_total_consumption": 1.1,
        "iecc00_designed_heating_consumption": 1.1,
        "iecc00_designed_cooling_consumption": 1.1,
        "iecc00_designed_hot_water_consumption": 1.1,
        "iecc00_designed_lights_appliance_consumption": 1.1,
        "iecc00_designed_photo_voltaic_consumption": 1.1,
        "iecc00_designed_total_consumption": 1.1,
        "iecc00_reference_overall_u0": 1.1,
        "iecc00_designed_overall_u0": 1.1,
        "iecc01_reference_heating_consumption": 1.1,
        "iecc01_reference_cooling_consumption": 1.1,
        "iecc01_reference_hot_water_consumption": 1.1,
        "iecc01_reference_lights_appliance_consumption": 1.1,
        "iecc01_reference_photo_voltaic_consumption": 1.1,
        "iecc01_reference_total_consumption": 1.1,
        "iecc01_designed_heating_consumption": 1.1,
        "iecc01_designed_cooling_consumption": 1.1,
        "iecc01_designed_hot_water_consumption": 1.1,
        "iecc01_designed_lights_appliance_consumption": 1.1,
        "iecc01_designed_photo_voltaic_consumption": 1.1,
        "iecc01_designed_total_consumption": 1.1,
        "iecc01_reference_overall_u0": 1.1,
        "iecc01_designed_overall_u0": 1.1,
        "iecc03_reference_heating_consumption": 1.1,
        "iecc03_reference_cooling_consumption": 1.1,
        "iecc03_reference_hot_water_consumption": 1.1,
        "iecc03_reference_lights_appliance_consumption": 1.1,
        "iecc03_reference_photo_voltaic_consumption": 1.1,
        "iecc03_reference_total_consumption": 1.1,
        "iecc03_designed_heating_consumption": 1.1,
        "iecc03_designed_cooling_consumption": 1.1,
        "iecc03_designed_hot_water_consumption": 1.1,
        "iecc03_designed_lights_appliance_consumption": 1.1,
        "iecc03_designed_photo_voltaic_consumption": 1.1,
        "iecc03_designed_total_consumption": 1.1,
        "iecc03_reference_overall_u0": 1.1,
        "iecc03_designed_overall_u0": 1.1,
        "iecc04_reference_heating_cost": 1.1,
        "iecc04_reference_cooling_cost": 1.1,
        "iecc04_reference_hot_water_cost": 1.1,
        "iecc04_reference_lights_appliance_cost": 1.1,
        "iecc04_reference_photo_voltaic_cost": 1.1,
        "iecc04_reference_service_cost": 1.1,
        "iecc04_reference_total_cost": 1.1,
        "iecc04_designed_heating_cost": 1.1,
        "iecc04_designed_cooling_cost": 1.1,
        "iecc04_designed_hot_water_cost": 1.1,
        "iecc04_designed_lights_appliance_cost": 1.1,
        "iecc04_designed_photo_voltaic_cost": 1.1,
        "iecc04_designed_service_cost": 1.1,
        "iecc04_designed_total_cost": 1.1,
        "iecc04_reference_overall_u0": 1.1,
        "iecc04_designed_overall_u0": 1.1,
        "iecc06_reference_heating_cost": 1.1,
        "iecc06_reference_cooling_cost": 1.1,
        "iecc06_reference_hot_water_cost": 1.1,
        "iecc06_reference_lights_appliance_cost": 1.1,
        "iecc06_reference_photo_voltaic_cost": 1.1,
        "iecc06_reference_service_cost": 1.1,
        "iecc06_reference_total_cost": 1.1,
        "iecc06_designed_heating_cost": 1.1,
        "iecc06_designed_cooling_cost": 1.1,
        "iecc06_designed_hot_water_cost": 1.1,
        "iecc06_designed_lights_appliance_cost": 1.1,
        "iecc06_designed_photo_voltaic_cost": 1.1,
        "iecc06_designed_service_cost": 1.1,
        "iecc06_designed_total_cost": 1.1,
        "iecc06_reference_overall_u0": 1.1,
        "iecc06_designed_overall_u0": 1.1,
        "iecc09_reference_heating_cost": 1.1,
        "iecc09_reference_cooling_cost": 1.1,
        "iecc09_reference_hot_water_cost": 1.1,
        "iecc09_reference_lights_appliance_cost": 1.1,
        "iecc09_reference_photo_voltaic_cost": 1.1,
        "iecc09_reference_service_cost": 1.1,
        "iecc09_reference_total_cost": 1.1,
        "iecc09_designed_heating_cost": 1.1,
        "iecc09_designed_cooling_cost": 1.1,
        "iecc09_designed_hot_water_cost": 1.1,
        "iecc09_designed_lights_appliance_cost": 1.1,
        "iecc09_designed_photo_voltaic_cost": 1.1,
        "iecc09_designed_service_cost": 1.1,
        "iecc09_designed_total_cost": 1.1,
        "iecc09_reference_overall_u0": 1.1,
        "iecc09_designed_overall_u0": 1.1,
    }

    if not simulation:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("simulation__"):
                c_kwrgs[re.sub(r"simulation__", "", k)] = kwargs.pop(k)
        from . import simulation_factory

        kwrgs["simulation"] = simulation_factory(**c_kwrgs)
    else:
        kwrgs["simulation"] = simulation

    kwrgs.update(kwargs)
    result_number = kwrgs.pop("_result_number")

    return IECC.objects.get_or_create(_result_number=result_number, defaults=kwrgs)[0]
