from django.test import TestCase

from axis.core.tests.client import AxisClient
from axis.customer_eto.calculator.eps.base import EPSInputException
from axis.customer_eto.calculator.eps.calculator import EPSCalculator
from axis.remrate_data.models import Simulation

__author__ = "Steven K"
__date__ = "12/16/2019 09:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


class EPSDumpMixin(object):
    """Dump Assertions"""

    def dump_code_data(self, calculator):
        """This dumps out validations on the lower half of the table"""
        # Calculations CODE Table
        print("# Code Calculation Validations (For EPS)")
        print("value = calculator.code_calculations.eps_gas_heat_total_therms")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.code_calculations.eps_gas_heat_total_therms, 3)
            )
        )
        print("value = calculator.code_calculations.eps_gas_heat_total_kwh")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.code_calculations.eps_gas_heat_total_kwh, 3)
            )
        )

        print("value = calculator.code_calculations.eps_heat_pump_total_therms")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.code_calculations.eps_heat_pump_total_therms, 3)
            )
        )
        print("value = calculator.code_calculations.eps_heat_pump_total_kwh")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.code_calculations.eps_heat_pump_total_kwh, 3)
            )
        )

        print("# Code Calculation Validations (For Carbon)")
        print("value = calculator.code_calculations.carbon_gas_heat_total_therms")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.code_calculations.carbon_gas_heat_total_therms, 3)
            )
        )
        print("value = calculator.code_calculations.carbon_gas_heat_total_kwh")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.code_calculations.carbon_gas_heat_total_kwh, 3)
            )
        )

        print("value = calculator.code_calculations.carbon_heat_pump_total_therms")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.code_calculations.carbon_heat_pump_total_therms, 3)
            )
        )
        print("value = calculator.code_calculations.carbon_heat_pump_total_kwh")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.code_calculations.carbon_heat_pump_total_kwh, 3)
            )
        )

        print("# Code Calculation Validations (Consumption Totals)")

        print("value = calculator.code_calculations.consumption_gas_heat_total_therms")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.code_calculations.consumption_gas_heat_total_therms, 3)
            )
        )
        print("value = calculator.code_calculations.consumption_gas_heat_total_kwh")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.code_calculations.consumption_gas_heat_total_kwh, 3)
            )
        )

        print("value = calculator.code_calculations.consumption_heat_pump_total_therms")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.code_calculations.consumption_heat_pump_total_therms, 3)
            )
        )
        print("value = calculator.code_calculations.consumption_heat_pump_total_kwh")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.code_calculations.consumption_heat_pump_total_kwh, 3)
            )
        )

        print("value = calculator.code_total_mbtu")
        print("self.assertEqual(round(value, 3), {})".format(round(calculator.code_total_mbtu, 3)))

    def dump_improved_data(self, calculator):
        """This dumps out validations on the lower half of the table"""

        # Calculations Improved Table
        print("\n# Improved Calculation Validations (For EPS)")
        print("value = calculator.improved_calculations.eps_gas_heat_total_therms")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.improved_calculations.eps_gas_heat_total_therms, 3)
            )
        )
        print("value = calculator.improved_calculations.eps_gas_heat_total_kwh")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.improved_calculations.eps_gas_heat_total_kwh, 3)
            )
        )

        print("value = calculator.improved_calculations.eps_heat_pump_total_therms")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.improved_calculations.eps_heat_pump_total_therms, 3)
            )
        )
        print("value = calculator.improved_calculations.eps_heat_pump_total_kwh")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.improved_calculations.eps_heat_pump_total_kwh, 3)
            )
        )

        print("# Improved Calculation Validations (For Carbon)")
        print("value = calculator.improved_calculations.carbon_gas_heat_total_therms")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.improved_calculations.carbon_gas_heat_total_therms, 3)
            )
        )
        print("value = calculator.improved_calculations.carbon_gas_heat_total_kwh")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.improved_calculations.carbon_gas_heat_total_kwh, 3)
            )
        )

        print("value = calculator.improved_calculations.carbon_heat_pump_total_therms")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.improved_calculations.carbon_heat_pump_total_therms, 3)
            )
        )
        print("value = calculator.improved_calculations.carbon_heat_pump_total_kwh")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.improved_calculations.carbon_heat_pump_total_kwh, 3)
            )
        )

        print("# Improved Calculation Validations (Consumption Totals)")

        print("value = calculator.improved_calculations.consumption_gas_heat_total_therms")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.improved_calculations.consumption_gas_heat_total_therms, 3)
            )
        )
        print("value = calculator.improved_calculations.consumption_gas_heat_total_kwh")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.improved_calculations.consumption_gas_heat_total_kwh, 3)
            )
        )

        print("value = calculator.improved_calculations.consumption_heat_pump_total_therms")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.improved_calculations.consumption_heat_pump_total_therms, 3)
            )
        )
        print("value = calculator.improved_calculations.consumption_heat_pump_total_kwh")
        print(
            "self.assertEqual(round(value, 3), {})".format(
                round(calculator.improved_calculations.consumption_heat_pump_total_kwh, 3)
            )
        )

        print("value = calculator.improved_total_mbtu")
        print(
            "self.assertEqual(round(value, 3), {})".format(round(calculator.improved_total_mbtu, 3))
        )

    def dump_incentive_data(self, calculator):
        # Incentive Data

        print("\n# Incentive data")
        print(
            "self.assertEqual(calculator.incentives.home_path, '{}')".format(
                calculator.incentives.home_path
            )
        )
        print(
            "self.assertEqual(calculator.incentives.home_subtype, '{}')".format(
                calculator.incentives.home_subtype
            )
        )
        print(
            "self.assertEqual(calculator.incentives.electric_load_profile, '{}')".format(
                calculator.incentives.electric_load_profile
            )
        )
        print(
            "self.assertEqual(calculator.incentives.gas_load_profile, '{}')".format(
                calculator.incentives.gas_load_profile
            )
        )
        print("value = calculator.incentives.measure_life")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.incentives.measure_life, 2)
            )
        )
        print("value = calculator.incentives.percentage_improvement")
        print(
            "self.assertEqual(round(value, 4), {})".format(
                round(calculator.incentives.percentage_improvement, 4)
            )
        )

        print("value = calculator.incentives.full_territory_builder_incentive")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.incentives.full_territory_builder_incentive, 2)
            )
        )

        print("value = calculator.incentives.electric_utility_allocation_pct")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.incentives.electric_utility_allocation_pct, 2)
            )
        )
        print("value = calculator.incentives.gas_utility_allocation_pct")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.incentives.gas_utility_allocation_pct, 2)
            )
        )

        print("value = calculator.incentives.electric_utility_allocation_pct")
        print(
            "self.assertEqual(round(value, 4), {})".format(
                round(calculator.incentives.electric_utility_allocation_pct, 4)
            )
        )
        print("value = calculator.incentives.gas_utility_allocation_pct")
        print(
            "self.assertEqual(round(value, 4), {})".format(
                round(calculator.incentives.gas_utility_allocation_pct, 4)
            )
        )

        print("value = calculator.incentives.builder_electric_incentive")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.incentives.builder_electric_incentive, 2)
            )
        )
        print("value = calculator.incentives.builder_gas_incentive")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.incentives.builder_gas_incentive, 2)
            )
        )

        print("value = calculator.incentives.actual_builder_incentive")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.incentives.actual_builder_incentive, 2)
            )
        )

        print("value = calculator.total_verifier_incentive")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.total_verifier_incentive, 2)
            )
        )
        print("value = calculator.incentives.verifier_electric_incentive")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.incentives.verifier_electric_incentive, 2)
            )
        )
        print("value = calculator.incentives.verifier_gas_incentive")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.incentives.verifier_gas_incentive, 2)
            )
        )

        print("value = calculator.incentives.actual_verifier_incentive")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.incentives.actual_verifier_incentive, 2)
            )
        )

    def dump_result_data(self, calculator):
        # Front Page Results
        print("\n# EPS Final Results")
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
            "self.assertEqual(round(calculator.total_builder_incentive, 2), {})".format(
                round(calculator.total_builder_incentive, 2)
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

    def dump_net_zero_data(self, calculator):
        print("\n# Net Zero data")
        print(
            "self.assertEqual(calculator.net_zero.qualifies_net_zero, {})".format(
                calculator.net_zero.qualifies_net_zero
            )
        )
        print(
            "self.assertEqual(calculator.net_zero.electric_utility, '{}')".format(
                calculator.net_zero.electric_utility
            )
        )
        print(
            "self.assertEqual(round(calculator.net_zero.improved_total_therms, 2), "
            "{})".format(round(calculator.net_zero.improved_total_therms, 2))
        )
        print(
            "self.assertEqual(round(calculator.net_zero.therms_pct_improvement, 2), "
            "{})".format(round(calculator.net_zero.therms_pct_improvement, 2))
        )
        print(
            "self.assertEqual(round(calculator.net_zero.percentage_improvement, 2), "
            "{})".format(round(calculator.net_zero.percentage_improvement, 2))
        )
        print(
            "self.assertEqual(round(calculator.net_zero.pv_kwh_unadjusted, 2), "
            "{})".format(round(calculator.net_zero.pv_kwh_unadjusted, 2))
        )
        print(
            "self.assertEqual(round(calculator.net_zero.improved_total_kwh, 2), "
            "{})".format(round(calculator.net_zero.improved_total_kwh, 2))
        )

        print(
            "self.assertEqual(calculator.net_zero.smart_thermostat_requirement_met, {})".format(
                calculator.net_zero.smart_thermostat_requirement_met
            )
        )
        print(
            "self.assertEqual(calculator.net_zero.solar_exempt, {})".format(
                calculator.net_zero.solar_exempt
            )
        )
        print(
            "self.assertEqual(calculator.net_zero.mini_split_in_use, {})".format(
                calculator.net_zero.mini_split_in_use
            )
        )
        print("value = calculator.net_zero.incentive")
        print(
            "self.assertEqual(round(value, 2), {})".format(round(calculator.net_zero.incentive, 2))
        )
        print("value = calculator.net_zero.net_zero_incentive")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.net_zero.net_zero_incentive, 2)
            )
        )
        print("value = calculator.net_zero.energy_smart_home_incentive")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.net_zero.energy_smart_home_incentive, 2)
            )
        )

        print("value = calculator.net_zero.base_package_energy_smart_incentive")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.net_zero.base_package_energy_smart_incentive, 2)
            )
        )
        print("value = calculator.net_zero.storage_ready_energy_smart_incentive")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.net_zero.storage_ready_energy_smart_incentive, 2)
            )
        )
        print("value = calculator.net_zero.storage_ready_energy_smart_incentive")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.net_zero.storage_ready_energy_smart_incentive, 2)
            )
        )

        print("value = calculator.incentives.mad_max_incentive")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.incentives.mad_max_incentive, 2)
            )
        )
        print("value = calculator.incentives.net_zero_eps_allocation")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.incentives.net_zero_eps_allocation, 2)
            )
        )
        print("value = calculator.incentives.net_zero_solar_allocation")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.incentives.net_zero_solar_allocation, 2)
            )
        )

        print("value = calculator.incentives.net_zero_eps_incentive")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.incentives.net_zero_eps_incentive, 2)
            )
        )
        print("value = calculator.incentives.energy_smart_homes_eps_incentive")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.incentives.energy_smart_homes_eps_incentive, 2)
            )
        )
        print("value = calculator.incentives.net_zero_solar_incentive")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.incentives.net_zero_solar_incentive, 2)
            )
        )
        print("value = calculator.incentives.energy_smart_homes_solar_incentive")
        print(
            "self.assertEqual(round(value, 2), {})".format(
                round(calculator.incentives.energy_smart_homes_solar_incentive, 2)
            )
        )

    def dump_output(self, calculator):
        self.dump_code_data(calculator)
        self.dump_improved_data(calculator)
        self.dump_incentive_data(calculator)
        self.dump_result_data(calculator)
        if calculator.program not in ["eto", "eto-2017", "eto-2018", "eto-2019"]:
            self.dump_net_zero_data(calculator)


