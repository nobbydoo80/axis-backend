"""__init__.py: Django Calculator Tests"""


import logging

from django.test import TestCase

from axis.core.tests.client import AxisClient
from axis.customer_eto.calculator.eps.calculator import EPSCalculator
from .test_eto_2016 import MIN_ATTRS

__author__ = "Steven K"
__date__ = "12/16/2019 09:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class EPS2018CalculatorTests(TestCase):
    """Test out ETO 2018 Calculator parser"""

    client_class = AxisClient
    fixtures = [
        "eto_simulation_data.json",
    ]

    def get_calculator(self, **kwargs):
        kwargs["program"] = "eto-2018"
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
            "location": "portland",
            "us_state": "OR",
            "heat_type": "gas heat",
            "pathway": "pct",
            "conditioned_area": 1000.0,
            "electric_utility": "portland general",
            "program": "eto-2018",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.82,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": False,
            "qualifying_thermostat": None,
            "qty_shower_head_1p5": 0,
            "qty_shower_head_1p6": 0,
            "qty_shower_head_1p75": 0,
            "qty_shower_wand_1p5": 0,
        }

    @property
    def code_values(self):
        return {
            "heating_therms": 402,
            "heating_kwh": 698.0,
            "cooling_kwh": 0.0,
            "hot_water_therms": 165.0,
            "hot_water_kwh": 0,
            "lights_and_appliances_therms": 36.0,
            "lights_and_appliances_kwh": 8019.0,
            "electric_cost": 924.0,
            "gas_cost": 564.0,
        }

    @property
    def improved_values(self):
        return {
            "heating_therms": 229.0,
            "heating_kwh": 339.0,
            "cooling_kwh": 0,
            "hot_water_therms": 98.0,
            "hot_water_kwh": 0,
            "lights_and_appliances_therms": 36.0,
            "lights_and_appliances_kwh": 7167.0,
            "pv_kwh": 1000.00,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 0.0,
            "electric_cost": 796.0,
            "gas_cost": 339.0,
        }.copy()

    def test_OR_basic(self):
        kwargs = {
            "site_address": "RB131021.7",
            "location": "portland",
            "us_state": "OR",
            "heat_type": "gas heat",
            "pathway": "pct",
            "conditioned_area": 1000.0,
            "electric_utility": "portland general",
            "program": "eto-2018",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.82,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": False,
            "qualifying_thermostat": None,
            "qty_shower_head_1p5": 0,
            "qty_shower_head_1p6": 0,
            "qty_shower_head_1p75": 0,
            "qty_shower_wand_1p5": 0,
            "code_data": {
                "heating_therms": 402,
                "heating_kwh": 698.0,
                "cooling_kwh": 0.0,
                "hot_water_therms": 165.0,
                "hot_water_kwh": 0,
                "lights_and_appliances_therms": 36.0,
                "lights_and_appliances_kwh": 8019.0,
                "electric_cost": 924.0,
                "gas_cost": 564.0,
            },
            "improved_data": {
                "heating_therms": 229.0,
                "heating_kwh": 339.0,
                "cooling_kwh": 0,
                "hot_water_therms": 98.0,
                "hot_water_kwh": 0,
                "lights_and_appliances_therms": 36.0,
                "lights_and_appliances_kwh": 7167.0,
                "pv_kwh": 1000.00,
                "solar_hot_water_therms": 0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 796.0,
                "gas_cost": 339.0,
            },
        }

        calculator = EPSCalculator(**kwargs)

        self.assertEqual(round(calculator.eps_score, 0), 58.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 90.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.31)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.11)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 0.89)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 2849.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 313.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 2536.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 890.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 98.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 792.0)
        self.assertEqual(round(calculator.carbon_score, 2), 5.14)
        self.assertEqual(round(calculator.code_carbon_score, 2), 7.56)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1135.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 94.58)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 74.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 6.21)

    def test_WA_basic(self):
        kwargs = {
            "site_address": "RB131021.7",
            "location": "portland",
            "us_state": "WA",
            "heat_type": "gas heat",
            "pathway": "pct",
            "conditioned_area": 1000.0,
            "electric_utility": "portland general",
            "program": "eto-2018",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.82,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": False,
            "qualifying_thermostat": None,
            "qty_shower_head_1p5": 0,
            "qty_shower_head_1p6": 0,
            "qty_shower_head_1p75": 0,
            "qty_shower_wand_1p5": 0,
            "code_data": {
                "heating_therms": 402,
                "heating_kwh": 698.0,
                "cooling_kwh": 0.0,
                "hot_water_therms": 165.0,
                "hot_water_kwh": 0,
                "lights_and_appliances_therms": 36.0,
                "lights_and_appliances_kwh": 8019.0,
                "electric_cost": 924.0,
                "gas_cost": 564.0,
            },
            "improved_data": {
                "heating_therms": 229.0,
                "heating_kwh": 339.0,
                "cooling_kwh": 0,
                "hot_water_therms": 98.0,
                "hot_water_kwh": 0,
                "lights_and_appliances_therms": 36.0,
                "lights_and_appliances_kwh": 7167.0,
                "pv_kwh": 1000.00,
                "solar_hot_water_therms": 0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 796.0,
                "gas_cost": 339.0,
            },
        }

        calculator = EPSCalculator(**kwargs)

        self.assertEqual(round(calculator.eps_score, 0), 58.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 90.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.39)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.0)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 1.0)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 846.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 846.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 100.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 100.0)
        self.assertEqual(round(calculator.carbon_score, 2), 5.14)
        self.assertEqual(round(calculator.code_carbon_score, 2), 7.56)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1135.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 94.58)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 74.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 6.21)

    def test_OR_partial(self):
        kwargs = {
            "site_address": "RB131021.7",
            "location": "portland",
            "us_state": "OR",
            "heat_type": "heat pump",
            "pathway": "pct",
            "conditioned_area": 1494.0,
            "electric_utility": "portland general",
            "program": "eto-2018",
            "gas_utility": "other",
            "hot_water_ef": 0.82,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": True,
            "qualifying_thermostat": "yes-ducted air source heat pump",
            "qty_shower_head_1p5": 0,
            "qty_shower_head_1p6": 2,
            "qty_shower_head_1p75": 0,
            "qty_shower_wand_1p5": 0,
            "code_data": {
                "heating_therms": 0.0,
                "heating_kwh": 2358.0,
                "cooling_kwh": 402.0,
                "hot_water_therms": 145.0,
                "hot_water_kwh": 0,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 5008.0,
                "electric_cost": 823.0,
                "gas_cost": 135.0,
            },
            "improved_data": {
                "heating_therms": 0.0,
                "heating_kwh": 1501.0,
                "cooling_kwh": 310,
                "hot_water_therms": 88.0,
                "hot_water_kwh": 0,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 5066.0,
                "pv_kwh": 00.00,
                "solar_hot_water_therms": 0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 729.0,
                "gas_cost": 82.0,
            },
        }
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 42.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 59.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.22)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.83)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 0.17)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 1306.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 1306.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 0.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 359.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 359.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 0.0)
        self.assertEqual(round(calculator.carbon_score, 2), 3.62)
        self.assertEqual(round(calculator.code_carbon_score, 2), 4.44)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 811.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 67.58)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 108.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 7.93)

    def _validate_min_attrs(self, calculator):
        for item in MIN_ATTRS:
            try:
                self.assertGreaterEqual(getattr(calculator, item), 0)
            except AssertionError:
                print(item)
                self.assertGreaterEqual(getattr(calculator, item), 0)

    def test_location(self):
        """This is the one test we got from them"""

        for location in [
            "astOria",
            "burns, or",
            "Eugene",
            "MEdford",
            "north bend, or",
            "pendleton",
            "portland",
            "RedmonD",
            "sAlEm",
        ]:
            kwargs = self.site_data.copy()
            kwargs["code_data"] = self.code_values
            kwargs["improved_data"] = self.improved_values
            kwargs["location"] = location
            calculator = self.get_calculator(**kwargs)
            self._validate_min_attrs(calculator)

    def test_location_translation(self):
        kwargs = {
            "site_address": "RB131021.7",
            "location": "eugene",
            "us_state": "OR",
            "heat_type": "heat pump",
            "pathway": "pct",
            "conditioned_area": 1494.0,
            "electric_utility": "portland general",
            "program": "eto-2018",
            "gas_utility": "other",
            "hot_water_ef": 0.82,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": True,
            "qualifying_thermostat": "yes-ducted air source heat pump",
            "qty_shower_head_1p5": 0,
            "qty_shower_head_1p6": 2,
            "qty_shower_head_1p75": 0,
            "qty_shower_wand_1p5": 0,
            "code_data": {
                "heating_therms": 0.0,
                "heating_kwh": 2358.0,
                "cooling_kwh": 402.0,
                "hot_water_therms": 145.0,
                "hot_water_kwh": 0,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 5008.0,
                "electric_cost": 823.0,
                "gas_cost": 135.0,
            },
            "improved_data": {
                "heating_therms": 0.0,
                "heating_kwh": 1501.0,
                "cooling_kwh": 310,
                "hot_water_therms": 88.0,
                "hot_water_kwh": 0,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 5066.0,
                "pv_kwh": 00.00,
                "solar_hot_water_therms": 0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 729.0,
                "gas_cost": 82.0,
            },
        }
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 42.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 59.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.22)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.83)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 0.17)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 1306.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 1306.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 0.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 359.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 359.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 0.0)
        self.assertEqual(round(calculator.carbon_score, 2), 3.62)
        self.assertEqual(round(calculator.code_carbon_score, 2), 4.44)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 811.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 67.58)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 108.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 7.93)

    def test_eight_pct_improvement(self):
        kwargs = {
            "site_address": "RB131021.7",
            "location": "redmond",
            "us_state": "OR",
            "heat_type": "heat pump",
            "pathway": "pct",
            "conditioned_area": 1492.0,
            "electric_utility": "portland general",
            "program": "eto-2018",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.82,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": True,
            "qualifying_thermostat": "no qualifying smart thermostat",
            "qty_shower_head_1p5": 0,
            "qty_shower_head_1p6": 2,
            "qty_shower_head_1p75": 0,
            "qty_shower_wand_1p5": 0,
            "code_data": {
                "heating_therms": 0.0,
                "heating_kwh": 4485.0,
                "cooling_kwh": 622.0,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 2622.0,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 6158.0,
                "electric_cost": 50.0,
                "gas_cost": 0.0,
            },
            "improved_data": {
                "heating_therms": 0.0,
                "heating_kwh": 3679.0,
                "cooling_kwh": 656,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 2215,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 6226.0,
                "pv_kwh": 00.00,
                "solar_hot_water_therms": 0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 25.0,
                "gas_cost": 0.0,
            },
        }
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 76.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 86.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.08)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 1.0)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 0.0)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 582.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 582.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 0.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 300.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 300.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 0.0)
        self.assertEqual(round(calculator.carbon_score, 2), 5.92)
        self.assertEqual(round(calculator.code_carbon_score, 2), 6.43)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 25.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 2.08)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 117.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 8.38)

    def test_zero_pct_improvement(self):
        kwargs = {
            "site_address": None,
            "location": "portland",
            "us_state": "WA",
            "heat_type": "gas heat",
            "pathway": "path 1",
            "conditioned_area": 2472.0,
            "electric_utility": "other/none",
            "program": "eto-2017",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.92,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": 0,
            "qualifying_thermostat": "no qualifying smart thermostat",
            "qty_shower_head_1p5": 0,
            "qty_shower_head_1p6": 0,
            "qty_shower_head_1p75": 0,
            "qty_shower_wand_1p5": 0,
            "code_data": {
                "heating_therms": 0.0,
                "heating_kwh": 197.685471,
                "cooling_kwh": 634.303406,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 0.0,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 5940.369629,
                "electric_cost": 552.480164,
                "gas_cost": 42.318932,
            },
            "improved_data": {
                "heating_therms": 0.0,
                "heating_kwh": 92.42112,
                "cooling_kwh": 802.939758,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 0.0,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 5288.164551,
                "pv_kwh": 0.0,
                "solar_hot_water_therms": 0.0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 504.420563,
                "gas_cost": 37.183498,
            },
        }
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 21.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 23.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.0)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.0)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 0.0)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 0.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 0.0)
        self.assertEqual(round(calculator.carbon_score, 2), 0.37)
        self.assertEqual(round(calculator.code_carbon_score, 2), 0.41)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 541.6)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 45.13)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 120.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 5.55)

    def test_dfhp_smart_tstat_has_incentive(self):
        kwargs = {
            "site_address": None,
            "location": "portland",
            "us_state": "OR",
            "heat_type": "heat pump",
            "pathway": "path 1",
            "conditioned_area": 3113.0,
            "electric_utility": "portland general",
            "program": "eto-2018",
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
        self.assertEqual(round(electric_thermostat_savings, 2), round(225.99, 2))

    def test_other_electric_company_incentive(self):
        kwargs = {
            "site_address": None,
            "location": "medford",
            "us_state": "OR",
            "heat_type": "heat pump",
            "pathway": "path 1",
            "conditioned_area": 1276.0,
            "electric_utility": "other/none",
            "program": "eto-2018",
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
        self.assertEqual(calculator.incentives.electric_load_profile, "Res Air Source HP")
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
