"""__init__.py: Django Calculator Tests"""


import logging

from django.test import TestCase

from axis.core.tests.client import AxisClient
from axis.customer_eto.calculator.eps import ETO_GEN2
from axis.customer_eto.calculator.eps.calculator import EPSCalculator

__author__ = "Steven K"
__date__ = "12/16/2019 09:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class EPS2019CalculatorTests(TestCase):
    """EPS 2019 Calculator Tests"""

    client_class = AxisClient
    fixtures = [
        "eto_simulation_data.json",
    ]

    def get_calculator(self, **kwargs):
        kwargs["program"] = "eto-2019"
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
            "program": "eto-2019",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.82,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": False,
            "qualifying_thermostat": None,
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
            "program": "eto-2019",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.82,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": False,
            "qualifying_thermostat": None,
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

        self.assertEqual(round(calculator.eps_score, 0), 62.0)
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
        self.assertEqual(round(calculator.carbon_score, 2), 6.21)
        self.assertEqual(round(calculator.code_carbon_score, 2), 8.28)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1135.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 94.58)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 74.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 6.79)

    def test_WA_basic(self):
        kwargs = {
            "site_address": "RB131021.7",
            "location": "portland",
            "us_state": "WA",
            "heat_type": "gas heat",
            "pathway": "pct",
            "conditioned_area": 1000.0,
            "electric_utility": "portland general",
            "program": "eto-2019",
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

        self.assertEqual(round(calculator.eps_score, 0), 62.0)
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
        self.assertEqual(round(calculator.carbon_score, 2), 6.21)
        self.assertEqual(round(calculator.code_carbon_score, 2), 8.28)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1135.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 94.58)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 74.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 6.79)

    def test_OR_no_hpwh(self):
        kwargs = {
            "site_address": None,
            "location": "portland",
            "us_state": "OR",
            "heat_type": "heat pump",
            "pathway": "path 1",
            "conditioned_area": 1083.0,
            "electric_utility": "pacific power",
            "program": "eto-2019",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.95,
            "has_tankless_water_heater": True,
            "has_heat_pump_water_heater": False,
            "has_solar_hot_water": False,
            "has_ashp": 1,
            "qualifying_thermostat": "no qualifying smart thermostat",
            "generated_solar_pv_kwh": None,
            "code_data": {
                "heating_therms": 0.0,
                "heating_kwh": 4275.654785,
                "cooling_kwh": 575.4776,
                "hot_water_therms": 144.818726,
                "hot_water_kwh": 0.0,
                "lights_and_appliances_therms": 28.0,
                "lights_and_appliances_kwh": 3654.874512,
                "electric_cost": 921.175659,
                "gas_cost": 144.027084,
            },
            "improved_data": {
                "heating_therms": 0.0,
                "heating_kwh": 3033.377441,
                "cooling_kwh": 607.608887,
                "hot_water_therms": 65.403465,
                "hot_water_kwh": 0.0,
                "lights_and_appliances_therms": 28.0,
                "lights_and_appliances_kwh": 3289.38916,
                "pv_kwh": 0.0,
                "solar_hot_water_therms": 0.0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 744.875,
                "gas_cost": 77.842461,
            },
        }

        # 37051 Solar Water Heater
        # 9120 Gas Heater with solar water heater
        # 65481 Huge Improvement

        # kwargs['simulation_id'] = 9120
        display_results = True
        calculator = EPSCalculator(**kwargs)

        self.assertFalse(calculator.has_heat_pump_water_heater)
        self.assertEqual(round(calculator.eps_score, 0), 57.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 80.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.28)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.75)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 0.25)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 2420.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 1815.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 605.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 696.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 522.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 174.0)
        self.assertEqual(round(calculator.carbon_score, 2), 4.32)
        self.assertEqual(round(calculator.code_carbon_score, 2), 5.65)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 822.72)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 68.56)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 101.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 8.55)

    def test_OR_has_hpwh(self):
        kwargs = {
            "site_address": None,
            "location": "portland",
            "us_state": "OR",
            "heat_type": "heat pump",
            "pathway": "path 1",
            "conditioned_area": 1083.0,
            "electric_utility": "pacific power",
            "program": "eto-2019",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.95,
            "has_tankless_water_heater": False,
            "has_heat_pump_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": 1,
            "qualifying_thermostat": "no qualifying smart thermostat",
            "generated_solar_pv_kwh": None,
            "code_data": {
                "heating_therms": 0.0,
                "heating_kwh": 4275.654785,
                "cooling_kwh": 575.4776,
                "hot_water_therms": 144.818726,
                "hot_water_kwh": 0.0,
                "lights_and_appliances_therms": 28.0,
                "lights_and_appliances_kwh": 3654.874512,
                "electric_cost": 921.175659,
                "gas_cost": 144.027084,
            },
            "improved_data": {
                "heating_therms": 0.0,
                "heating_kwh": 3033.377441,
                "cooling_kwh": 607.608887,
                "hot_water_therms": 65.403465,
                "hot_water_kwh": 0.0,
                "lights_and_appliances_therms": 28.0,
                "lights_and_appliances_kwh": 3289.38916,
                "pv_kwh": 0.0,
                "solar_hot_water_therms": 0.0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 744.875,
                "gas_cost": 77.842461,
            },
        }

        calculator = EPSCalculator(**kwargs)

        self.assertTrue(calculator.has_heat_pump_water_heater)
        self.assertEqual(round(calculator.eps_score, 0), 57.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 80.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.28)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.75)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 0.25)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 2170.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 1565.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 605.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 696.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 522.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 174.0)
        self.assertEqual(round(calculator.carbon_score, 2), 4.32)
        self.assertEqual(round(calculator.code_carbon_score, 2), 5.65)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 822.72)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 68.56)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 101.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 8.55)

    def test_OR_alt_path(self):
        kwargs = {
            "site_address": "RB131021.7",
            "location": "portland",
            "us_state": "OR",
            "heat_type": "gas heat",
            "gas_furnace_afue": 92.0,
            "pathway": "pct",
            "conditioned_area": 1000.0,
            "electric_utility": "portland general",
            "program": "eto-2019",
            "gas_utility": "nw natural",
            "hot_water_ef": 2.1,
            "has_tankless_water_heater": False,
            "has_solar_hot_water": False,
            "has_ashp": False,
            "qualifying_thermostat": None,
            "code_data": {
                "heating_therms": 402,
                "heating_kwh": 698.0,
                "cooling_kwh": 0.0,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 200.0,
                "lights_and_appliances_therms": 36.0,
                "lights_and_appliances_kwh": 8019.0,
                "electric_cost": 924.0,
                "gas_cost": 564.0,
            },
            "improved_data": {
                "heating_therms": 229.0,
                "heating_kwh": 339.0,
                "cooling_kwh": 0,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 120.0,
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

        self.assertEqual(round(calculator.eps_score, 0), 53.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 75.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.29)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.67)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 0.33)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 2501.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 1670.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 831.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 731.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 488.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 243.0)
        self.assertEqual(round(calculator.carbon_score, 2), 5.71)
        self.assertEqual(round(calculator.code_carbon_score, 2), 7.42)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1135.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 94.58)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 74.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 6.79)
        self.assertEqual(round(calculator.therms_savings, 2), 165.51)
        self.assertEqual(round(calculator.kwh_savings, 2), 1510.65)
        self.assertEqual(round(calculator.mbtu_savings, 2), 21.70)

    def test_OR_no_alt_path_afue_test(self):
        kwargs = {
            "site_address": "RB131021.7",
            "location": "portland",
            "us_state": "OR",
            "heat_type": "gas heat",
            "gas_furnace_afue": 94.0,
            "pathway": "pct",
            "conditioned_area": 1000.0,
            "electric_utility": "portland general",
            "program": "eto-2019",
            "gas_utility": "nw natural",
            "hot_water_ef": 2.1,
            "has_tankless_water_heater": False,
            "has_solar_hot_water": False,
            "has_ashp": False,
            "qualifying_thermostat": None,
            "code_data": {
                "heating_therms": 402,
                "heating_kwh": 698.0,
                "cooling_kwh": 0.0,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 200.0,
                "lights_and_appliances_therms": 36.0,
                "lights_and_appliances_kwh": 8019.0,
                "electric_cost": 924.0,
                "gas_cost": 564.0,
            },
            "improved_data": {
                "heating_therms": 229.0,
                "heating_kwh": 339.0,
                "cooling_kwh": 0,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 120.0,
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
        self.assertFalse(calculator.incentives.use_alternate_allocation_method)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 6.79)
        self.assertEqual(round(calculator.therms_savings, 2), 173.0)
        self.assertEqual(round(calculator.kwh_savings, 2), 1291.0)
        self.assertEqual(round(calculator.mbtu_savings, 2), 21.70)

        kwargs["gas_furnace_afue"] = 93.9
        calculator = EPSCalculator(**kwargs)
        self.assertTrue(calculator.incentives.use_alternate_allocation_method)
        self.assertEqual(round(calculator.therms_savings, 2), 165.51)
        self.assertEqual(round(calculator.kwh_savings, 2), 1510.65)
        self.assertEqual(round(calculator.mbtu_savings, 2), 21.70)

        kwargs["hot_water_ef"] = 1.99
        calculator = EPSCalculator(**kwargs)
        self.assertFalse(calculator.incentives.use_alternate_allocation_method)
        self.assertEqual(round(calculator.therms_savings, 2), 173.0)
        self.assertEqual(round(calculator.kwh_savings, 2), 1291.0)
        self.assertEqual(round(calculator.mbtu_savings, 2), 21.70)

    def test_WA_no_alt_path_afue_test(self):
        kwargs = {
            "site_address": None,
            "location": "portland",
            "us_state": "WA",
            "heat_type": "gas heat",
            "pathway": "path 1",
            "conditioned_area": 3218.0,
            "electric_utility": "other/none",
            "program": "eto-2019",
            "gas_utility": "nw natural",
            "hot_water_ef": 3.4,
            "has_tankless_water_heater": False,
            "has_solar_hot_water": False,
            "has_ashp": 0,
            "qualifying_thermostat": "no qualifying smart thermostat",
            "generated_solar_pv_kwh": None,
            "has_heat_pump_water_heater": True,
            "gas_furnace_afue": 70.0,
            "code_data": {
                "heating_therms": 396.703033,
                "heating_kwh": 541.971008,
                "cooling_kwh": 966.392639,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 1587.060791,
                "lights_and_appliances_therms": 33.400002,
                "lights_and_appliances_kwh": 7526.558594,
                "electric_cost": 866.492371,
                "gas_cost": 315.719818,
            },
            "improved_data": {
                "heating_therms": 350.014099,
                "heating_kwh": 411.957855,
                "cooling_kwh": 1035.845215,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 785.076538,
                "lights_and_appliances_therms": 33.400002,
                "lights_and_appliances_kwh": 6638.860352,
                "pv_kwh": 0.0,
                "solar_hot_water_therms": 0.0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 723.682983,
                "gas_cost": 281.453217,
            },
        }

        calculator = EPSCalculator(**kwargs)
        # self.dump_output()
        self.assertFalse(calculator.incentives.use_alternate_allocation_method)
        self.assertEqual(round(calculator.eps_score, 0), 70.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 82.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.08)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.0)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 1.0)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 0.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 0.0)

    def test_zd22780(self):
        kwargs = {
            "site_address": None,
            "location": "portland",
            "us_state": "WA",
            "heat_type": "gas heat",
            "pathway": "path 1",
            "conditioned_area": 3218.0,
            "electric_utility": "other/none",
            "program": "eto-2019",
            "gas_utility": "nw natural",
            "hot_water_ef": 3.4,
            "has_tankless_water_heater": False,
            "has_solar_hot_water": False,
            "has_ashp": 0,
            "qualifying_thermostat": "no qualifying smart thermostat",
            "generated_solar_pv_kwh": None,
            "has_heat_pump_water_heater": True,
            "gas_furnace_afue": None,
            "code_data": {
                "heating_therms": 396.703033,
                "heating_kwh": 541.971008,
                "cooling_kwh": 966.392639,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 1587.060791,
                "lights_and_appliances_therms": 33.400002,
                "lights_and_appliances_kwh": 7526.558594,
                "electric_cost": 866.492371,
                "gas_cost": 315.719818,
            },
            "improved_data": {
                "heating_therms": 351.824951,
                "heating_kwh": 429.882599,
                "cooling_kwh": 1043.404175,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 785.076538,
                "lights_and_appliances_therms": 33.400002,
                "lights_and_appliances_kwh": 6638.860352,
                "pv_kwh": 0.0,
                "solar_hot_water_therms": 0.0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 725.758057,
                "gas_cost": 282.782227,
            },
        }

        calculator = EPSCalculator(**kwargs)
        # self.dump_output(calculator)

        self.assertEqual(calculator.us_state, "WA")
        self.assertIn(calculator.program, ETO_GEN2)
        self.assertEqual(round(calculator.therms_savings, 2), 44.88)
        self.assertEqual(round(calculator.code_total_therms, 2), 554.10)
        self.assertFalse(calculator.use_alternate_allocation_method)
        self.assertEqual(round(calculator.improved_therm_savings, 2), 385.22)
        self.assertEqual(calculator.heat_type, "gas heat")

        # Improved Calculations
        value = calculator.improved_calculations.eps_gas_heat_total_therms
        self.assertEqual(round(value, 2), 385.22)

        value = calculator.improved_calculations.heating_therms_gas_heat_fuel_weight
        self.assertEqual(round(value, 2), 351.82)

        value = calculator.improved_calculations.hot_water_therms_gas_heat_fuel_weight
        self.assertEqual(round(value, 2), 0.0)

        value = calculator.improved_calculations.lights_and_appliances_therms_gas_heat_fuel_weight
        self.assertEqual(round(value, 2), 33.40)

        value = calculator.improved_calculations.solar_hot_water_therms_gas_heat_fuel_weight
        self.assertEqual(round(value, 2), 0.0)

        # Code Calculations
        value = calculator.code_calculations.eps_gas_heat_total_therms
        self.assertEqual(round(value, 2), 430.10)

        value = calculator.code_calculations.heating_therms_gas_heat_fuel_weight
        self.assertEqual(round(value, 2), 396.70)

        value = calculator.code_calculations.hot_water_therms_gas_heat_fuel_weight
        self.assertEqual(round(value, 2), 0.0)

        value = calculator.code_calculations.lights_and_appliances_therms_gas_heat_fuel_weight
        self.assertEqual(round(value, 2), 33.40)

        value = calculator.code_calculations.solar_hot_water_therms_gas_heat_fuel_weight
        self.assertEqual(value, "N/A")

        self.assertEqual(round(calculator.eps_score, 0), 70.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 82.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.08)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.0)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 1.0)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 0.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 0.0)
        self.assertEqual(round(calculator.carbon_score, 2), 2.55)
        self.assertEqual(round(calculator.code_carbon_score, 2), 2.87)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1008.54)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 84.05)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 143.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 6.33)

    def test_other_electric_company_incentive(self):
        kwargs = {
            "site_address": None,
            "location": "medford",
            "us_state": "OR",
            "heat_type": "heat pump",
            "pathway": "path 1",
            "conditioned_area": 1276.0,
            "electric_utility": "other/none",
            "program": "eto-2019",
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
