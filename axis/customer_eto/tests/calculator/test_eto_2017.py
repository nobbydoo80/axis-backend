"""__init__.py: Django Calculator Tests"""


import logging

from django.test import TestCase

from axis.core.tests.client import AxisClient
from axis.customer_eto.calculator.eps.base import EPSInputException
from axis.customer_eto.calculator.eps.calculator import EPSCalculator
from axis.customer_eto.calculator.eps.incentives import Incentives2017

__author__ = "Steven K"
__date__ = "12/16/2019 09:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class EPS2017CalculatorTests(TestCase):
    """Test out ETO 2017 Calculator parser"""

    client_class = AxisClient
    fixtures = [
        "eto_simulation_data.json",
    ]

    def get_calculator(self, **kwargs):
        kwargs["program"] = "eto-2017"
        return EPSCalculator(**kwargs)

    def dump_output(self, calculator):
        print(
            "self.assertEqual(round(calculator.eps_score, 0), {})".format(
                round(calculator.eps_score, 0)
            )
        )
        print(
            "self.assertEqual(round(calculator.code_eps_score, 0), {})".format(
                round(calculator.code_eps_score, 0)
            )
        )
        print(
            "self.assertEqual(round(calculator.floored_percentage_improvement, 2), {})".format(
                round(calculator.floored_percentage_improvement, 2)
            )
        )
        print(
            "self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), {})".format(
                round(calculator.incentives.electric_utility_allocation_pct, 2)
            )
        )
        print(
            "self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), {})".format(
                round(calculator.incentives.gas_utility_allocation_pct, 2)
            )
        )
        print(
            "self.assertEqual(round(calculator.total_builder_incentive, 2), {})".format(
                round(calculator.total_builder_incentive, 2)
            )
        )
        print(
            "self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), {})".format(
                round(calculator.incentives.builder_electric_incentive, 2)
            )
        )
        print(
            "self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), {})".format(
                round(calculator.incentives.builder_gas_incentive, 2)
            )
        )
        print(
            "self.assertEqual(round(calculator.total_verifier_incentive, 2), {})".format(
                round(calculator.total_verifier_incentive, 2)
            )
        )
        print(
            "self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), {})".format(
                round(calculator.incentives.verifier_electric_incentive, 2)
            )
        )
        print(
            "self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), {})".format(
                round(calculator.incentives.verifier_gas_incentive, 2)
            )
        )
        print(
            "self.assertEqual(round(calculator.carbon_score, 2), {})".format(
                round(calculator.carbon_score, 2)
            )
        )
        print(
            "self.assertEqual(round(calculator.code_carbon_score, 2), {})".format(
                round(calculator.code_carbon_score, 2)
            )
        )
        print(
            "self.assertEqual(round(calculator.estimated_annual_cost, 2), {})".format(
                round(calculator.estimated_annual_cost, 2)
            )
        )
        print(
            "self.assertEqual(round(calculator.estimated_monthly_cost, 2), {})".format(
                round(calculator.estimated_monthly_cost, 2)
            )
        )
        print(
            "self.assertEqual(round(calculator.projected_size_or_home_eps, 0), {})".format(
                round(calculator.projected_size_or_home_eps, 0)
            )
        )
        print(
            "self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), {})".format(
                round(calculator.projected_size_or_home_carbon, 2)
            )
        )

    @property
    def site_data(self):
        return {
            "site_address": "1234 Sample St. City, WA 12345",
            "location": "portland",
            "heat_type": "gas heat",
            "pathway": "pct",
            "conditioned_area": "2509",
            "electric_utility": "pacific power",
            "gas_utility": "nw natural",
            "has_ashp": False,
            "qualifying_thermostat": "YES-ducted gas furnace",
            "qty_shower_head_1p5": 0,
            "qty_shower_head_1p6": 2,
            "qty_shower_head_1p75": 3,
        }

    @property
    def code_values(self):
        return {
            "heating_therms": 311,
            "heating_kwh": 281,
            "cooling_kwh": 0,
            "hot_water_therms": 176,
            "hot_water_kwh": 0,
            "lights_and_appliances_therms": 31,
            "lights_and_appliances_kwh": 5626,
            "electric_cost": 584,
            "gas_cost": 469,
        }

    @property
    def improved_values(self):
        return {
            "heating_therms": 208,
            "heating_kwh": 250,
            "cooling_kwh": 0,
            "hot_water_therms": 150,
            "hot_water_kwh": 0,
            "lights_and_appliances_therms": 31,
            "lights_and_appliances_kwh": 4800,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 0,
            "pv_kwh": 0,
            "electric_cost": 517,
            "gas_cost": 299,
        }.copy()

    def test_smart_thermometer_choices(self):
        for tstat_choice in [
            "no qualifying smart therMOSTat",
            "yes-DUCTEd gas furnace",
            "yes-ducted AIR source heat pump",
            None,
        ]:
            kwargs = self.site_data.copy()
            kwargs["code_data"] = self.code_values
            kwargs["improved_data"] = self.improved_values
            kwargs["qualifying_thermostat"] = tstat_choice
            if tstat_choice and "AIR" in tstat_choice:
                kwargs["has_ashp"] = True
            self.get_calculator(**kwargs)

    def test_bad_smart_thermometer_choices(self):
        for tstat_choice in ["no qualifying", True]:
            kwargs = self.site_data.copy()
            kwargs["code_data"] = self.code_values
            kwargs["improved_data"] = self.improved_values
            kwargs["qualifying_thermostat"] = tstat_choice
            self.assertRaises(EPSInputException, self.get_calculator, **kwargs)

    def test_gas_utiliity_avista(self):
        kwargs = self.site_data.copy()
        kwargs["code_data"] = self.code_values
        kwargs["improved_data"] = self.improved_values
        kwargs["gas_utility"] = "avista"
        self.get_calculator(**kwargs)

    def test_full_incentives(self):
        from axis.customer_eto.calculator.eps.constants import eto_2017 as constants

        incentives = Incentives2017(constants=constants)

        incentives.percentage_improvement = None
        self.assertEqual(incentives.full_territory_builder_incentive, 0.0)

        for pct_imp, incentive in [
            (0, 0.0),
            (0.09999, 0.0),
            (0.1, 600.0),
            (0.1099, 600.0),
            (0.11, 660.0),
            (0.12, 720.0),
            (0.199, 1194.0),
            (0.2, 1240.0),
            (0.2399, 1683.85),
            (0.24, 1695.0),
            (0.2899, 2418.5),
            (0.29, 2445.0),
            (0.309, 2777.5),
            (0.31, 2820.0),
            (0.319, 3000.0),
            (0.32, 3025.0),
            (0.35, 3640.0),
            (0.379, 4234.5),
            (0.38, 4260.0),
            (0.4, 4680.0),
            (0.5, 4680.0),
        ]:
            incentives.percentage_improvement = pct_imp
            c_value = incentives.full_territory_builder_incentive
            # print("({}, {}).".format(pct_imp, round(c_value, 2)))
            self.assertEqual(round(c_value, 2), round(incentive, 2))

    def test_solar_therm_water_heating(self):
        kwargs = {
            "site_address": "RB131021.7",
            "location": "portland",
            "us_state": "WA",
            "heat_type": "gas heat",
            "pathway": "pct",
            "conditioned_area": 2200.0,
            "electric_utility": "pacific power",
            "program": "eto-2017",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.82,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": False,
            "qualifying_thermostat": "yes-ducted gas furnace",
            "qty_shower_head_1p5": 3,
            "qty_shower_head_1p6": 2,
            "qty_shower_head_1p75": 1,
            "code_data": {
                "heating_therms": 413.151886,
                "heating_kwh": 330.73877,
                "cooling_kwh": 1096.550903,
                "hot_water_therms": 209.060745,
                "hot_water_kwh": 0.0,
                "lights_and_appliances_therms": 30.700001,
                "lights_and_appliances_kwh": 6423.179199,
                "electric_cost": 794.945435,
                "gas_cost": 636.384583,
            },
            "improved_data": {
                "heating_therms": 302.681824,
                "heating_kwh": 106.226616,
                "cooling_kwh": 1036.22644,
                "hot_water_therms": 87.484634,
                "hot_water_kwh": 0.0,
                "lights_and_appliances_therms": 30.700001,
                "lights_and_appliances_kwh": 5696.834473,
                "pv_kwh": 0.0,
                "solar_hot_water_therms": 52.672699,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 692.574097,
                "gas_cost": 376.160492,
            },
        }
        calculator = self.get_calculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 59.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 92.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.39)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.0)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 1.0)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 837.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 837.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 100.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 100.0)
        self.assertEqual(round(calculator.carbon_score, 2), 9.23)
        self.assertEqual(round(calculator.code_carbon_score, 2), 11.98)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1068.73)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 89.06)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 112.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 14.9)

    def test_solar_kwh_water_heating(self):
        kwargs = {
            "site_address": "RB131021.7",
            "location": "portland",
            "us_state": "WA",
            "heat_type": "gas heat",
            "pathway": "pct",
            "conditioned_area": 2200.0,
            "electric_utility": "pacific power",
            "program": "eto-2017",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.82,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": False,
            "qualifying_thermostat": "yes-ducted gas furnace",
            "qty_shower_head_1p5": 3,
            "qty_shower_head_1p6": 2,
            "qty_shower_head_1p75": 1,
            "code_data": {
                "heating_therms": 413.151886,
                "heating_kwh": 330.73877,
                "cooling_kwh": 1096.550903,
                "hot_water_kwh": 209.060745,
                "hot_water_therms": 0.0,
                "lights_and_appliances_therms": 30.700001,
                "lights_and_appliances_kwh": 6423.179199,
                "electric_cost": 794.945435,
                "gas_cost": 636.384583,
            },
            "improved_data": {
                "heating_therms": 302.681824,
                "heating_kwh": 106.226616,
                "cooling_kwh": 1036.22644,
                "hot_water_kwh": 87.484634,
                "hot_water_therms": 0.0,
                "lights_and_appliances_therms": 30.700001,
                "lights_and_appliances_kwh": 5696.834473,
                "pv_kwh": 0.0,
                "solar_hot_water_kwh": 52.672699,
                "solar_hot_water_therms": 0.0,
                "electric_cost": 692.574097,
                "gas_cost": 376.160492,
            },
        }
        calculator = self.get_calculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 55.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 72.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.22)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.0)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 1.0)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 503.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 503.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 100.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 100.0)
        self.assertEqual(round(calculator.carbon_score, 2), 9.02)
        self.assertEqual(round(calculator.code_carbon_score, 2), 10.98)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1068.73)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 89.06)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 112.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 14.9)

    def test_shower_head_qty_swap(self):
        kwargs = {
            "site_address": "RB131021.7",
            "location": "portland",
            "us_state": "WA",
            "heat_type": "gas heat",
            "pathway": "pct",
            "conditioned_area": 2200.0,
            "electric_utility": "pacific power",
            "program": "eto-2017",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.82,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": False,
            "qualifying_thermostat": "yes-ducted gas furnace",
            "qty_shower_head_1p5": 3,
            "qty_shower_head_1p6": 0,
            "qty_shower_head_1p75": 1,
            "qty_shower_wand_1p5": 2,
            "code_data": {
                "heating_therms": 413.151886,
                "heating_kwh": 330.73877,
                "cooling_kwh": 1096.550903,
                "hot_water_kwh": 209.060745,
                "hot_water_therms": 0.0,
                "lights_and_appliances_therms": 30.700001,
                "lights_and_appliances_kwh": 6423.179199,
                "electric_cost": 794.945435,
                "gas_cost": 636.384583,
            },
            "improved_data": {
                "heating_therms": 302.681824,
                "heating_kwh": 106.226616,
                "cooling_kwh": 1036.22644,
                "hot_water_kwh": 87.484634,
                "hot_water_therms": 0.0,
                "lights_and_appliances_therms": 30.700001,
                "lights_and_appliances_kwh": 5696.834473,
                "pv_kwh": 0.0,
                "solar_hot_water_kwh": 52.672699,
                "solar_hot_water_therms": 0.0,
                "electric_cost": 692.574097,
                "gas_cost": 376.160492,
            },
        }
        calculator = self.get_calculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 55.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 72.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.22)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 503.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 100.0)

        kwargs.update(
            {"qty_shower_head_1p5": 1, "qty_shower_head_1p6": 3, "qty_shower_head_1p75": 2}
        )
        calculator = self.get_calculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 55.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 72.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.22)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 503.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 100.0)

        kwargs.update(
            {"qty_shower_head_1p5": 2, "qty_shower_head_1p6": 1, "qty_shower_head_1p75": 3}
        )
        calculator = self.get_calculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 55.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 72.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.22)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 503.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 100.0)

        kwargs.update(
            {"qty_shower_head_1p5": 6, "qty_shower_head_1p6": 0, "qty_shower_head_1p75": 0}
        )
        calculator = self.get_calculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 55.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 72.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.22)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 503.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 100.0)

        kwargs.update(
            {"qty_shower_head_1p5": 0, "qty_shower_head_1p6": 6, "qty_shower_head_1p75": 0}
        )
        calculator = self.get_calculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 55.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 72.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.22)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 503.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 100.0)

        kwargs.update(
            {"qty_shower_head_1p5": 0, "qty_shower_head_1p6": 0, "qty_shower_head_1p75": 6}
        )
        calculator = self.get_calculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 55.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 72.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.22)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 503.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 100.0)

        kwargs.update(
            {"qty_shower_wand_1p5": 6, "qty_shower_head_1p6": 0, "qty_shower_head_1p75": 0}
        )
        calculator = self.get_calculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 55.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 72.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.22)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 503.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 100.0)

    def test_shower_head_part_and_max_pct_improvement(self):
        kwargs = {
            "site_address": None,
            "location": "portland",
            "us_state": "OR",
            "heat_type": "gas heat",
            "pathway": "path 1",
            "conditioned_area": 2000.0,
            "electric_utility": "pacific power",
            "program": "eto-2017",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.0,
            "has_tankless_water_heater": False,
            "has_solar_hot_water": True,
            "has_ashp": False,
            "qualifying_thermostat": "no qualifying smart thermostat",
            "qty_shower_head_1p5": 1,
            "qty_shower_head_1p6": 0,
            "qty_shower_head_1p75": 0,
            "code_data": {
                "heating_therms": 200.0,
                "heating_kwh": 20.0,
                "cooling_kwh": 200.0,
                "hot_water_therms": 20.0,
                "hot_water_kwh": 20.0,
                "lights_and_appliances_therms": 20.0,
                "lights_and_appliances_kwh": 200.0,
                "electric_cost": 100.0,
                "gas_cost": 20.0,
            },
            "improved_data": {
                "heating_therms": 100.0,
                "heating_kwh": 10.0,
                "cooling_kwh": 100.0,
                "hot_water_therms": 10.0,
                "hot_water_kwh": 10.0,
                "lights_and_appliances_therms": 10.0,
                "lights_and_appliances_kwh": 100.0,
                "pv_kwh": 0.0,
                "solar_hot_water_therms": 50.0,
                "solar_hot_water_kwh": 20.0,
                "electric_cost": 50.0,
                "gas_cost": 10.0,
            },
        }

        calculator = self.get_calculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 17.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.5)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 4680.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 1872.0)

        kwargs.update(
            {"qty_shower_head_1p5": 0, "qty_shower_head_1p6": 1, "qty_shower_head_1p75": 0}
        )
        calculator = self.get_calculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 17.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.5)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 4680.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 1872.0)

        kwargs.update(
            {"qty_shower_head_1p5": 0, "qty_shower_head_1p6": 0, "qty_shower_head_1p75": 1}
        )
        calculator = self.get_calculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 17.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.5)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 4680.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 1872.0)

        kwargs.update(
            {"qty_shower_head_1p5": 0, "qty_shower_head_1p6": 0, "qty_shower_wand_1p5": 1}
        )
        calculator = self.get_calculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 17.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.5)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 4680.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 1872.0)

    def test_pv_incentives(self):
        kwargs = {
            "site_address": "RB131021.7",
            "location": "portland",
            "us_state": "OR",
            "heat_type": "heat pump",
            "pathway": "pct",
            "conditioned_area": 2517.0,
            "electric_utility": "portland general",
            "program": "eto-2017",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.82,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": False,
            "qualifying_thermostat": None,
            "qty_shower_head_1p5": 0,
            "qty_shower_head_1p6": 0,
            "qty_shower_head_1p75": 0,
            "code_data": {
                "heating_therms": 0,
                "heating_kwh": 981,
                "cooling_kwh": 400,
                "hot_water_therms": 0,
                "hot_water_kwh": 1279.0,
                "lights_and_appliances_therms": 0,
                "lights_and_appliances_kwh": 7197,
                "electric_cost": 794.945435,
                "gas_cost": 636.384583,
            },
            "improved_data": {
                "heating_therms": 0,
                "heating_kwh": 376.15329,
                "cooling_kwh": 300,
                "hot_water_therms": 0,
                "hot_water_kwh": 900,
                "lights_and_appliances_therms": 0,
                "lights_and_appliances_kwh": 6396.078613,
                "pv_kwh": 5000.0,
                "solar_hot_water_therms": 0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 15,
                "gas_cost": 718,
            },
        }

        # 37051 Solar Water Heater
        # 9120 Gas Heater with solar water heater
        #

        # kwargs['simulation_id'] = 9120
        display_results = True
        calculator = EPSCalculator(**kwargs)

        self.assertEqual(round(calculator.eps_score, 0), 10.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 43.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.19)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 1.0)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 0.0)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 1147.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 1147.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 0.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 300.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 300.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 0.0)
        self.assertEqual(round(calculator.carbon_score, 2), 1.58)
        self.assertEqual(round(calculator.code_carbon_score, 2), 5.22)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 733.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 61.08)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 128.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 10.99)

    def test_partial_territory(self):
        kwargs = {
            "site_address": "RB131021.7",
            "location": "portland",
            "us_state": "OR",
            "heat_type": "gas heat",
            "pathway": "pct",
            "conditioned_area": 3387.0,
            "electric_utility": "other/none",
            "program": "eto-2017",
            "gas_utility": "cascade",
            "hot_water_ef": 0.82,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": False,
            "qualifying_thermostat": None,
            "qty_shower_head_1p5": 0,
            "qty_shower_head_1p6": 0,
            "qty_shower_head_1p75": 0,
            "code_data": {
                "heating_therms": 720,
                "heating_kwh": 591,
                "cooling_kwh": 1103,
                "hot_water_therms": 176,
                "hot_water_kwh": 0.0,
                "lights_and_appliances_therms": 33,
                "lights_and_appliances_kwh": 8805,
                "electric_cost": 824,
                "gas_cost": 792,
            },
            "improved_data": {
                "heating_therms": 524,
                "heating_kwh": 888,
                "cooling_kwh": 989,
                "hot_water_therms": 91,
                "hot_water_kwh": 0,
                "lights_and_appliances_therms": 33,
                "lights_and_appliances_kwh": 8148,
                "pv_kwh": 5000.0,
                "solar_hot_water_therms": 0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 787,
                "gas_cost": 552,
            },
        }
        calculator = EPSCalculator(**kwargs)

        self.assertEqual(round(calculator.eps_score, 0), 82.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 129.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.23)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.54)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 0.46)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 727.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 727.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 365.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 365.0)
        self.assertEqual(round(calculator.carbon_score, 2), 4.09)
        self.assertEqual(round(calculator.code_carbon_score, 2), 6.06)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1339.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 111.58)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 149.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 6.91)

    def test_high_pv_value(self):
        kwargs = {
            "site_address": "RB131021.7",
            "location": "portland",
            "us_state": "OR",
            "heat_type": "gas heat",
            "pathway": "pct",
            "conditioned_area": 3242.0,
            "electric_utility": "portland general",
            "program": "eto-2017",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.82,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": True,
            "qualifying_thermostat": None,
            "qty_shower_head_1p5": 0,
            "qty_shower_head_1p6": 2,
            "qty_shower_head_1p75": 0,
            "code_data": {
                "heating_therms": 456,
                "heating_kwh": 1058,
                "cooling_kwh": 949,
                "hot_water_therms": 0,
                "hot_water_kwh": 2799,
                "lights_and_appliances_therms": 33,
                "lights_and_appliances_kwh": 8578,
                "electric_cost": 1300,
                "gas_cost": 852,
            },
            "improved_data": {
                "heating_therms": 200,
                "heating_kwh": 228,
                "cooling_kwh": 953,
                "hot_water_therms": 0,
                "hot_water_kwh": 2507,
                "lights_and_appliances_therms": 33,
                "lights_and_appliances_kwh": 7646,
                "pv_kwh": 10000,
                "solar_hot_water_therms": 0,
                "solar_hot_water_kwh": 1452,
                "electric_cost": 1000,
                "gas_cost": 250,
            },
        }
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 23.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 99.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.35)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.76)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 0.24)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 3739.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 2852.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 887.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 1327.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 1012.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 315.0)
        self.assertEqual(round(calculator.carbon_score, 2), 1.36)
        self.assertEqual(round(calculator.code_carbon_score, 2), 9.95)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1250.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 104.17)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 144.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 12.55)

    def test_other_weighted_incentive(self):
        kwargs = {
            "site_address": "RB131021.7",
            "location": "portland",
            "us_state": "OR",
            "heat_type": "heat pump",
            "pathway": "pct",
            "conditioned_area": 2717.0,
            "electric_utility": "portland general",
            "program": "eto-2017",
            "gas_utility": "other/none",
            "hot_water_ef": 0.82,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": False,
            "qualifying_thermostat": None,
            "qty_shower_head_1p5": 1,
            "qty_shower_head_1p6": 1,
            "qty_shower_head_1p75": 0,
            "qty_shower_wand_1p5": 0,
            "code_data": {
                "heating_therms": 0,
                "heating_kwh": 698.4908,
                "cooling_kwh": 0,
                "hot_water_therms": 200.0,
                "hot_water_kwh": 0,
                "lights_and_appliances_therms": 36.1,
                "lights_and_appliances_kwh": 8019.1582,
                "electric_cost": 923.9131,
                "gas_cost": 563.8336,
            },
            "improved_data": {
                "heating_therms": 0,
                "heating_kwh": 589,
                "cooling_kwh": 0,
                "hot_water_therms": 180,
                "hot_water_kwh": 0,
                "lights_and_appliances_therms": 36.1,
                "lights_and_appliances_kwh": 7166.6313,
                "pv_kwh": 0,
                "solar_hot_water_therms": 0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 795.5388,
                "gas_cost": 339.1448,
            },
        }

        calculator = EPSCalculator(**kwargs)

        self.assertEqual(round(calculator.eps_score, 0), 48.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 59.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.19)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.89)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 0.11)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 1025.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 1025.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 0.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 300.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 300.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 0.0)
        self.assertEqual(round(calculator.carbon_score, 2), 5.08)
        self.assertEqual(round(calculator.code_carbon_score, 2), 6.0)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1134.68)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 94.56)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 132.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 11.36)

    def test_net_pv(self):
        # This test is to verify that net energy in the eps reports are = total_kwh - solar generation #

        kwargs = {
            "site_address": None,
            "location": "portland",
            "us_state": "OR",
            "heat_type": "heat pump",
            "pathway": "path 1",
            "conditioned_area": 3113.0,
            "electric_utility": "portland general",
            "program": "eto-2017",
            "gas_utility": "other/none",
            "hot_water_ef": 3.1,
            "has_tankless_water_heater": False,
            "has_solar_hot_water": False,
            "has_ashp": 0,
            "qualifying_thermostat": "no qualifying smart thermostat",
            "qty_shower_head_1p5": None,
            "qty_shower_head_1p6": None,
            "qty_shower_head_1p75": None,
            "qty_shower_wand_1p5": None,
            "code_data": {
                "heating_therms": 0.0,
                "heating_kwh": 7280.92627,
                "cooling_kwh": 1451.220215,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 2545.199463,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 8658.996094,
                "electric_cost": 2269.991943,
                "gas_cost": 0.0,
            },
            "improved_data": {
                "heating_therms": 0.0,
                "heating_kwh": 1883.2323,
                "cooling_kwh": 1315.012939,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 776.154236,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 7719.049316,
                "pv_kwh": 9120.763672,
                "solar_hot_water_therms": 0.0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 286.234039,
                "gas_cost": 0.0,
            },
        }

        calculator = EPSCalculator(**kwargs)

        results = calculator.report_data()
        improved_data = results.get("improved_input")
        solar_kwh = improved_data.get("solar_hot_water_kwh") + improved_data.get("pv_kwh")
        net_electric_kwhs = improved_data.get("total_kwh") - solar_kwh
        self.assertEqual(round(net_electric_kwhs, 2), round(2572.69, 2))

    def test_dfhp_smart_tstat_no_incentive(self):
        kwargs = {
            "site_address": None,
            "location": "portland",
            "us_state": "OR",
            "heat_type": "heat pump",
            "pathway": "path 1",
            "conditioned_area": 3113.0,
            "electric_utility": "portland general",
            "program": "eto-2017",
            "gas_utility": "avista",
            "hot_water_ef": 3.1,
            "has_tankless_water_heater": False,
            "has_solar_hot_water": False,
            "has_ashp": 1,
            "qualifying_thermostat": "yes-ducted air source heat pump",
            "qty_shower_head_1p5": None,
            "qty_shower_head_1p6": None,
            "qty_shower_head_1p75": None,
            "qty_shower_wand_1p5": None,
            "code_data": {
                "heating_therms": 100.0,
                "heating_kwh": 7280.92627,
                "cooling_kwh": 1451.220215,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 2545.199463,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 8658.996094,
                "electric_cost": 2269.991943,
                "gas_cost": 0.0,
            },
            "improved_data": {
                "heating_therms": 95.0,
                "heating_kwh": 1883.2323,
                "cooling_kwh": 1315.012939,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 776.154236,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 7719.049316,
                "pv_kwh": 9120.763672,
                "solar_hot_water_therms": 0.0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 286.234039,
                "gas_cost": 0.0,
            },
        }

        calculator = EPSCalculator(**kwargs)
        unadjusted = calculator.improved_calculations.report_data.get("unadjusted")
        gas_thermostat_savings = unadjusted.get("gas_thermostat_savings")
        electric_thermostat_savings = unadjusted.get("electric_thermostat_savings")
        self.assertEqual(round(gas_thermostat_savings, 2), round(0.0, 2))
        self.assertEqual(round(electric_thermostat_savings, 2), round(0.0, 2))

    def test_other_electric_company_incentive(self):
        kwargs = {
            "site_address": None,
            "location": "medford",
            "us_state": "OR",
            "heat_type": "heat pump",
            "pathway": "path 1",
            "conditioned_area": 1276.0,
            "electric_utility": "other/none",
            "program": "eto-2017",
            "gas_utility": "avista",
            "hot_water_ef": 0.93,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": 1,
            "qualifying_thermostat": "no qualifying smart thermostat",
            "generated_solar_pv_kwh": None,
            "has_heat_pump_water_heater": False,
            "code_data": {
                "heating_therms": 0.0,
                "heating_kwh": 2328.743164,
                "cooling_kwh": 641.750366,
                "hot_water_therms": 167.609497,
                "hot_water_kwh": 0.0,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 4388.898438,
                "electric_cost": 691.215271,
                "gas_cost": 143.825714,
            },
            "improved_data": {
                "heating_therms": 0.0,
                "heating_kwh": 1138.844971,
                "cooling_kwh": 598.5578,
                "hot_water_therms": 85.072273,
                "hot_water_kwh": 0.0,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 4382.916992,
                "pv_kwh": 0.0,
                "solar_hot_water_therms": 0.0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 559.721191,
                "gas_cost": 73.000511,
            },
        }

        calculator = EPSCalculator(**kwargs)

        # Incentive data
        self.assertEqual(calculator.incentives.home_path, "Path 2")
        self.assertEqual(calculator.incentives.home_subtype, "EH+GW")
        self.assertEqual(calculator.incentives.gas_load_profile, "DHW")
        value = calculator.incentives.percentage_improvement
        self.assertGreater(round(value, 2), 0.25)

        value = calculator.incentives.builder_electric_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.builder_gas_incentive
        self.assertGreater(round(value, 2), 0.0)
        value = calculator.incentives.actual_builder_incentive
        self.assertGreater(round(value, 2), 0.0)

        value = calculator.incentives.verifier_electric_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.verifier_gas_incentive
        self.assertGreater(round(value, 2), 0.0)
        value = calculator.incentives.actual_verifier_incentive
        self.assertGreater(round(value, 2), 0.0)
