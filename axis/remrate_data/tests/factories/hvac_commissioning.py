"""hvac_commissioning.py - simulation"""

__author__ = "Steven K"
__date__ = "1/6/22 12:59"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import random

from ...models.hvac_commissioning import CommissionRefrigerantChargeMethod, HVACCommissioning

log = logging.getLogger(__name__)


def hvac_commissioning_factory(simulation, duct_system=None, **kwargs):
    kwrgs = {
        "_result_number": random.randint(100, 100000),
        "rating_number": "Random",
        "_source_commissioning_number": random.randint(100, 100000),
        "duct_system_number": -1,
        "heating_equipment_number": -1,
        "cooling_equipment_number": -1,
        "total_duct_leakage_grade": 1,  # No idea how to change that.
        "total_duct_leakage_exemption": random.choice([True, False]),
        "total_duct_leakage_grade_1_met": random.choice([True, False]),
        "blower_airflow_grade": 3,  # No idea how to change it.
        "blower_watt_draw_grade": 3,
        "refrigerant_charge_grade": 3,
        "blower_fan_efficiency": random.uniform(0, 1.0),  # Guess
        "difference_DTD": random.uniform(0, 1.0),  # Guess
        "difference_CTOA": random.uniform(0, 1.0),  # Guess
        "deviation": random.uniform(0.01, 0.2),  # Guess
        "total_refrigerant_weight": random.uniform(1.2, 5.0),  # Guess
    }
    if duct_system:
        if duct_system.duct_set.count():
            kwrgs["duct_system_number"] = kwargs.pop("duct_system_number", 0)
            kwrgs["heating_equipment_number"] = -1
            kwrgs["cooling_equipment_number"] = -1
            kwargs.pop("heating_equipment_number", None)
            kwargs.pop("cooling_equipment_number", None)
        else:
            kwrgs["duct_system_number"] = -1
            kwargs.pop("duct_system_number", None)
            kwrgs["heating_equipment_number"] = kwargs.pop("heating_equipment_number", 0)
            kwrgs["cooling_equipment_number"] = kwargs.pop("cooling_equipment_number", 0)

    if kwrgs["total_duct_leakage_exemption"]:
        kwrgs["blower_airflow_grade"] = 1
        kwargs["blower_airflow_design_specified"] = random.randint(0, 2999)
        kwargs["blower_airflow_operating_condition"] = random.randint(0, 2999)
        kwrgs["blower_watt_draw_grade"] = 1
        kwargs["blower_airflow_watt_draw"] = random.randint(0, 1499)
        kwrgs["refrigerant_charge_grade"] = 1
    else:
        kwrgs["refrigerant_charge_single_package_system"] = random.choice([True, False])
        kwrgs["refrigerant_charge_onboard_diagnostic"] = random.choice([True, False])

        if kwrgs["refrigerant_charge_single_package_system"]:
            kwrgs["refrigerant_charge_grade"] = 1
        if kwrgs["refrigerant_charge_onboard_diagnostic"]:
            kwrgs["refrigerant_charge_grade"] = 1

        if (
            not kwrgs["refrigerant_charge_single_package_system"]
            and not kwrgs["refrigerant_charge_onboard_diagnostic"]
        ):
            kwrgs["refrigerant_charge_test_method"] = random.choice(
                CommissionRefrigerantChargeMethod.choices
            )[0]

    kwrgs.update(kwargs)
    return HVACCommissioning.objects.create(simulation=simulation, **kwrgs)