class EPSCalculatorTests(TestCase):
    """Test out ETO 2016 Calculator parser"""

    client_class = AxisClient
    fixtures = [
        "eto_simulation_data.json",
    ]

    def get_calculator(self, **kwargs):
        return EPSCalculator(**kwargs)

    @property
    def site_data(self):
        return {
            "site_address": "1234 Sample St. City, OR 12345",
            "location": "portland",
            "heat_type": "gas heat",
            "pathway": "path 2",
            "conditioned_area": "2200",
            "electric_utility": "portland general",
            "gas_utility": "nw natural",
        }

    @property
    def code_values(self):
        return {
            "heating_therms": 411.0,
            "heating_kwh": 331.0,
            "cooling_kwh": 1104.0,
            "hot_water_therms": 207.0,
            "hot_water_kwh": 0.0,
            "lights_and_appliances_therms": 31,
            "lights_and_appliances_kwh": 7098,
            "electric_cost": 852.0,
            "gas_cost": 632.0,
        }

    @property
    def improved_values(self):
        return {
            "heating_therms": 301,
            "heating_kwh": 106,
            "cooling_kwh": 1044,
            "hot_water_therms": 137,
            "hot_water_kwh": 0,
            "lights_and_appliances_therms": 31,
            "lights_and_appliances_kwh": 6372,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 0,
            "pv_kwh": 0.0,
            "electric_cost": 762,
            "gas_cost": 457,
        }.copy()

    def test_inline(self):
        """This is the one test we got from them"""
        kwargs = self.site_data.copy()
        kwargs["code_data"] = self.code_values
        kwargs["improved_data"] = self.improved_values
        calculator = self.get_calculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 73)
        self.assertEqual(round(calculator.code_eps_score, 0), 94)
        self.assertEqual(round(calculator.percentage_improvement, 3), 0.228)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 1650.00)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 330.00)
        self.assertEqual(round(calculator.carbon_score, 2), 6.73)
        self.assertEqual(round(calculator.code_carbon_score, 2), 8.32)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1219.00)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 101.58)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 112)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 9.82)

    def _validate_min_attrs(self, calculator):
        for item in MIN_ATTRS:
            try:
                self.assertGreaterEqual(getattr(calculator, item), 0)
            except AssertionError:
                print(item)
                self.assertGreaterEqual(getattr(calculator, item), 0)

    def test_location(self):
        """This is the one test we got from them"""

        for location in ["Portland", "Medford", "REDmonD"]:
            kwargs = self.site_data.copy()
            kwargs["code_data"] = self.code_values
            kwargs["improved_data"] = self.improved_values
            kwargs["location"] = location
            calculator = self.get_calculator(**kwargs)
            self._validate_min_attrs(calculator)

    def test_heat_type(self):
        """This is the one test we got from them"""

        for item in ["GaS Heat", "HEAT PUMP"]:
            kwargs = self.site_data.copy()
            kwargs["code_data"] = self.code_values
            kwargs["improved_data"] = self.improved_values
            kwargs["heat_type"] = item
            calculator = self.get_calculator(**kwargs)
            self._validate_min_attrs(calculator)

    def test_min_incentive_payment(self):
        """verify that an incentive payment won't be less than $250 combined for utilities."""
        kwargs = self.site_data.copy()
        kwargs["pathway"] = "path 1"
        kwargs["heat_type"] = "gas heat"
        kwargs["code_data"] = self.code_values
        kwargs["improved_data"] = self.improved_values
        kwargs["improved_data"]["heating_therms"] = 400
        kwargs["electric_utility"] = "Other/None"
        calculator = self.get_calculator(**kwargs)
        self._validate_min_attrs(calculator)
        self.assertLessEqual(calculator.total_verifier_incentive, 300)
        self.assertGreaterEqual(
            calculator.incentives.verifier_electric_incentive
            + calculator.incentives.verifier_gas_incentive,
            250,
        )

    def test_utility(self):
        for item in ["Pacific Power", "Portland General", "Other/None"]:
            kwargs = self.site_data.copy()
            kwargs["code_data"] = self.code_values
            kwargs["improved_data"] = self.improved_values
            kwargs["electric_utility"] = item
            calculator = self.get_calculator(**kwargs)
            self._validate_min_attrs(calculator)

    def test_gas_utility(self):
        for item in ["NW Natural", "Cascade", "Other/None"]:
            kwargs = self.site_data.copy()
            kwargs["code_data"] = self.code_values
            kwargs["improved_data"] = self.improved_values
            kwargs["gas_utility"] = item
            calculator = self.get_calculator(**kwargs)
            self._validate_min_attrs(calculator)

    def test_pathway(self):
        for item in ["path 1", "Path 2", "path 3", "path 4", "path 5"]:
            kwargs = self.site_data.copy()
            kwargs["code_data"] = self.code_values
            kwargs["improved_data"] = self.improved_values
            kwargs["pathway"] = item
            calculator = self.get_calculator(**kwargs)
            self._validate_min_attrs(calculator)

    def test_heating(self):
        for item in range(0, 5000, 10):
            kwargs = self.site_data.copy()
            kwargs["code_data"] = self.code_values
            kwargs["code_data"]["heating_therms"] = item
            kwargs["code_data"]["heating_kwh"] = 5000 - item
            kwargs["improved_data"] = self.improved_values
            kwargs["improved_data"]["heating_therms"] = item * 0.85
            kwargs["improved_data"]["heating_kwh"] = 5000 - item * 0.5
            calculator = self.get_calculator(**kwargs)
            self._validate_min_attrs(calculator)

    def test_cooling(self):
        for item in range(0, 5000, 10):
            kwargs = self.site_data.copy()
            kwargs["code_data"] = self.code_values
            kwargs["code_data"]["cooling_kwh"] = item
            kwargs["improved_data"] = self.improved_values
            kwargs["improved_data"]["cooling_kwh"] = 5000 - item * 0.5
            calculator = self.get_calculator(**kwargs)
            self._validate_min_attrs(calculator)

    def test_water_heating(self):
        for item in range(0, 5000, 10):
            kwargs = self.site_data.copy()
            kwargs["code_data"] = self.code_values
            kwargs["code_data"]["water_heating_therms"] = item
            kwargs["code_data"]["water_heating_kwh"] = 5000 - item
            kwargs["improved_data"] = self.improved_values
            kwargs["improved_data"]["water_heating_therms"] = item * 0.75
            kwargs["improved_data"]["water_heating_kwh"] = 5000 - item * 0.66
            calculator = self.get_calculator(**kwargs)
            self._validate_min_attrs(calculator)

    def test_lights_and_appliances_heating(self):
        for item in range(0, 10000, 10):
            kwargs = self.site_data.copy()
            kwargs["code_data"] = self.code_values
            kwargs["code_data"]["lights_and_appliances_therms"] = item
            kwargs["code_data"]["lights_and_appliances_kwh"] = 10000 - item
            kwargs["improved_data"] = self.improved_values
            kwargs["improved_data"]["lights_and_appliances_therms"] = item * 0.05
            kwargs["improved_data"]["lights_and_appliances_kwh"] = 10000 - item * 0.01
            calculator = self.get_calculator(**kwargs)
            self._validate_min_attrs(calculator)

    def test_cost(self):
        for item in range(0, 10000, 10):
            kwargs = self.site_data.copy()
            kwargs["code_data"] = self.code_values
            kwargs["code_data"]["gas_cost"] = item
            kwargs["code_data"]["electric_cost"] = 10000 - item
            kwargs["improved_data"] = self.improved_values
            kwargs["improved_data"]["gas_cost"] = item * 0.05
            kwargs["improved_data"]["electric_cost"] = 10000 - item * 0.01
            calculator = self.get_calculator(**kwargs)
            self._validate_min_attrs(calculator)

    def test_sweep(self):
        for path in ["path 1", "Path 2", "path 3", "path 4", "path 5", "pct"]:
            for item in range(0, 1000):
                kwargs = self.site_data.copy()
                kwargs["pathway"] = path
                kwargs["code_data"] = self.code_values.copy()
                kwargs["code_data"]["heating_therms"] = (item / 500.0) * (
                    kwargs["code_data"]["heating_therms"]
                )
                kwargs["code_data"]["heating_kwh"] = (item / 500.0) * (
                    kwargs["code_data"]["heating_therms"]
                )
                kwargs["code_data"]["cooling_kwh"] = (item / 500.0) * (
                    kwargs["code_data"]["cooling_kwh"]
                )
                kwargs["code_data"]["hot_water_therms"] = (item / 500.0) * (
                    kwargs["code_data"]["hot_water_therms"]
                )
                kwargs["code_data"]["hot_water_kwh"] = (item / 500.0) * 50
                kwargs["code_data"]["lights_and_appliances_therms"] = (item / 500.0) * (
                    kwargs["code_data"]["lights_and_appliances_therms"]
                )
                kwargs["code_data"]["lights_and_appliances_kwh"] = (item / 500.0) * (
                    kwargs["code_data"]["lights_and_appliances_kwh"]
                )
                kwargs["code_data"]["gas_cost"] = (item / 500.0) * (kwargs["code_data"]["gas_cost"])
                kwargs["code_data"]["electric_cost"] = (item / 500.0) * (
                    kwargs["code_data"]["electric_cost"]
                )

                kwargs["improved_data"] = self.improved_values.copy()
                kwargs["improved_data"]["heating_therms"] = (item / 500.0) * (
                    kwargs["improved_data"]["heating_therms"]
                )
                kwargs["improved_data"]["heating_kwh"] = (item / 500.0) * (
                    kwargs["improved_data"]["heating_therms"]
                )
                kwargs["improved_data"]["cooling_kwh"] = (item / 500.0) * (
                    kwargs["improved_data"]["cooling_kwh"]
                )
                kwargs["improved_data"]["hot_water_therms"] = (item / 500.0) * (
                    kwargs["improved_data"]["hot_water_therms"]
                )
                kwargs["improved_data"]["water_heating_kwh"] = (item / 500.0) * 20
                kwargs["improved_data"]["lights_and_appliances_therms"] = (item / 500.0) * (
                    kwargs["improved_data"]["lights_and_appliances_therms"]
                )
                kwargs["improved_data"]["lights_and_appliances_kwh"] = (item / 500.0) * (
                    kwargs["improved_data"]["lights_and_appliances_kwh"]
                )
                kwargs["improved_data"]["gas_cost"] = (item / 500.0) * (
                    kwargs["improved_data"]["gas_cost"]
                )
                kwargs["improved_data"]["electric_cost"] = (item / 500.0) * (
                    kwargs["improved_data"]["electric_cost"]
                )
                kwargs["improved_data"]["gas_cost"] = (item / 500.0) * (
                    kwargs["improved_data"]["gas_cost"]
                )
                kwargs["improved_data"]["solar_hot_water_therms"] = (item / 500.0) * 30.0
                kwargs["improved_data"]["solar_hot_water_kwh"] = (item / 500.0) * 20.0
                kwargs["improved_data"]["pv_kwh"] = (item / 500.0) * 15.0

                calculator = self.get_calculator(**kwargs)
                self._validate_min_attrs(calculator)

    def test_simulation_bad_inputs(self):
        kwargs = self.site_data.copy()
        kwargs.update({"simulation_id": 7})

        err_msg = "Input simulation ID 7 is the wrong type 'Standard Building'.  Must be 'UDRH As Is Building'"
        self.assertRaisesRegex(EPSInputException, err_msg, EPSCalculator, **kwargs)

        kwargs.update({"simulation_id": 3})
        self.assertEqual(Simulation.objects.get(id=3).export_type, 5)
        EPSCalculator(**kwargs)  # This now magically will swap them around.

        kwargs = self.site_data.copy()
        Simulation.objects.get(id=6).similar.clear()
        kwargs.update({"simulation_id": 4})
        self.assertEqual(Simulation.objects.get(id=4).similar.all().count(), 0)
        self.assertEqual(Simulation.objects.get(id=4).solarsystem.type, 1)
        err = (
            "When using a Solar System you must define the non-solar counterpart.  "
            "Re-Run REMRate export with the Active Solar System set to None."
        )
        self.assertRaisesRegex(EPSInputException, err, EPSCalculator, **kwargs)

    def _check_code_data(self, calculator):
        self.assertEqual(round(calculator.code_data.gas_cost), 636)
        self.assertEqual(round(calculator.code_data.electric_cost), 795)

        self.assertEqual(round(calculator.code_data.heating_therms), 413)
        self.assertEqual(round(calculator.code_data.heating_kwh), 331)
        self.assertEqual(round(calculator.code_data.cooling_kwh), 1097)
        self.assertEqual(round(calculator.code_data.hot_water_therms), 209)
        self.assertEqual(round(calculator.code_data.hot_water_kwh), 0)
        self.assertEqual(round(calculator.code_data.lights_and_appliances_therms), 31)
        self.assertEqual(round(calculator.code_data.lights_and_appliances_kwh), 6423)

        self.assertEqual(calculator.code_calculations.solar_hot_water_therms_unadjusted, "N/A")
        self.assertEqual(calculator.code_calculations.solar_hot_water_kwh_unadjusted, "N/A")
        self.assertEqual(calculator.code_calculations.pv_kwh_unadjusted, "N/A")

    def test_simulation_inputs(self):
        kwargs = self.site_data.copy()
        kwargs.update({"simulation_id": 2})
        calculator = self.get_calculator(**kwargs)
        self._check_code_data(calculator)

        self.assertEqual(round(calculator.improved_data.gas_cost), 462)
        self.assertEqual(round(calculator.improved_data.electric_cost), 693)

        self.assertEqual(round(calculator.improved_data.heating_therms), 303)
        self.assertEqual(round(calculator.improved_data.heating_kwh), 106)
        self.assertEqual(round(calculator.improved_data.cooling_kwh), 1036)
        self.assertEqual(round(calculator.improved_data.hot_water_therms), 140)
        self.assertEqual(round(calculator.improved_data.hot_water_kwh), 0)
        self.assertEqual(round(calculator.improved_data.lights_and_appliances_therms), 31)
        self.assertEqual(round(calculator.improved_data.lights_and_appliances_kwh), 5697)

        self.assertEqual(
            round(calculator.improved_calculations.solar_hot_water_therms_unadjusted), 0
        )
        self.assertEqual(round(calculator.improved_calculations.solar_hot_water_kwh_unadjusted), 0)
        self.assertEqual(round(calculator.improved_calculations.pv_kwh_unadjusted), 0)

    def test_simulation_solar_input_swappability(self):
        kwargs = self.site_data.copy()

        self.assertEqual(Simulation.objects.get(id=6).similar.all().count(), 1)
        self.assertEqual(Simulation.objects.get(id=6).similar.all()[0].solarsystem.type, 1)

        kwargs.update({"simulation_id": 4})
        calculator = self.get_calculator(**kwargs)

        # Verify the improved has a solar system and the non-improved does not..
        self.assertEqual(calculator.code_data.simulation.solarsystem.type, 0)
        self.assertEqual(calculator.code_data.simulation.id, 5)
        self.assertEqual(calculator.improved_data.simulation.solarsystem.type, 1)
        self.assertEqual(calculator.improved_data.simulation.id, 4)

        kwargs.update({"simulation_id": 6})
        calculator = self.get_calculator(**kwargs)

        # Verify the improved has a solar system and the non-improved does not..
        self.assertEqual(calculator.code_data.simulation.solarsystem.type, 0)
        self.assertEqual(calculator.code_data.simulation.id, 5)
        self.assertEqual(calculator.improved_data.simulation.solarsystem.type, 1)
        self.assertEqual(calculator.improved_data.simulation.id, 4)

    def test_simulation_solar_input(self):
        kwargs = self.site_data.copy()
        kwargs.update({"simulation_id": 6})
        calculator = self.get_calculator(**kwargs)

        self._check_code_data(calculator)

        self.assertEqual(round(calculator.improved_data.heating_therms), 303)
        self.assertEqual(round(calculator.improved_data.heating_kwh), 106)
        self.assertEqual(round(calculator.improved_data.cooling_kwh), 1036)
        self.assertEqual(round(calculator.improved_data.lights_and_appliances_therms), 31)
        self.assertEqual(round(calculator.improved_data.electric_cost), 693)
        self.assertEqual(round(calculator.improved_data.gas_cost), 376)

        # This is where the swapparoo occurs..
        self.assertEqual(round(calculator.improved_data._reference_non_solar_hot_water_therms), 140)

        # The hot water is broken out between solar and non-solar
        self.assertEqual(round(calculator.improved_data.hot_water_therms), 87)
        self.assertEqual(round(calculator.improved_data.solar_hot_water_therms), 53)
        total = (
            calculator.improved_data.hot_water_therms
            + calculator.improved_data.solar_hot_water_therms
        )
        self.assertEqual(
            round(total), round(calculator.improved_data._reference_non_solar_hot_water_therms)
        )

    def test_simulation_solar_results(self):
        kwargs = self.site_data.copy()
        kwargs.update({"simulation_id": 6})
        calculator = self.get_calculator(**kwargs)

        self.assertEqual(round(calculator.eps_score, 0), 62.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 92.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.28)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.4)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 0.6)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 2800.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 1120.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 1680.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 560.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 224.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 336.0)
        self.assertEqual(round(calculator.carbon_score, 2), 5.88)
        self.assertEqual(round(calculator.code_carbon_score, 2), 7.98)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1068.73)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 89.06)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 112.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 9.82)

    def test_electricity_only(self):
        kwargs = {
            "site_address": "1234 Sample St. City, OR 12345",
            "location": "medford",
            "heat_type": "heat pump",
            "pathway": "path 1",
            "conditioned_area": "2624",
            "electric_utility": "pacific power",
            "gas_utility": "other/none",
        }

        code_data = {
            "heating_therms": 0.0,
            "heating_kwh": 6995.0,
            "cooling_kwh": 1418.0,
            "hot_water_therms": 0.0,
            "hot_water_kwh": 4401.0,
            "lights_and_appliances_therms": 0.0,
            "lights_and_appliances_kwh": 8486.0,
            "electric_cost": 2107.0,
            "gas_cost": 0.0,
        }

        improved_data = {
            "heating_therms": 0,
            "heating_kwh": 4243,
            "cooling_kwh": 1038,
            "hot_water_therms": 0,
            "hot_water_kwh": 4183,
            "lights_and_appliances_therms": 0.0,
            "lights_and_appliances_kwh": 7305,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 0,
            "pv_kwh": 0,
            "electric_cost": 1609,
            "gas_cost": 0,
        }
        kwargs = kwargs.copy()
        kwargs["code_data"] = code_data
        kwargs["improved_data"] = improved_data
        calculator = self.get_calculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 90)
        self.assertEqual(round(calculator.code_eps_score, 0), 134)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.28)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 2650.00)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 530.00)
        self.assertEqual(round(calculator.carbon_score, 2), 19.78)
        self.assertEqual(round(calculator.code_carbon_score, 2), 27.57)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1609)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 134.08)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 140)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 25.45)

    def test_pv_electric(self):
        kwargs = {
            "site_address": "FG130724.1-PV Sample St. City, OR 12345",
            "location": "medford",
            "heat_type": "heat pump",
            "pathway": "pct",
            "conditioned_area": "1735",
            "electric_utility": "pacific power",
            "gas_utility": "other/none",
        }

        code_data = {
            "heating_therms": 0.0,
            "heating_kwh": 3937.0,
            "cooling_kwh": 929.0,
            "hot_water_therms": 209.0,
            "hot_water_kwh": 0.0,
            "lights_and_appliances_therms": 0.0,
            "lights_and_appliances_kwh": 6791.0,
            "electric_cost": 1076.0,
            "gas_cost": 234.0,
        }

        improved_data = {
            "heating_therms": 0,
            "heating_kwh": 2533,
            "cooling_kwh": 811,
            "hot_water_therms": 140,
            "hot_water_kwh": 0.0,
            "lights_and_appliances_therms": 0.0,
            "lights_and_appliances_kwh": 5831.0,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 0,
            "pv_kwh": 3034,
            "electric_cost": 556,
            "gas_cost": 157,
        }
        kwargs = kwargs.copy()
        kwargs["code_data"] = code_data
        kwargs["improved_data"] = improved_data
        calculator = self.get_calculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 43)
        self.assertEqual(round(calculator.code_eps_score, 0), 92)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.29)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 2925.00)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 585.00)
        self.assertEqual(round(calculator.carbon_score, 2), 8.52)
        self.assertEqual(round(calculator.code_carbon_score, 2), 16.35)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 713.00)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 59.42)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 117)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 20.75)

    def test_pv_electric_2(self):
        kwargs = {
            "site_address": "RB131016.1 Sample St. City, OR 12345",
            "location": "portland",
            "heat_type": "heat pump",
            "pathway": "pct",
            "conditioned_area": "4491",
            "electric_utility": "portland general",
            "gas_utility": "other/none",
        }

        code_data = {
            "heating_therms": 0.0,
            "heating_kwh": 19657.0,
            "cooling_kwh": 0.0,
            "hot_water_therms": 0.0,
            "hot_water_kwh": 3830.0,
            "lights_and_appliances_therms": 0.0,
            "lights_and_appliances_kwh": 12158.0,
            "electric_cost": 3777.0,
            "gas_cost": 0.0,
        }

        improved_data = {
            "heating_therms": 0,
            "heating_kwh": 2012,
            "cooling_kwh": 0,
            "hot_water_therms": 0,
            "hot_water_kwh": 2229.0,
            "lights_and_appliances_therms": 0.0,
            "lights_and_appliances_kwh": 8957.0,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 0,
            "pv_kwh": 9450,
            "electric_cost": 383,
            "gas_cost": 0,
        }
        kwargs = kwargs.copy()
        kwargs["code_data"] = code_data
        kwargs["improved_data"] = improved_data
        calculator = self.get_calculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 15)
        self.assertEqual(round(calculator.code_eps_score, 0), 304)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.70)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 5000.00)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 1000.00)
        self.assertEqual(round(calculator.carbon_score, 2), 2.33)
        self.assertEqual(round(calculator.code_carbon_score, 2), 24.52)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 383)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 31.92)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 165)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 14.67)

    def test_gas_only_incentive(self):
        kwargs = {
            "site_address": "RB131021.7",
            "location": "portland",
            "heat_type": "gas heat",
            "pathway": "pct",
            "conditioned_area": "3155",
            "electric_utility": "other/none",
            "gas_utility": "nw natural",
        }

        code_data = {
            "heating_therms": 527.0,
            "heating_kwh": 438.0,
            "cooling_kwh": 1231.0,
            "hot_water_therms": 233.0,
            "hot_water_kwh": 0.0,
            "lights_and_appliances_therms": 33.0,
            "lights_and_appliances_kwh": 8860.0,
            "electric_cost": 538.0,
            "gas_cost": 773.0,
        }

        improved_data = {
            "heating_therms": 338,
            "heating_kwh": 324,
            "cooling_kwh": 1171.0,
            "hot_water_therms": 164,
            "hot_water_kwh": 0.0,
            "lights_and_appliances_therms": 33.0,
            "lights_and_appliances_kwh": 7874.0,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 0,
            "pv_kwh": 0,
            "electric_cost": 477,
            "gas_cost": 521,
        }
        kwargs = kwargs.copy()
        kwargs["code_data"] = code_data
        kwargs["improved_data"] = improved_data
        calculator = self.get_calculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 85)
        self.assertEqual(round(calculator.code_eps_score, 0), 115)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.25)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 1400.00)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 435.00)
        self.assertEqual(round(calculator.carbon_score, 2), 3.69)
        self.assertEqual(round(calculator.code_carbon_score, 2), 5.27)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 998.00)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 83.17)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 141)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 6.56)

    def test_fuel_weight_swapout(self):
        kwargs = {
            "site_address": "4220 Falcon Ridge",
            "location": "medford",
            "heat_type": "heat pump",
            "pathway": "pct",
            "conditioned_area": "2624",
            "electric_utility": "pacific power",
            "gas_utility": None,
        }

        code_data = {
            "heating_therms": 0.0,
            "heating_kwh": 6995.0,
            "cooling_kwh": 1418.0,
            "hot_water_therms": 0.0,
            "hot_water_kwh": 4401.0,
            "lights_and_appliances_therms": 0.0,
            "lights_and_appliances_kwh": 8486.0,
            "electric_cost": 2107.0,
            "gas_cost": 0.0,
        }

        improved_data = {
            "heating_therms": 0,
            "heating_kwh": 4243.0,
            "cooling_kwh": 1038.0,
            "hot_water_therms": 0,
            "hot_water_kwh": 4183.0,
            "lights_and_appliances_therms": 0.0,
            "lights_and_appliances_kwh": 7305.0,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 0,
            "pv_kwh": 0,
            "electric_cost": 1609.30,
            "gas_cost": 0.0,
        }
        kwargs = kwargs.copy()
        kwargs["code_data"] = code_data
        kwargs["improved_data"] = improved_data
        calculator = self.get_calculator(**kwargs)

        self.assertEqual(round(calculator.eps_score, 0), 90)
        self.assertEqual(round(calculator.code_eps_score, 0), 134)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.28)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 2650.00)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 530.00)
        self.assertEqual(round(calculator.carbon_score, 2), 19.78)
        self.assertEqual(round(calculator.code_carbon_score, 2), 27.57)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1609.30)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 134.11)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 140)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 25.45)

    def test_sliding_weights_portland(self):
        kwargs = {
            "site_address": "1234 Sample St. City, OR 12345",
            "location": "portland",
            "heat_type": "heat pump",
            "pathway": "path 1",
            "conditioned_area": "2663",
            "electric_utility": "portland general",
            "gas_utility": "nw natural",
        }

        code_data = {
            "heating_therms": 0.0,
            "heating_kwh": 5401.0,
            "cooling_kwh": 925.0,
            "hot_water_therms": 0.0,
            "hot_water_kwh": 3193.0,
            "lights_and_appliances_therms": 0.0,
            "lights_and_appliances_kwh": 8449.0,
            "electric_cost": 1682.0,
            "gas_cost": 0.0,
        }

        improved_data = {
            "heating_therms": 0,
            "heating_kwh": 4491,
            "cooling_kwh": 853,
            "hot_water_therms": 0,
            "hot_water_kwh": 2674,
            "lights_and_appliances_therms": 0.0,
            "lights_and_appliances_kwh": 7781,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 0,
            "pv_kwh": 0,
            "electric_cost": 1627,
            "gas_cost": 0,
        }
        kwargs = kwargs.copy()
        kwargs["code_data"] = code_data
        kwargs["improved_data"] = improved_data
        calculator = self.get_calculator(**kwargs)

        self.assertEqual(round(calculator.eps_score, 0), 88.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 112.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.17)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 1050.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 300.0)
        self.assertEqual(round(calculator.carbon_score, 2), 8.86)
        self.assertEqual(round(calculator.code_carbon_score, 2), 10.75)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1627.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 135.58)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 131.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 11.26)

    def test_sliding_weights_medford(self):
        kwargs = {
            "site_address": "1234 Sample St. City, OR 12345",
            "location": "medford",
            "heat_type": "heat pump",
            "pathway": "pct",
            "conditioned_area": "906",
            "electric_utility": "pacific power",
            "gas_utility": None,
        }

        code_data = {
            "heating_therms": 0.0,
            "heating_kwh": 1867.0,
            "cooling_kwh": 776.0,
            "hot_water_therms": 0.0,
            "hot_water_kwh": 2798.0,
            "lights_and_appliances_therms": 0.0,
            "lights_and_appliances_kwh": 4983.0,
            "electric_cost": 974.0,
            "gas_cost": 0.0,
        }

        improved_data = {
            "heating_therms": 0,
            "heating_kwh": 760,
            "cooling_kwh": 389,
            "hot_water_therms": 0,
            "hot_water_kwh": 2579,
            "lights_and_appliances_therms": 0.0,
            "lights_and_appliances_kwh": 4276,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 0,
            "pv_kwh": 0,
            "electric_cost": 747,
            "gas_cost": 0,
        }
        kwargs = kwargs.copy()
        kwargs["code_data"] = code_data
        kwargs["improved_data"] = improved_data
        calculator = self.get_calculator(**kwargs)

        self.assertEqual(round(calculator.eps_score, 0), 35.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 53.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.28)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 2725.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 545.00)
        self.assertEqual(round(calculator.carbon_score, 2), 8.66)
        self.assertEqual(round(calculator.code_carbon_score, 2), 12.13)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 747.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 62.25)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 95.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 16.37)

    def test_pv_and_swh(self):
        kwargs = {
            "site_address": "1234 Sample St. City, OR 12345",
            "location": "portland",
            "heat_type": "heat pump",
            "pathway": "pct",
            "conditioned_area": "3227",
            "electric_utility": "portland general",
            "gas_utility": "nw natural",
        }

        code_data = {
            "heating_therms": 0.0,
            "heating_kwh": 6437.0,
            "cooling_kwh": 1231.0,
            "hot_water_therms": 0.0,
            "hot_water_kwh": 2799.0,
            "lights_and_appliances_therms": 0.0,
            "lights_and_appliances_kwh": 9503.0,
            "electric_cost": 2079.0,
            "gas_cost": 0.0,
        }

        improved_data = {
            "heating_therms": 0,
            "heating_kwh": 4812,
            "cooling_kwh": 1202,
            "hot_water_therms": 0,
            "hot_water_kwh": 2540,
            "lights_and_appliances_therms": 0.0,
            "lights_and_appliances_kwh": 8884,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 800,
            "pv_kwh": 3268,
            "electric_cost": 1281.0,
            "gas_cost": 0,
        }
        kwargs = kwargs.copy()
        kwargs["code_data"] = code_data
        kwargs["improved_data"] = improved_data
        calculator = self.get_calculator(**kwargs)

        self.assertEqual(round(calculator.eps_score, 0), 61.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 127.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.19)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 1175.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 300.00)
        self.assertEqual(round(calculator.carbon_score, 2), 7.02)
        self.assertEqual(round(calculator.code_carbon_score, 2), 12.0)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1281.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 106.75)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 141.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 12.31)

    def test_gas_only_min_hundred_bucks(self):
        kwargs = {
            "site_address": "1234 Sample St. City, OR 12345",
            "location": "portland",
            "heat_type": "heat pump",
            "pathway": "pct",
            "conditioned_area": "2000",
            "electric_utility": "other/none",
            "gas_utility": "nw natural",
        }

        code_data = {
            "heating_therms": 0.0,
            "heating_kwh": 2561.0,
            "cooling_kwh": 1256.0,
            "hot_water_therms": 186.0,
            "hot_water_kwh": 0.0,
            "lights_and_appliances_therms": 45.0,
            "lights_and_appliances_kwh": 3659.0,
            "electric_cost": 125.0,
            "gas_cost": 45.0,
        }

        improved_data = {
            "heating_therms": 0,
            "heating_kwh": 1598,
            "cooling_kwh": 896,
            "hot_water_therms": 185,
            "hot_water_kwh": 0.0,
            "lights_and_appliances_therms": 45.0,
            "lights_and_appliances_kwh": 3695,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 0,
            "pv_kwh": 0,
            "electric_cost": 100.0,
            "gas_cost": 25,
        }
        kwargs["code_data"] = code_data
        kwargs["improved_data"] = improved_data

        calculator = self.get_calculator(**kwargs)

        self.assertEqual(round(calculator.eps_score, 0), 54.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 69.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.12)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 100.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 300.0)
        self.assertEqual(round(calculator.carbon_score, 2), 1.71)
        self.assertEqual(round(calculator.code_carbon_score, 2), 1.83)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 125.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 10.42)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 118.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 1.13)

    def test_gas_only_min_three_hundred_bucks(self):
        kwargs = {
            "site_address": "1234 Sample St. City, OR 12345",
            "location": "portland",
            "heat_type": "heat pump",
            "pathway": "path 2",
            "conditioned_area": "3602",
            "electric_utility": "other/none",
            "gas_utility": "cascade",
        }

        code_data = {
            "heating_therms": 0.0,
            "heating_kwh": 6245.9,
            "cooling_kwh": 1448.5,
            "hot_water_therms": 165.4,
            "hot_water_kwh": 0.0,
            "lights_and_appliances_therms": 0.0,
            "lights_and_appliances_kwh": 10322.1,
            "electric_cost": 1541.8,
            "gas_cost": 148.9,
        }

        improved_data = {
            "heating_therms": 0,
            "heating_kwh": 7267.6,
            "cooling_kwh": 1254.1,
            "hot_water_therms": 89.4,
            "hot_water_kwh": 0.0,
            "lights_and_appliances_therms": 0.0,
            "lights_and_appliances_kwh": 10096.1,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 0,
            "pv_kwh": 0,
            "electric_cost": 1603.1,
            "gas_cost": 80.5,
        }
        # calculator = self.get_calculator(**kwargs)

        kwargs = kwargs.copy()
        kwargs["code_data"] = code_data
        kwargs["improved_data"] = improved_data

        calculator = self.get_calculator(**kwargs)

        self.assertEqual(round(calculator.eps_score, 0), 123.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 132.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.09)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 100.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 300.0)
        self.assertEqual(round(calculator.carbon_score, 2), 1.73)
        self.assertEqual(round(calculator.code_carbon_score, 2), 2.19)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1683.6)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 140.3)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 148.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 1.47)

    def test_full_territory_gas_water_heaters(self):
        kwargs = {
            "site_address": "1234 Sample St. City, OR 12345",
            "location": "portland",
            "heat_type": "heat pump",
            "pathway": "pct",
            "conditioned_area": "200",
            "electric_utility": "portland general",
            "gas_utility": "cascade",
        }

        code_data = {
            "heating_therms": 0.0,
            "heating_kwh": 4432,
            "cooling_kwh": 1028,
            "hot_water_therms": 165,
            "hot_water_kwh": 165,
            "lights_and_appliances_therms": 0,
            "lights_and_appliances_kwh": 7226,
            "electric_cost": 125,
            "gas_cost": 45,
        }

        improved_data = {
            "heating_therms": 0,
            "heating_kwh": 3713,
            "cooling_kwh": 864,
            "hot_water_therms": 170,
            "hot_water_kwh": 98,
            "lights_and_appliances_therms": 0,
            "lights_and_appliances_kwh": 6787,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 0,
            "pv_kwh": 0,
            "electric_cost": 100,
            "gas_cost": 25,
        }
        kwargs = kwargs.copy()
        kwargs["code_data"] = code_data
        kwargs["improved_data"] = improved_data

        calculator = self.get_calculator(**kwargs)

        self.assertEqual(round(calculator.eps_score, 0), 82.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 99.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.11)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.88)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 0.12)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 725.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 638.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 87.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 300.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 264.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 36.0)
        self.assertEqual(round(calculator.carbon_score, 2), 7.42)
        self.assertEqual(round(calculator.code_carbon_score, 2), 8.69)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 125.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 10.42)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 84.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 6.67)

    def test_full_territory_no_gas_water_heaters(self):
        kwargs = {
            "site_address": "1234 Sample St. City, OR 12345",
            "location": "portland",
            "heat_type": "heat pump",
            "pathway": "pct",
            "conditioned_area": "200",
            "electric_utility": "portland general",
            "gas_utility": "cascade",
        }

        code_data = {
            "heating_therms": 0.0,
            "heating_kwh": 4432,
            "cooling_kwh": 1028,
            "hot_water_therms": 0,
            "hot_water_kwh": 165,
            "lights_and_appliances_therms": 0,
            "lights_and_appliances_kwh": 7226,
            "electric_cost": 125,
            "gas_cost": 45,
        }

        improved_data = {
            "heating_therms": 0,
            "heating_kwh": 3713,
            "cooling_kwh": 864,
            "hot_water_therms": 0,
            "hot_water_kwh": 98,
            "lights_and_appliances_therms": 0,
            "lights_and_appliances_kwh": 6787,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 0,
            "pv_kwh": 0,
            "electric_cost": 100,
            "gas_cost": 25,
        }
        kwargs = kwargs.copy()
        kwargs["code_data"] = code_data
        kwargs["improved_data"] = improved_data

        calculator = self.get_calculator(**kwargs)

        self.assertEqual(round(calculator.eps_score, 0), 65.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 82.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.16)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 1.0)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 0.0)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 1000.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 1000.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 0.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 300.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 300.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 0.0)
        self.assertEqual(round(calculator.carbon_score, 2), 6.43)
        self.assertEqual(round(calculator.code_carbon_score, 2), 7.73)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 125.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 10.42)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 84.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 6.67)


MIN_ATTRS = [
    "eps_score",
    "code_eps_score",
    "percentage_improvement",
    "total_builder_incentive",
    "total_verifier_incentive",
    "carbon_score",
    "code_carbon_score",
    "estimated_annual_cost",
    "estimated_monthly_cost",
    "projected_size_or_home_eps",
    "projected_size_or_home_carbon",
]
