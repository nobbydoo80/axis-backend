"""test_eto_2020.py: Django """


import logging

__author__ = "Steven K"
__date__ = "12/16/2019 13:54"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from django.test import TestCase

from axis.core.tests.client import AxisClient
from axis.customer_eto.calculator.eps.calculator import EPSCalculator
from .test_eto_2016 import EPSDumpMixin

log = logging.getLogger(__name__)


class EPS2020CalculatorTests(TestCase, EPSDumpMixin):
    """Test ETO 2020 Program"""

    client_class = AxisClient

    @property
    def site_data(self):
        return {
            "site_address": "RB131021.7",
            "location": "portland",
            "us_state": "OR",
            "primary_heating_equipment_type": "Gas Unit Heater",
            "pathway": "pct",
            "conditioned_area": 1000.0,
            "electric_utility": "portland general",
            "program": "eto-2020",
            "gas_utility": "nw natural",
            "builder": None,
            "hot_water_ef": 0.82,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": False,
            "smart_thermostat_brand": "Ecobee4",
            "has_gas_fireplace": "60-69FE",
            "generated_solar_pv_kwh": 1000.00,
        }

    @property
    def code_values(self):
        return {
            "heating_therms": 402,
            "heating_kwh": 698.0,
            "cooling_kwh": 563.0,
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
            "cooling_kwh": 225,
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

    def test_OR_basic_gas_heat_fireplace(self):
        kwargs = self.site_data.copy()
        kwargs["code_data"] = self.code_values.copy()
        kwargs["improved_data"] = self.improved_values.copy()

        calculator = EPSCalculator(**kwargs)

        # Code Calculation Validations (For EPS)
        value = calculator.code_calculations.eps_gas_heat_total_therms
        self.assertEqual(round(value, 3), 691.5)
        value = calculator.code_calculations.eps_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 9280.0)
        value = calculator.code_calculations.eps_heat_pump_total_therms
        self.assertEqual(round(value, 3), 691.5)
        value = calculator.code_calculations.eps_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 10878.42)
        # Code Calculation Validations (For Carbon)
        value = calculator.code_calculations.carbon_gas_heat_total_therms
        self.assertEqual(round(value, 3), 4.045)
        value = calculator.code_calculations.carbon_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 5.058)
        value = calculator.code_calculations.carbon_heat_pump_total_therms
        self.assertEqual(round(value, 3), 4.045)
        value = calculator.code_calculations.carbon_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 5.058)
        # Code Calculation Validations (Consumption Totals)
        value = calculator.code_calculations.consumption_gas_heat_total_therms
        self.assertEqual(round(value, 3), 691.5)
        value = calculator.code_calculations.consumption_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 9280.0)
        value = calculator.code_calculations.consumption_heat_pump_total_therms
        self.assertEqual(round(value, 3), 691.5)
        value = calculator.code_calculations.consumption_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 9280.0)

        # Improved Calculation Validations (For EPS)
        value = calculator.improved_calculations.eps_gas_heat_total_therms
        self.assertEqual(round(value, 3), 437.76)
        value = calculator.improved_calculations.eps_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 6697.16)
        value = calculator.improved_calculations.eps_heat_pump_total_therms
        self.assertEqual(round(value, 3), 451.5)
        value = calculator.improved_calculations.eps_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 6717.5)
        # Improved Calculation Validations (For Carbon)
        value = calculator.improved_calculations.carbon_gas_heat_total_therms
        self.assertEqual(round(value, 3), 2.561)
        value = calculator.improved_calculations.carbon_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 3.65)
        value = calculator.improved_calculations.carbon_heat_pump_total_therms
        self.assertEqual(round(value, 3), 2.641)
        value = calculator.improved_calculations.carbon_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 3.661)
        # Improved Calculation Validations (Consumption Totals)
        value = calculator.improved_calculations.consumption_gas_heat_total_therms
        self.assertEqual(round(value, 3), 437.76)
        value = calculator.improved_calculations.consumption_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 7697.16)
        value = calculator.improved_calculations.consumption_heat_pump_total_therms
        self.assertEqual(round(value, 3), 451.5)
        value = calculator.improved_calculations.consumption_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 7697.16)

        # Incentive data
        self.assertEqual(calculator.incentives.home_path, "Path 3")
        self.assertEqual(calculator.incentives.home_subtype, "GH+GW")
        self.assertEqual(calculator.incentives.electric_load_profile, "Res Space Conditioning")
        self.assertEqual(calculator.incentives.gas_load_profile, "Res Heating")
        value = calculator.incentives.measure_life
        self.assertEqual(round(value, 2), 38.0)
        value = calculator.incentives.percentage_improvement
        self.assertEqual(round(value, 4), 0.3053)
        value = calculator.incentives.full_territory_builder_incentive
        self.assertEqual(round(value, 2), 3221.38)
        value = calculator.incentives.electric_utility_allocation_pct
        self.assertEqual(round(value, 2), 0.23)
        value = calculator.incentives.gas_utility_allocation_pct
        self.assertEqual(round(value, 2), 0.77)
        value = calculator.incentives.electric_utility_allocation_pct
        self.assertEqual(round(value, 4), 0.2264)
        value = calculator.incentives.gas_utility_allocation_pct
        self.assertEqual(round(value, 4), 0.7736)
        value = calculator.incentives.builder_electric_incentive
        self.assertEqual(round(value, 2), 729.0)
        value = calculator.incentives.builder_gas_incentive
        self.assertEqual(round(value, 2), 2492.0)
        value = calculator.total_verifier_incentive
        self.assertEqual(round(value, 2), 831.0)
        value = calculator.incentives.verifier_electric_incentive
        self.assertEqual(round(value, 2), 188.0)
        value = calculator.incentives.verifier_gas_incentive
        self.assertEqual(round(value, 2), 643.0)

        # print(calculator.report())
        # print(calculator.incentives.net_zero_report())
        # print(self.dump_net_zero_data(calculator))

        # EPS Final Results
        self.assertEqual(round(calculator.eps_score, 0), 67.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 101.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.3)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 3221.0)
        self.assertEqual(round(calculator.carbon_score, 2), 6.21)
        self.assertEqual(round(calculator.code_carbon_score, 2), 9.1)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1135.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 94.58)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 74.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 6.79)

    def test_OR_basic_heat_pump_fireplace(self):
        kwargs = self.site_data.copy()
        kwargs["code_data"] = self.code_values.copy()
        kwargs["improved_data"] = self.improved_values.copy()

        kwargs["has_ashp"] = True
        kwargs["smart_thermostat_brand"] = "NEST Learning Thermostat"
        kwargs["primary_heating_equipment_type"] = "Electric Heat Pump \u2013 Air Source Ducted"
        kwargs["has_gas_fireplace"] = ">=70FE"

        calculator = EPSCalculator(**kwargs)

        # print(calculator.report())
        #
        # print(calculator.code_data.report())
        # print(calculator.improved_data.report(show_header=False))
        # print(calculator.code_calculations.report())
        # print(calculator.improved_calculations.report())
        # print(calculator.calculations_report())
        # print(calculator.incentives.report())
        # print(calculator.projected.report())
        # print(calculator.output())
        # print(calculator.dump_exel())
        #
        # print(self.dump_output(calculator))

        # Code Calculation Validations (For EPS)
        value = calculator.code_calculations.eps_gas_heat_total_therms
        self.assertEqual(round(value, 3), 691.5)
        value = calculator.code_calculations.eps_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 9280.0)
        value = calculator.code_calculations.eps_heat_pump_total_therms
        self.assertEqual(round(value, 3), 691.5)
        value = calculator.code_calculations.eps_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 10878.42)
        # Code Calculation Validations (For Carbon)
        value = calculator.code_calculations.carbon_gas_heat_total_therms
        self.assertEqual(round(value, 3), 4.045)
        value = calculator.code_calculations.carbon_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 5.058)
        value = calculator.code_calculations.carbon_heat_pump_total_therms
        self.assertEqual(round(value, 3), 4.045)
        value = calculator.code_calculations.carbon_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 5.058)
        # Code Calculation Validations (Consumption Totals)
        value = calculator.code_calculations.consumption_gas_heat_total_therms
        self.assertEqual(round(value, 3), 691.5)
        value = calculator.code_calculations.consumption_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 9280.0)
        value = calculator.code_calculations.consumption_heat_pump_total_therms
        self.assertEqual(round(value, 3), 691.5)
        value = calculator.code_calculations.consumption_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 9280.0)

        # Improved Calculation Validations (For EPS)
        value = calculator.improved_calculations.eps_gas_heat_total_therms
        self.assertEqual(round(value, 3), 405.72)
        value = calculator.improved_calculations.eps_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 6676.82)
        value = calculator.improved_calculations.eps_heat_pump_total_therms
        self.assertEqual(round(value, 3), 433.2)
        value = calculator.improved_calculations.eps_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 6717.5)
        # Improved Calculation Validations (For Carbon)
        value = calculator.improved_calculations.carbon_gas_heat_total_therms
        self.assertEqual(round(value, 3), 2.373)
        value = calculator.improved_calculations.carbon_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 3.639)
        value = calculator.improved_calculations.carbon_heat_pump_total_therms
        self.assertEqual(round(value, 3), 2.534)
        value = calculator.improved_calculations.carbon_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 3.661)
        # Improved Calculation Validations (Consumption Totals)
        value = calculator.improved_calculations.consumption_gas_heat_total_therms
        self.assertEqual(round(value, 3), 405.72)
        value = calculator.improved_calculations.consumption_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 7676.82)
        value = calculator.improved_calculations.consumption_heat_pump_total_therms
        self.assertEqual(round(value, 3), 433.2)
        value = calculator.improved_calculations.consumption_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 7676.82)

        # Incentive data
        self.assertEqual(calculator.incentives.home_path, "Path 3")
        self.assertEqual(calculator.incentives.home_subtype, "GH+GW")
        self.assertEqual(calculator.incentives.electric_load_profile, "Res Space Conditioning")
        self.assertEqual(calculator.incentives.gas_load_profile, "Res Heating")
        value = calculator.incentives.measure_life
        self.assertEqual(round(value, 2), 38.0)
        value = calculator.incentives.percentage_improvement
        self.assertEqual(round(value, 4), 0.3105)
        value = calculator.incentives.full_territory_builder_incentive
        self.assertEqual(round(value, 2), 3314.53)
        value = calculator.incentives.electric_utility_allocation_pct
        self.assertEqual(round(value, 2), 0.23)
        value = calculator.incentives.gas_utility_allocation_pct
        self.assertEqual(round(value, 2), 0.77)
        value = calculator.incentives.electric_utility_allocation_pct
        self.assertEqual(round(value, 4), 0.2264)
        value = calculator.incentives.gas_utility_allocation_pct
        self.assertEqual(round(value, 4), 0.7736)
        value = calculator.incentives.builder_electric_incentive
        self.assertEqual(round(value, 2), 750.0)
        value = calculator.incentives.builder_gas_incentive
        self.assertEqual(round(value, 2), 2564.0)
        value = calculator.total_verifier_incentive
        self.assertEqual(round(value, 2), 874.0)
        value = calculator.incentives.verifier_electric_incentive
        self.assertEqual(round(value, 2), 198.0)
        value = calculator.incentives.verifier_gas_incentive
        self.assertEqual(round(value, 2), 676.0)

        # EPS Final Results
        self.assertEqual(round(calculator.eps_score, 0), 66.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 106.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.31)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 3315.0)
        self.assertEqual(round(calculator.carbon_score, 2), 6.2)
        self.assertEqual(round(calculator.code_carbon_score, 2), 9.1)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1135.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 94.58)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 99.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 8.39)

    def test_WA_basic_gas_heat_fireplace(self):
        kwargs = self.site_data.copy()
        kwargs["code_data"] = self.code_values.copy()
        kwargs["improved_data"] = self.improved_values.copy()
        kwargs["us_state"] = "WA"

        calculator = EPSCalculator(**kwargs)

        # print(calculator.report())
        #
        # print(calculator.code_data.report())
        # print(calculator.improved_data.report(show_header=False))
        # print(calculator.code_calculations.report())
        # print(calculator.improved_calculations.report())
        # print(calculator.calculations_report())
        # print(calculator.incentives.report())
        # print(calculator.projected.report())
        # print(calculator.output())
        # print(calculator.dump_exel())
        # print(self.dump_output(calculator))

        # Code Calculation Validations (For EPS)
        value = calculator.code_calculations.eps_gas_heat_total_therms
        self.assertEqual(round(value, 3), 691.5)
        value = calculator.code_calculations.eps_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 9280.0)
        value = calculator.code_calculations.eps_heat_pump_total_therms
        self.assertEqual(round(value, 3), 691.5)
        value = calculator.code_calculations.eps_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 10878.42)
        # Code Calculation Validations (For Carbon)
        value = calculator.code_calculations.carbon_gas_heat_total_therms
        self.assertEqual(round(value, 3), 4.045)
        value = calculator.code_calculations.carbon_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 4.297)
        value = calculator.code_calculations.carbon_heat_pump_total_therms
        self.assertEqual(round(value, 3), 4.045)
        value = calculator.code_calculations.carbon_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 4.297)
        # Code Calculation Validations (Consumption Totals)
        value = calculator.code_calculations.consumption_gas_heat_total_therms
        self.assertEqual(round(value, 3), 691.5)
        value = calculator.code_calculations.consumption_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 9280.0)
        value = calculator.code_calculations.consumption_heat_pump_total_therms
        self.assertEqual(round(value, 3), 691.5)
        value = calculator.code_calculations.consumption_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 9280.0)

        # Improved Calculation Validations (For EPS)
        value = calculator.improved_calculations.eps_gas_heat_total_therms
        self.assertEqual(round(value, 3), 437.76)
        value = calculator.improved_calculations.eps_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 6731.0)
        value = calculator.improved_calculations.eps_heat_pump_total_therms
        self.assertEqual(round(value, 3), 451.5)
        value = calculator.improved_calculations.eps_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 6731.0)
        # Improved Calculation Validations (For Carbon)
        value = calculator.improved_calculations.carbon_gas_heat_total_therms
        self.assertEqual(round(value, 3), 2.561)
        value = calculator.improved_calculations.carbon_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 3.116)
        value = calculator.improved_calculations.carbon_heat_pump_total_therms
        self.assertEqual(round(value, 3), 2.124)
        value = calculator.improved_calculations.carbon_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 3.116)
        # Improved Calculation Validations (Consumption Totals)
        value = calculator.improved_calculations.consumption_gas_heat_total_therms
        self.assertEqual(round(value, 3), 437.76)
        value = calculator.improved_calculations.consumption_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 7731.0)
        value = calculator.improved_calculations.consumption_heat_pump_total_therms
        self.assertEqual(round(value, 3), 451.5)
        value = calculator.improved_calculations.consumption_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 7731.0)

        # Incentive data
        self.assertEqual(calculator.incentives.home_path, "Path 3")
        self.assertEqual(calculator.incentives.home_subtype, "GH+GW")
        self.assertEqual(calculator.incentives.electric_load_profile, "Res Lighting")
        self.assertEqual(calculator.incentives.gas_load_profile, "Res Heating")
        value = calculator.incentives.measure_life
        self.assertEqual(round(value, 2), 42.0)
        value = calculator.incentives.percentage_improvement
        self.assertEqual(round(value, 4), 0.3669)
        value = calculator.incentives.full_territory_builder_incentive
        self.assertEqual(round(value, 2), 1200.82)
        value = calculator.incentives.electric_utility_allocation_pct
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.gas_utility_allocation_pct
        self.assertEqual(round(value, 2), 1.0)
        value = calculator.incentives.electric_utility_allocation_pct
        self.assertEqual(round(value, 4), 0.0)
        value = calculator.incentives.gas_utility_allocation_pct
        self.assertEqual(round(value, 4), 1.0)
        value = calculator.incentives.builder_electric_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.builder_gas_incentive
        self.assertEqual(round(value, 2), 1201.0)
        value = calculator.total_verifier_incentive
        self.assertEqual(round(value, 2), 100.0)
        value = calculator.incentives.verifier_electric_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.verifier_gas_incentive
        self.assertEqual(round(value, 2), 100.0)

        # EPS Final Results
        self.assertEqual(round(calculator.eps_score, 0), 67.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 101.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.36)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 1201.0)
        self.assertEqual(round(calculator.carbon_score, 2), 5.68)
        self.assertEqual(round(calculator.code_carbon_score, 2), 8.34)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1135.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 94.58)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 74.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 6.21)

    def test_OR_alt_path_gas_heat_valid_builder(self):
        """Test OR alternate allocations"""
        from ...enumerations import ETO_2020_BUILDER_CHOICES
        from axis.company.models import Company

        kwargs = self.site_data.copy()
        kwargs["primary_heating_equipment_type"] = "Gas Furnace"

        kwargs["builder"] = ETO_2020_BUILDER_CHOICES[0][0]

        kwargs["code_data"] = self.code_values.copy()
        kwargs["improved_data"] = self.improved_values.copy()

        kwargs["code_data"]["hot_water_kwh"] = 200.0
        kwargs["code_data"]["hot_water_therms"] = 0.0
        kwargs["improved_data"]["hot_water_kwh"] = 140.0
        kwargs["improved_data"]["hot_water_therms"] = 0.0

        kwargs["hot_water_ef"] = 2.01

        calculator = EPSCalculator(**kwargs)

        self.assertTrue(calculator.use_alternate_allocation_method)
        self.assertTrue(calculator.incentives.use_alternate_allocation_method)
        self.assertEqual(calculator.builder, ETO_2020_BUILDER_CHOICES[0][0])
        self.assertEqual(calculator.primary_heat_type, "Gas Furnace")
        self.assertGreater(calculator.hot_water_ef, 2.0)

        # print(self.dump_net_zero_data(calculator))

        # EPS Final Results
        self.assertEqual(round(calculator.eps_score, 0), 57.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 85.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.28)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 2869.0)
        self.assertEqual(round(calculator.carbon_score, 2), 5.71)
        self.assertEqual(round(calculator.code_carbon_score, 2), 8.25)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1135.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 94.58)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 74.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 6.79)

        # Throw the company object at it.
        kwargs["builder"] = Company.objects.create(name="DR", slug=ETO_2020_BUILDER_CHOICES[0][0])
        calculator = EPSCalculator(**kwargs)

        self.assertTrue(calculator.use_alternate_allocation_method)
        self.assertTrue(calculator.incentives.use_alternate_allocation_method)
        self.assertEqual(calculator.builder, ETO_2020_BUILDER_CHOICES[0][0])
        self.assertEqual(calculator.primary_heat_type, "Gas Furnace")
        self.assertGreater(calculator.hot_water_ef, 2.0)
        self.assertEqual(round(calculator.eps_score, 0), 57.0)

    def test_fireplace_inputs(self):
        """Test out the Fireplace Inputs"""
        kwargs = self.site_data.copy()
        kwargs["code_data"] = self.code_values.copy()
        kwargs["improved_data"] = self.improved_values.copy()

        kwargs["has_gas_fireplace"] = "No fireplace".lower()
        calculator = EPSCalculator(**kwargs)
        self.assertFalse(calculator.has_gas_fireplace)

        kwargs["has_gas_fireplace"] = "<=49FE".lower()
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(calculator.has_gas_fireplace, kwargs["has_gas_fireplace"].upper())

        kwargs["has_gas_fireplace"] = "50-59FE".lower()
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(calculator.has_gas_fireplace, kwargs["has_gas_fireplace"].upper())

        kwargs["has_gas_fireplace"] = "60-69FE".lower()
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(calculator.has_gas_fireplace, kwargs["has_gas_fireplace"].upper())

        kwargs["has_gas_fireplace"] = ">=70FE".lower()
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(calculator.has_gas_fireplace, kwargs["has_gas_fireplace"].upper())

    def test_flooring_rater_incentive(self):
        # https://staging.pivotalenergy.net/home//86159//#/tabs/programs
        kwargs = {
            "site_address": None,
            "location": "portland",
            "us_state": "OR",
            "primary_heating_equipment_type": "Gas Unit Heater",
            "pathway": "path 1",
            "conditioned_area": 3390.0,
            "electric_utility": "other/none",
            "program": "eto-2020",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.82,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": 0,
            "smart_thermostat_brand": "Ecobee4",
            "generated_solar_pv_kwh": None,
            "has_heat_pump_water_heater": False,
            "gas_furnace_afue": None,
            "code_data": {
                "heating_therms": 521.588074,
                "heating_kwh": 561.645325,
                "cooling_kwh": 1048.147217,
                "hot_water_therms": 206.78717,
                "hot_water_kwh": 0.0,
                "lights_and_appliances_therms": 36.099998,
                "lights_and_appliances_kwh": 7503.901855,
                "electric_cost": 563.036865,
                "gas_cost": 636.188416,
            },
            "improved_data": {
                "heating_therms": 415.728119,
                "heating_kwh": 630.042725,
                "cooling_kwh": 1095.773926,
                "hot_water_therms": 133.119904,
                "hot_water_kwh": 0.0,
                "lights_and_appliances_therms": 36.099998,
                "lights_and_appliances_kwh": 7503.901855,
                "pv_kwh": 0.0,
                "solar_hot_water_therms": 0.0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 570.372437,
                "gas_cost": 486.75827,
            },
        }

        calculator = EPSCalculator(**kwargs)

        # Incentive data
        self.assertEqual(calculator.incentives.home_path, "Path 1")
        self.assertEqual(calculator.incentives.home_subtype, "GH+GW")
        self.assertEqual(calculator.incentives.electric_load_profile, "Res Space Conditioning")
        self.assertEqual(calculator.incentives.gas_load_profile, "Res Heating")
        value = calculator.incentives.measure_life
        self.assertEqual(round(value, 2), 34.0)
        value = calculator.incentives.percentage_improvement
        self.assertEqual(round(value, 4), 0.1897)
        value = calculator.incentives.full_territory_builder_incentive
        self.assertEqual(round(value, 2), 1663.46)
        value = calculator.incentives.electric_utility_allocation_pct
        self.assertEqual(round(value, 2), 0.08)
        value = calculator.incentives.gas_utility_allocation_pct
        self.assertEqual(round(value, 2), 0.92)
        value = calculator.incentives.electric_utility_allocation_pct
        self.assertEqual(round(value, 4), 0.08)
        value = calculator.incentives.gas_utility_allocation_pct
        self.assertEqual(round(value, 4), 0.92)
        value = calculator.incentives.builder_electric_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.builder_gas_incentive
        self.assertEqual(round(value, 2), 1530.0)
        value = calculator.total_verifier_incentive
        self.assertEqual(round(value, 2), 300.0)
        value = calculator.incentives.verifier_electric_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.verifier_gas_incentive
        self.assertEqual(round(value, 2), 300.0)

    def test_builder_electric_incentive(self):
        # https://staging.pivotalenergy.net/home//86179//#/tabs/programs
        kwargs = {
            "site_address": None,
            "location": "portland",
            "us_state": "OR",
            "primary_heating_equipment_type": "Gas Furnace",
            "pathway": "path 1",
            "conditioned_area": 1393.0,
            "electric_utility": "portland general",
            "program": "eto-2020",
            "gas_utility": "nw natural",
            "hot_water_ef": 2.7,
            "has_tankless_water_heater": False,
            "has_solar_hot_water": False,
            "has_ashp": 0,
            "smart_thermostat_brand": "N/A",
            "generated_solar_pv_kwh": None,
            "has_heat_pump_water_heater": True,
            "gas_furnace_afue": None,
            "code_data": {
                "heating_therms": 244.77063,
                "heating_kwh": 216.290817,
                "cooling_kwh": 0.0,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 2622.320801,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 4788.064453,
                "electric_cost": 905.231812,
                "gas_cost": 203.557663,
            },
            "improved_data": {
                "heating_therms": 151.858749,
                "heating_kwh": 210.137482,
                "cooling_kwh": 0.0,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 783.51178,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 4506.068359,
                "pv_kwh": 0.0,
                "solar_hot_water_therms": 0.0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 652.763367,
                "gas_cost": 126.289749,
            },
        }
        calculator = EPSCalculator(**kwargs)

        # Incentive data
        self.assertEqual(calculator.incentives.home_path, "Path 3")
        self.assertEqual(calculator.incentives.home_subtype, "GH+EW")
        self.assertEqual(calculator.incentives.electric_load_profile, "Res Space Conditioning")
        self.assertEqual(calculator.incentives.gas_load_profile, "Res Heating")
        value = calculator.incentives.measure_life
        self.assertEqual(round(value, 2), 33.0)
        value = calculator.incentives.percentage_improvement
        self.assertEqual(round(value, 4), 0.3277)
        value = calculator.incentives.full_territory_builder_incentive
        self.assertEqual(round(value, 2), 3636.37)
        value = calculator.incentives.electric_utility_allocation_pct
        self.assertEqual(round(value, 2), 0.75)
        value = calculator.incentives.gas_utility_allocation_pct
        self.assertEqual(round(value, 2), 0.25)
        value = calculator.incentives.electric_utility_allocation_pct
        self.assertEqual(round(value, 4), 0.7547)
        value = calculator.incentives.gas_utility_allocation_pct
        self.assertEqual(round(value, 4), 0.2453)
        value = calculator.incentives.builder_electric_incentive
        self.assertEqual(round(value, 2), 2494.0)
        value = calculator.incentives.builder_gas_incentive
        self.assertEqual(round(value, 2), 892.0)
        value = calculator.incentives.builder_incentive
        self.assertEqual(round(value, 2), 3386.0)
        value = calculator.total_verifier_incentive
        self.assertEqual(round(value, 2), 1028.0)
        value = calculator.incentives.verifier_electric_incentive
        self.assertEqual(round(value, 2), 776.0)
        value = calculator.incentives.verifier_gas_incentive
        self.assertEqual(round(value, 2), 252.0)
        value = calculator.incentives.actual_verifier_incentive
        self.assertEqual(round(value, 2), 1027.77)

    def test_improved_hp_kwh_calcs(self):
        # https://staging.pivotalenergy.net/home//86180//#/tabs/programs
        kwargs = {
            "site_address": None,
            "location": "portland",
            "us_state": "OR",
            "primary_heating_equipment_type": "Electric Heat Pump \u2013 Air Source Ducted",
            "pathway": "path 1",
            "conditioned_area": 480.0,
            "electric_utility": "portland general",
            "program": "eto-2020",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.95,
            "has_tankless_water_heater": False,
            "has_solar_hot_water": False,
            "has_ashp": 1,
            "smart_thermostat_brand": "N/A",
            "generated_solar_pv_kwh": None,
            "has_heat_pump_water_heater": False,
            "gas_furnace_afue": None,
            "code_data": {
                "heating_therms": 0.0,
                "heating_kwh": 889.39563,
                "cooling_kwh": 184.94162,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 1575.468018,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 2989.086914,
                "electric_cost": 669.065186,
                "gas_cost": 0.0,
            },
            "improved_data": {
                "heating_therms": 0.0,
                "heating_kwh": 647.915344,
                "cooling_kwh": 163.020279,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 1546.226685,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 2989.086914,
                "pv_kwh": 0.0,
                "solar_hot_water_therms": 0.0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 634.394958,
                "gas_cost": 0.0,
            },
        }

        calculator = EPSCalculator(**kwargs)

        # Improved Calculation Validations (For EPS)
        value = calculator.improved_calculations.eps_gas_heat_total_therms
        self.assertEqual(round(value, 3), 0.0)
        value = calculator.improved_calculations.eps_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 6011.127)
        value = calculator.improved_calculations.eps_heat_pump_total_therms
        self.assertEqual(round(value, 3), 0.0)
        value = calculator.improved_calculations.eps_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 7494.853)
        # Improved Calculation Validations (For Carbon)
        value = calculator.improved_calculations.carbon_gas_heat_total_therms
        self.assertEqual(round(value, 3), 0.0)
        value = calculator.improved_calculations.carbon_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 2.914)
        value = calculator.improved_calculations.carbon_heat_pump_total_therms
        self.assertEqual(round(value, 3), 0.0)
        value = calculator.improved_calculations.carbon_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 2.914)
        # Improved Calculation Validations (Consumption Totals)
        value = calculator.improved_calculations.consumption_gas_heat_total_therms
        self.assertEqual(round(value, 3), 0.0)
        value = calculator.improved_calculations.consumption_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 5346.249)
        value = calculator.improved_calculations.consumption_heat_pump_total_therms
        self.assertEqual(round(value, 3), 0.0)
        value = calculator.improved_calculations.consumption_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 5346.249)

    def test_other_electric_company_incentive(self):
        kwargs = {
            "site_address": None,
            "location": "medford",
            "us_state": "OR",
            "primary_heating_equipment_type": "Electric Heat Pump \u2013 Air Source Ducted",
            "pathway": "path 1",
            "conditioned_area": 1276.0,
            "electric_utility": "other/none",
            "program": "eto-2020",
            "gas_utility": "avista",
            "hot_water_ef": 0.93,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": 1,
            "smart_thermostat_brand": "N/A",
            "generated_solar_pv_kwh": None,
            "has_heat_pump_water_heater": False,
            "gas_furnace_afue": None,
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
        # self.dump_improved_data(calculator)

        # Incentive data
        self.assertEqual(calculator.incentives.home_path, "N/A")
        self.assertEqual(calculator.incentives.home_subtype, "EH+GW")
        self.assertEqual(calculator.incentives.electric_load_profile, "N/A")
        self.assertEqual(calculator.incentives.gas_load_profile, "N/A")

        value = calculator.incentives.percentage_improvement
        self.assertEqual(round(value, 2), 0.0)

        value = calculator.code_total_mbtu
        self.assertEqual(round(value, 3), 0.0)
        value = calculator.improved_total_mbtu
        self.assertEqual(round(value, 3), 0.0)

        value = calculator.incentives.builder_electric_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.builder_gas_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.actual_builder_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.total_verifier_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.verifier_electric_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.verifier_gas_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.actual_verifier_incentive
        self.assertEqual(round(value, 2), 0.0)

    def test_partial_incentive_other(self):
        kwargs = {
            "site_address": None,
            "location": "portland",
            "us_state": "OR",
            "primary_heating_equipment_type": "Gas Boiler",
            "pathway": "path 1",
            "conditioned_area": 2502.0,
            "electric_utility": "other/none",
            "program": "eto-2020",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.94,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": 0,
            "smart_thermostat_brand": "N/A",
            "generated_solar_pv_kwh": None,
            "has_heat_pump_water_heater": False,
            "gas_furnace_afue": None,
            "code_data": {
                "heating_therms": 375.84021,
                "heating_kwh": 416.171997,
                "cooling_kwh": 0.0,
                "hot_water_therms": 166.048569,
                "hot_water_kwh": 0.0,
                "lights_and_appliances_therms": 30.700001,
                "lights_and_appliances_kwh": 5245.103516,
                "electric_cost": 671.888184,
                "gas_cost": 476.5289,
            },
            "improved_data": {
                "heating_therms": 302.464722,
                "heating_kwh": 511.839935,
                "cooling_kwh": 0.0,
                "hot_water_therms": 71.106705,
                "hot_water_kwh": 0.0,
                "lights_and_appliances_therms": 30.700001,
                "lights_and_appliances_kwh": 5272.195313,
                "pv_kwh": 0.0,
                "solar_hot_water_therms": 0.0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 686.435669,
                "gas_cost": 336.383331,
            },
        }
        calculator = EPSCalculator(**kwargs)

        # Incentive data
        self.assertEqual(calculator.incentives.home_path, "Path 2")
        self.assertEqual(calculator.incentives.home_subtype, "GH+GW")
        self.assertEqual(calculator.incentives.electric_load_profile, "Res Space Conditioning")
        self.assertEqual(calculator.incentives.gas_load_profile, "Res Heating")
        value = calculator.incentives.measure_life
        self.assertEqual(round(value, 2), 34.0)
        value = calculator.incentives.percentage_improvement
        self.assertEqual(round(value, 4), 0.2143)
        value = calculator.incentives.full_territory_builder_incentive
        self.assertEqual(round(value, 2), 1913.91)
        value = calculator.incentives.electric_utility_allocation_pct
        self.assertEqual(round(value, 2), 0.08)
        value = calculator.incentives.gas_utility_allocation_pct
        self.assertEqual(round(value, 2), 0.92)
        value = calculator.incentives.electric_utility_allocation_pct
        self.assertEqual(round(value, 4), 0.08)
        value = calculator.incentives.gas_utility_allocation_pct
        self.assertEqual(round(value, 4), 0.92)
        value = calculator.incentives.builder_electric_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.builder_gas_incentive
        self.assertEqual(round(value, 2), 1761.0)
        value = calculator.incentives.actual_builder_incentive
        self.assertEqual(round(value, 2), 1760.8)
        value = calculator.total_verifier_incentive
        self.assertEqual(round(value, 2), 303.0)
        value = calculator.incentives.verifier_electric_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.verifier_gas_incentive
        self.assertEqual(round(value, 2), 303.0)
        value = calculator.incentives.actual_verifier_incentive
        self.assertEqual(round(value, 2), 303.05)

    def test_min_pct_improvement(self):
        kwargs = {
            "site_address": None,
            "location": "portland",
            "us_state": "OR",
            "primary_heating_equipment_type": "Gas Unit Heater",
            "pathway": "path 1",
            "conditioned_area": 2886.0,
            "electric_utility": "portland general",
            "program": "eto-2020",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.93,
            "has_tankless_water_heater": False,
            "has_solar_hot_water": False,
            "has_ashp": 0,
            "smart_thermostat_brand": "N/A",
            "generated_solar_pv_kwh": None,
            "has_heat_pump_water_heater": False,
            "gas_furnace_afue": 92.099998,
            "code_data": {
                "heating_therms": 426.496094,
                "heating_kwh": 434.067352,
                "cooling_kwh": 0.0,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 3114.425293,
                "lights_and_appliances_therms": 33.400002,
                "lights_and_appliances_kwh": 6256.010254,
                "electric_cost": 1163.684448,
                "gas_cost": 382.520996,
            },
            "improved_data": {
                "heating_therms": 354.287689,
                "heating_kwh": 412.663666,
                "cooling_kwh": 0.0,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 2982.916016,
                "lights_and_appliances_therms": 33.400002,
                "lights_and_appliances_kwh": 6256.010254,
                "pv_kwh": 0.0,
                "solar_hot_water_therms": 0.0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 1145.539551,
                "gas_cost": 322.47052,
            },
        }

        calculator = EPSCalculator(**kwargs)

        # Incentive data
        self.assertEqual(calculator.incentives.home_path, "Path 1")
        self.assertEqual(calculator.incentives.home_subtype, "GH+EW")
        self.assertEqual(calculator.incentives.electric_load_profile, "Res Space Conditioning")
        self.assertEqual(calculator.incentives.gas_load_profile, "Res Heating")
        value = calculator.incentives.measure_life
        self.assertEqual(round(value, 2), 35.0)
        value = calculator.incentives.percentage_improvement
        self.assertEqual(round(value, 4), 0.0975)
        value = calculator.incentives.full_territory_builder_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.electric_utility_allocation_pct
        self.assertEqual(round(value, 2), 0.38)
        value = calculator.incentives.gas_utility_allocation_pct
        self.assertEqual(round(value, 2), 0.62)
        value = calculator.incentives.electric_utility_allocation_pct
        self.assertEqual(round(value, 4), 0.3791)
        value = calculator.incentives.gas_utility_allocation_pct
        self.assertEqual(round(value, 4), 0.6209)
        value = calculator.incentives.builder_electric_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.builder_gas_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.actual_builder_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.total_verifier_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.verifier_electric_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.verifier_gas_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.actual_verifier_incentive
        self.assertEqual(round(value, 2), 0.0)


class EPS2020NetZeroCalculatorTests(TestCase, EPSDumpMixin):
    """Test ETO 2020 Net Zero Program"""

    client_class = AxisClient

    @property
    def site_data(self):
        return {
            "site_address": "RB131021.7",
            "location": "portland",
            "us_state": "OR",
            "primary_heating_equipment_type": "Electric Heat Pump \u2013 Mini Split Ducted",
            "pathway": "pct",
            "conditioned_area": 1927.0,
            "electric_utility": "pacific power",
            "program": "eto-2020",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.82,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": True,
            "smart_thermostat_brand": "Ecobee4",
            "has_gas_fireplace": "60-69FE",
            "generated_solar_pv_kwh": 1200.00,
            "grid_harmonization_elements": "Energy smart homes – Base package + storage ready + advanced wiring",
            "eps_additional_incentives": "Energy smart homes (upload solar exemption to documents tab)",
            "solar_elements": "Solar PV",
        }

    @property
    def code_values(self):
        return {
            "heating_therms": 402,
            "heating_kwh": 698.0,
            "cooling_kwh": 563.0,
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
            "cooling_kwh": 225,
            "hot_water_therms": 98.0,
            "hot_water_kwh": 0,
            "lights_and_appliances_therms": 36.0,
            "lights_and_appliances_kwh": 7167.0,
            "pv_kwh": 7800.00,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 0.0,
            "electric_cost": 796.0,
            "gas_cost": 339.0,
        }.copy()

    def test_netzero_qualifications(self):
        """Flex out the netzero qualification"""
        kwargs = self.site_data.copy()
        kwargs["code_data"] = self.code_values.copy()
        kwargs["improved_data"] = self.improved_values.copy()

        calculator = EPSCalculator(**kwargs)
        self.assertEqual(calculator.net_zero.qualifies_net_zero, True)

        kwargs["solar_elements"] = "Non-Energy Trust Solar PV"
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(calculator.net_zero.qualifies_net_zero, False)

        kwargs["solar_elements"] = "Solar PV"
        kwargs["improved_data"]["pv_kwh"] = 7500.0
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(calculator.net_zero.qualifies_net_zero, False)

        kwargs["improved_data"]["pv_kwh"] = 1000000.0
        kwargs["improved_data"]["cooling_kwh"] = kwargs["code_data"]["cooling_kwh"]
        kwargs["improved_data"]["heating_kwh"] = kwargs["code_data"]["heating_kwh"]
        kwargs["improved_data"]["heating_therms"] = 0.9 * kwargs["code_data"]["heating_therms"]
        kwh = kwargs["code_data"]["lights_and_appliances_kwh"]
        kwargs["improved_data"]["lights_and_appliances_kwh"] = kwh
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(calculator.net_zero.qualifies_net_zero, False)

    def test_smart_thermostat_requirement(self):
        """Flex out the smart thermostat qualification"""
        kwargs = self.site_data.copy()
        kwargs["code_data"] = self.code_values.copy()
        kwargs["improved_data"] = self.improved_values.copy()

        calculator = EPSCalculator(**kwargs)
        self.assertEqual(calculator.net_zero.smart_thermostat_requirement_met, True)

        kwargs["smart_thermostat_brand"] = "CARRIER COR WIFI MODEL T6-WEM01-A"
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(calculator.net_zero.smart_thermostat_requirement_met, False)

        kwargs["smart_thermostat_brand"] = "nest thermostat e"
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(calculator.net_zero.smart_thermostat_requirement_met, True)

    def test_solar_exempt(self):
        """Flex out the solar exemption qualification"""
        kwargs = self.site_data.copy()
        kwargs["code_data"] = self.code_values.copy()
        kwargs["improved_data"] = self.improved_values.copy()

        calculator = EPSCalculator(**kwargs)
        self.assertEqual(calculator.net_zero.solar_exempt, True)

        kwargs["eps_additional_incentives"] = "Affordable housing and solar elements"
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(calculator.net_zero.solar_exempt, False)

    def test_mini_split_in_use(self):
        """Flex out the mini-split qualification"""
        kwargs = self.site_data.copy()
        kwargs["code_data"] = self.code_values.copy()
        kwargs["improved_data"] = self.improved_values.copy()

        calculator = EPSCalculator(**kwargs)
        self.assertEqual(calculator.net_zero.mini_split_in_use, True)

        kwargs["primary_heating_equipment_type"] = "Gas Furnace"
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(calculator.net_zero.mini_split_in_use, False)

    def test_energy_smart_home_incentive(self):
        """Flex out the ESH incentive"""
        kwargs = self.site_data.copy()
        kwargs["code_data"] = self.code_values.copy()
        kwargs["improved_data"] = self.improved_values.copy()

        from ...enumerations import GridHarmonization2020

        kwargs["grid_harmonization_elements"] = GridHarmonization2020.ALL.value
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(round(calculator.net_zero.energy_smart_home_incentive, 2), 350.0)

        kwargs["grid_harmonization_elements"] = GridHarmonization2020.WIRING.value
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(round(calculator.net_zero.energy_smart_home_incentive, 2), 350.0)

        kwargs["grid_harmonization_elements"] = GridHarmonization2020.STORAGE.value
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(round(calculator.net_zero.energy_smart_home_incentive, 2), 200.0)

        kwargs["grid_harmonization_elements"] = GridHarmonization2020.BASE.value
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(round(calculator.net_zero.energy_smart_home_incentive, 2), 200.0)

        kwargs["grid_harmonization_elements"] = None
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(round(calculator.net_zero.energy_smart_home_incentive, 2), 0.0)

    def test_net_zero_incentive(self):
        """Flex out the Net Zero incentive"""
        kwargs = self.site_data.copy()
        kwargs["code_data"] = self.code_values.copy()
        kwargs["improved_data"] = self.improved_values.copy()

        calculator = EPSCalculator(**kwargs)
        self.assertEqual(round(calculator.net_zero.net_zero_incentive, 2), 750.0)

        kwargs["improved_data"]["pv_kwh"] = 0.0
        calculator = EPSCalculator(**kwargs)
        self.assertEqual(round(calculator.net_zero.net_zero_incentive, 2), 0.0)

    def test_incentive(self):
        """Flex out the incentive passes to the builder"""
        kwargs = self.site_data.copy()
        kwargs["code_data"] = self.code_values.copy()
        kwargs["improved_data"] = self.improved_values.copy()

        calculator = EPSCalculator(**kwargs)
        # print(calculator.incentives.net_zero_report())
        self.assertEqual(round(calculator.net_zero.net_zero_incentive, 2), 750.0)
        self.assertEqual(round(calculator.net_zero.energy_smart_home_incentive, 2), 350.0)

        base = calculator.total_builder_incentive
        self.assertEqual(round(base, 2), 4068.0)
        # self.dump_net_zero_data(calculator)

        # Net Zero data
        self.assertEqual(calculator.net_zero.qualifies_net_zero, True)
        self.assertEqual(calculator.net_zero.electric_utility, "pacific power")
        self.assertEqual(round(calculator.net_zero.improved_total_therms, 2), 451.5)
        self.assertEqual(round(calculator.net_zero.therms_pct_improvement, 2), 0.35)
        self.assertEqual(round(calculator.net_zero.percentage_improvement, 2), 0.29)
        self.assertEqual(round(calculator.net_zero.pv_kwh_unadjusted, 2), 7800.0)
        self.assertEqual(round(calculator.net_zero.improved_total_kwh, 2), 7731.0)
        self.assertEqual(calculator.net_zero.smart_thermostat_requirement_met, True)
        self.assertEqual(calculator.net_zero.solar_exempt, True)
        self.assertEqual(calculator.net_zero.mini_split_in_use, True)
        value = calculator.net_zero.incentive
        self.assertEqual(round(value, 2), 1100.0)
        value = calculator.net_zero.net_zero_incentive
        self.assertEqual(round(value, 2), 750.0)
        value = calculator.net_zero.energy_smart_home_incentive
        self.assertEqual(round(value, 2), 350.0)
        value = calculator.net_zero.base_package_energy_smart_incentive
        self.assertEqual(round(value, 2), 200.0)
        value = calculator.net_zero.storage_ready_energy_smart_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.net_zero.storage_ready_energy_smart_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.mad_max_incentive
        self.assertEqual(round(value, 2), 3452.7)
        value = calculator.incentives.net_zero_eps_allocation
        self.assertEqual(round(value, 2), 484.67)
        value = calculator.incentives.net_zero_solar_allocation
        self.assertEqual(round(value, 2), 615.33)
        value = calculator.incentives.net_zero_eps_incentive
        self.assertEqual(round(value, 2), 330.45)
        value = calculator.incentives.energy_smart_homes_eps_incentive
        self.assertEqual(round(value, 2), 154.21)
        value = calculator.incentives.net_zero_solar_incentive
        self.assertEqual(round(value, 2), 419.55)
        value = calculator.incentives.energy_smart_homes_solar_incentive
        self.assertEqual(round(value, 2), 195.79)

        kwargs["improved_data"]["pv_kwh"] = 0.0
        kwargs["grid_harmonization_elements"] = None
        calculator = EPSCalculator(**kwargs)

        # self.dump_net_zero_data(calculator)
        # Net Zero data
        self.assertEqual(calculator.net_zero.qualifies_net_zero, False)
        self.assertEqual(calculator.net_zero.electric_utility, "pacific power")
        self.assertEqual(round(calculator.net_zero.improved_total_therms, 2), 451.5)
        self.assertEqual(round(calculator.net_zero.therms_pct_improvement, 2), 0.35)
        self.assertEqual(round(calculator.net_zero.percentage_improvement, 2), 0.29)
        self.assertEqual(round(calculator.net_zero.pv_kwh_unadjusted, 2), 1200.0)
        self.assertEqual(round(calculator.net_zero.improved_total_kwh, 2), 7731.0)
        self.assertEqual(calculator.net_zero.smart_thermostat_requirement_met, True)
        self.assertEqual(calculator.net_zero.solar_exempt, True)
        self.assertEqual(calculator.net_zero.mini_split_in_use, True)
        value = calculator.net_zero.incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.net_zero.net_zero_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.net_zero.energy_smart_home_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.net_zero.base_package_energy_smart_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.net_zero.storage_ready_energy_smart_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.net_zero.storage_ready_energy_smart_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.mad_max_incentive
        self.assertEqual(round(value, 2), 3452.7)
        value = calculator.incentives.net_zero_eps_allocation
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.net_zero_solar_allocation
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.net_zero_eps_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.energy_smart_homes_eps_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.net_zero_solar_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.energy_smart_homes_solar_incentive
        self.assertEqual(round(value, 2), 0.0)

    def test_original_data(self):
        kwargs = {
            "site_address": "Some really cool place",
            "location": "portland",
            "us_state": "OR",
            "primary_heating_equipment_type": "Gas Furnace",
            "pathway": "pct",
            "conditioned_area": 1927.0,
            "electric_utility": "pacific power",
            "program": "eto-2020",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.82,
            "has_tankless_water_heater": True,
            "has_solar_hot_water": False,
            "has_ashp": False,
            "smart_thermostat_brand": "Ecobee4",
            "has_heat_pump_water_heater": False,
            "gas_furnace_afue": 92.0,
            "generated_solar_pv_kwh": 10000.00,
            "grid_harmonization_elements": "Energy smart homes \u2013 Base package + storage ready + advanced wiring",
            "eps_additional_incentives": "No",
            "solar_elements": "Solar PV",
            "code_data": {
                "heating_therms": 800.0,
                "heating_kwh": 812.0,
                "cooling_kwh": 300.0,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 500.0,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 8698.0,
                "electric_cost": 823.0,
                "gas_cost": 0.0,
            },
            "improved_data": {
                "heating_therms": 500.0,
                "heating_kwh": 309.0,
                "cooling_kwh": 300.0,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 200.0,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 8342.0,
                "solar_hot_water_therms": 0.0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 729.0,
                "gas_cost": 0.0,
            },
        }
        calculator = EPSCalculator(**kwargs)
        # print(calculator.report())
        # print(calculator.code_data.report())
        # print(calculator.improved_data.report(show_header=False))
        # print(calculator.code_calculations.report())
        # print(calculator.improved_calculations.report())
        # print(calculator.calculations_report())
        # print(calculator.incentives.report())
        # print(calculator.projected.report())
        # print(calculator.incentives.net_zero_report())
        # print(calculator.output())
        #
        # self.dump_output(calculator)

        # Code Calculation Validations (For EPS)
        value = calculator.code_calculations.eps_gas_heat_total_therms
        self.assertEqual(round(value, 3), 800.0)
        value = calculator.code_calculations.eps_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 10525.0)
        value = calculator.code_calculations.eps_heat_pump_total_therms
        self.assertEqual(round(value, 3), 800.0)
        value = calculator.code_calculations.eps_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 12384.48)
        # Code Calculation Validations (For Carbon)
        value = calculator.code_calculations.carbon_gas_heat_total_therms
        self.assertEqual(round(value, 3), 4.68)
        value = calculator.code_calculations.carbon_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 5.619)
        value = calculator.code_calculations.carbon_heat_pump_total_therms
        self.assertEqual(round(value, 3), 4.68)
        value = calculator.code_calculations.carbon_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 5.619)
        # Code Calculation Validations (Consumption Totals)
        value = calculator.code_calculations.consumption_gas_heat_total_therms
        self.assertEqual(round(value, 3), 800.0)
        value = calculator.code_calculations.consumption_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 10310.0)
        value = calculator.code_calculations.consumption_heat_pump_total_therms
        self.assertEqual(round(value, 3), 800.0)
        value = calculator.code_calculations.consumption_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 10310.0)
        value = calculator.code_total_mbtu
        self.assertEqual(round(value, 3), 115.178)

        # Improved Calculation Validations (For EPS)
        value = calculator.improved_calculations.eps_gas_heat_total_therms
        self.assertEqual(round(value, 3), 470.0)
        value = calculator.improved_calculations.eps_gas_heat_total_kwh
        self.assertEqual(round(value, 3), -885.54)
        value = calculator.improved_calculations.eps_heat_pump_total_therms
        self.assertEqual(round(value, 3), 500.0)
        value = calculator.improved_calculations.eps_heat_pump_total_kwh
        self.assertEqual(round(value, 3), -867.0)
        # Improved Calculation Validations (For Carbon)
        value = calculator.improved_calculations.carbon_gas_heat_total_therms
        self.assertEqual(round(value, 3), 2.749)
        value = calculator.improved_calculations.carbon_gas_heat_total_kwh
        self.assertEqual(round(value, 3), -0.483)
        value = calculator.improved_calculations.carbon_heat_pump_total_therms
        self.assertEqual(round(value, 3), 2.925)
        value = calculator.improved_calculations.carbon_heat_pump_total_kwh
        self.assertEqual(round(value, 3), -0.473)
        # Improved Calculation Validations (Consumption Totals)
        value = calculator.improved_calculations.consumption_gas_heat_total_therms
        self.assertEqual(round(value, 3), 470.0)
        value = calculator.improved_calculations.consumption_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 9114.46)
        value = calculator.improved_calculations.consumption_heat_pump_total_therms
        self.assertEqual(round(value, 3), 500.0)
        value = calculator.improved_calculations.consumption_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 9114.46)
        value = calculator.improved_total_mbtu
        self.assertEqual(round(value, 3), 78.099)

        # Incentive data
        self.assertEqual(calculator.incentives.home_path, "Path 3")
        self.assertEqual(calculator.incentives.home_subtype, "GH+EW")
        self.assertEqual(calculator.incentives.electric_load_profile, "Res Space Conditioning")
        self.assertEqual(calculator.incentives.gas_load_profile, "Res Heating")
        value = calculator.incentives.measure_life
        self.assertEqual(round(value, 2), 33.0)
        value = calculator.incentives.percentage_improvement
        self.assertEqual(round(value, 4), 0.3219)
        value = calculator.incentives.full_territory_builder_incentive
        self.assertEqual(round(value, 2), 3526.22)
        value = calculator.incentives.electric_utility_allocation_pct
        self.assertEqual(round(value, 2), 0.75)
        value = calculator.incentives.gas_utility_allocation_pct
        self.assertEqual(round(value, 2), 0.25)
        value = calculator.incentives.electric_utility_allocation_pct
        self.assertEqual(round(value, 4), 0.7547)
        value = calculator.incentives.gas_utility_allocation_pct
        self.assertEqual(round(value, 4), 0.2453)
        value = calculator.incentives.builder_electric_incentive
        self.assertEqual(round(value, 2), 2661.0)
        value = calculator.incentives.builder_gas_incentive
        self.assertEqual(round(value, 2), 865.0)
        value = calculator.incentives.actual_builder_incentive
        self.assertEqual(round(value, 2), 4776.22)
        value = calculator.total_verifier_incentive
        self.assertEqual(round(value, 2), 974.0)
        value = calculator.incentives.verifier_electric_incentive
        self.assertEqual(round(value, 2), 735.0)
        value = calculator.incentives.verifier_gas_incentive
        self.assertEqual(round(value, 2), 239.0)
        value = calculator.incentives.actual_verifier_incentive
        self.assertEqual(round(value, 2), 974.23)

        # EPS Final Results
        self.assertEqual(round(calculator.eps_score, 0), 44.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 116.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.32)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 4776.0)
        self.assertEqual(round(calculator.carbon_score, 2), 2.27)
        self.assertEqual(round(calculator.code_carbon_score, 2), 10.3)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 729.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 60.75)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 103.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 9.25)

        # Net Zero data
        self.assertEqual(calculator.net_zero.qualifies_net_zero, True)
        self.assertEqual(calculator.net_zero.electric_utility, "pacific power")
        self.assertEqual(round(calculator.net_zero.improved_total_therms, 2), 470.0)
        self.assertEqual(round(calculator.net_zero.therms_pct_improvement, 2), 0.41)
        self.assertEqual(round(calculator.net_zero.percentage_improvement, 2), 0.32)
        self.assertEqual(round(calculator.net_zero.pv_kwh_unadjusted, 2), 10000.0)
        self.assertEqual(round(calculator.net_zero.improved_total_kwh, 2), 9114.46)
        self.assertEqual(calculator.net_zero.smart_thermostat_requirement_met, True)
        self.assertEqual(calculator.net_zero.solar_exempt, False)
        self.assertEqual(calculator.net_zero.mini_split_in_use, False)
        value = calculator.net_zero.incentive
        self.assertEqual(round(value, 2), 1250.0)
        value = calculator.net_zero.net_zero_incentive
        self.assertEqual(round(value, 2), 750.0)
        value = calculator.net_zero.energy_smart_home_incentive
        self.assertEqual(round(value, 2), 500.0)
        value = calculator.net_zero.base_package_energy_smart_incentive
        self.assertEqual(round(value, 2), 200.0)
        value = calculator.net_zero.storage_ready_energy_smart_incentive
        self.assertEqual(round(value, 2), 150.0)
        value = calculator.net_zero.storage_ready_energy_smart_incentive
        self.assertEqual(round(value, 2), 150.0)
        value = calculator.incentives.mad_max_incentive
        self.assertEqual(round(value, 2), 4013.83)
        value = calculator.incentives.net_zero_eps_allocation
        self.assertEqual(round(value, 2), 487.61)
        value = calculator.incentives.net_zero_solar_allocation
        self.assertEqual(round(value, 2), 762.39)
        value = calculator.incentives.net_zero_eps_incentive
        self.assertEqual(round(value, 2), 292.57)
        value = calculator.incentives.energy_smart_homes_eps_incentive
        self.assertEqual(round(value, 2), 195.04)
        value = calculator.incentives.net_zero_solar_incentive
        self.assertEqual(round(value, 2), 457.43)
        value = calculator.incentives.energy_smart_homes_solar_incentive
        self.assertEqual(round(value, 2), 304.96)

    def test_thermostat(self):
        kwargs = {
            "site_address": None,
            "location": "portland",
            "us_state": "OR",
            "primary_heating_equipment_type": "Gas Furnace",
            "has_solar_hot_water": False,
            "has_tankless_water_heater": False,
            "has_ashp": 0,
            "gas_utility": "nw natural",
            "electric_utility": "pacific power",
            "program": "eto-2020",
            "conditioned_area": 2200.0,
            "hot_water_ef": 0.62,
            "pathway": "path 1",
            "smart_thermostat_brand": "N/A",
            "generated_solar_pv_kwh": None,
            "has_heat_pump_water_heater": False,
            "gas_furnace_afue": None,
            "grid_harmonization_elements": "Energy smart homes \u2013 Base package + storage ready + advanced wiring",
            "eps_additional_incentives": "Affordable housing, energy smart homes and solar elements",
            "code_data": {
                "heating_therms": 420.561646,
                "heating_kwh": 351.059723,
                "cooling_kwh": 731.038818,
                "hot_water_therms": 166.048569,
                "hot_water_kwh": 0.0,
                "lights_and_appliances_therms": 29.165001,
                "lights_and_appliances_kwh": 5762.953125,
                "electric_cost": 725.331726,
                "gas_cost": 574.974487,
            },
            "improved_data": {
                "heating_therms": 340.451111,
                "heating_kwh": 116.438629,
                "cooling_kwh": 793.201416,
                "hot_water_therms": 155.8741,
                "hot_water_kwh": 0.0,
                "lights_and_appliances_therms": 29.165001,
                "lights_and_appliances_kwh": 5831.544434,
                "pv_kwh": 0.0,
                "solar_hot_water_therms": 0.0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 714.360718,
                "gas_cost": 490.708466,
            },
        }

        calculator = EPSCalculator(**kwargs)
        # print(calculator.report())
        # print(calculator.code_data.report())
        # print(calculator.improved_data.report(show_header=False))
        # print(calculator.code_calculations.report())
        # print(calculator.improved_calculations.report())
        # print(calculator.calculations_report())
        # print(calculator.incentives.report())
        # print(calculator.projected.report())
        # print(calculator.incentives.net_zero_report())
        # print(self.dump_net_zero_data(calculator))

        self.assertEqual(calculator.net_zero.qualifies_net_zero, False)
        self.assertEqual(calculator.net_zero.electric_utility, "pacific power")
        self.assertEqual(round(calculator.net_zero.improved_total_therms, 2), 525.49)
        self.assertEqual(round(calculator.net_zero.therms_pct_improvement, 2), 0.15)
        self.assertEqual(round(calculator.net_zero.percentage_improvement, 2), 0.11)
        self.assertEqual(round(calculator.net_zero.pv_kwh_unadjusted, 2), 0.0)
        self.assertEqual(round(calculator.net_zero.improved_total_kwh, 2), 6741.18)
        self.assertEqual(calculator.net_zero.smart_thermostat_requirement_met, False)
        self.assertEqual(calculator.net_zero.solar_exempt, False)
        self.assertEqual(calculator.net_zero.mini_split_in_use, False)
        value = calculator.net_zero.incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.net_zero.net_zero_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.net_zero.energy_smart_home_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.mad_max_incentive
        self.assertEqual(round(value, 2), 1725.41)
        value = calculator.incentives.net_zero_eps_allocation
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.net_zero_solar_allocation
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.net_zero_eps_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.energy_smart_homes_eps_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.net_zero_solar_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.energy_smart_homes_solar_incentive
        self.assertEqual(round(value, 2), 0.0)

    def test_esh(self):
        """Test ESH Stuff.."""
        kwargs = {
            "site_address": None,
            "location": "medford",
            "us_state": "OR",
            "primary_heating_equipment_type": "Electric Heat Pump \u2013 Air Source Ducted",
            "has_solar_hot_water": False,
            "has_tankless_water_heater": True,
            "has_ashp": 1,
            "gas_utility": "nw natural",
            "electric_utility": "portland general",
            "program": "eto-2020",
            "conditioned_area": 2514.0,
            "hot_water_ef": 0.97,
            "pathway": "path 1",
            "smart_thermostat_brand": "NEST Learning Thermostat",
            "generated_solar_pv_kwh": None,
            "has_heat_pump_water_heater": False,
            "gas_furnace_afue": None,
            "grid_harmonization_elements": "Energy smart homes \u2013 Base package + storage ready + advanced wiring",
            "eps_additional_incentives": "Energy smart homes (upload solar exemption to documents tab)",
            "code_data": {
                "heating_therms": 0.0,
                "heating_kwh": 4716.914063,
                "cooling_kwh": 1134.064819,
                "hot_water_therms": 188.406967,
                "hot_water_kwh": 0.0,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 6049.068359,
                "electric_cost": 1308.860474,
                "gas_cost": 161.671967,
            },
            "improved_data": {
                "heating_therms": 0.0,
                "heating_kwh": 4660.273926,
                "cooling_kwh": 1226.440796,
                "hot_water_therms": 100.021973,
                "hot_water_kwh": 0.0,
                "lights_and_appliances_therms": 0.0,
                "lights_and_appliances_kwh": 6049.068848,
                "pv_kwh": 0.0,
                "solar_hot_water_therms": 0.0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 1311.83728,
                "gas_cost": 85.828865,
            },
        }

        calculator = EPSCalculator(**kwargs)
        # print(calculator.report())
        # print(calculator.incentives.net_zero_report())
        # print(self.dump_net_zero_data(calculator))

        # Net Zero data
        self.assertEqual(calculator.net_zero.qualifies_net_zero, False)
        self.assertEqual(calculator.net_zero.electric_utility, "portland general")
        self.assertEqual(round(calculator.net_zero.improved_total_therms, 2), 100.02)
        self.assertEqual(round(calculator.net_zero.therms_pct_improvement, 2), 0.47)
        self.assertEqual(round(calculator.net_zero.percentage_improvement, 2), 0.18)
        self.assertEqual(round(calculator.net_zero.pv_kwh_unadjusted, 2), 0.0)
        self.assertEqual(round(calculator.net_zero.improved_total_kwh, 2), 11302.96)
        self.assertEqual(calculator.net_zero.smart_thermostat_requirement_met, True)
        self.assertEqual(calculator.net_zero.solar_exempt, True)
        self.assertEqual(calculator.net_zero.mini_split_in_use, False)
        value = calculator.net_zero.incentive
        self.assertEqual(round(value, 2), 350.0)
        value = calculator.net_zero.net_zero_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.net_zero.energy_smart_home_incentive
        self.assertEqual(round(value, 2), 350.0)
        value = calculator.net_zero.base_package_energy_smart_incentive
        self.assertEqual(round(value, 2), 200.0)
        value = calculator.net_zero.storage_ready_energy_smart_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.net_zero.storage_ready_energy_smart_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.mad_max_incentive
        self.assertEqual(round(value, 2), 2690.18)
        value = calculator.incentives.net_zero_eps_allocation
        self.assertEqual(round(value, 2), 350.0)
        value = calculator.incentives.net_zero_solar_allocation
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.net_zero_eps_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.energy_smart_homes_eps_incentive
        self.assertEqual(round(value, 2), 350.0)
        value = calculator.incentives.net_zero_solar_incentive
        self.assertEqual(round(value, 2), 0.0)
        value = calculator.incentives.energy_smart_homes_solar_incentive
        self.assertEqual(round(value, 2), 0.0)

    def test_dr_horton(self):
        kwargs = {
            "site_address": None,
            "location": "redmond",
            "us_state": "OR",
            "primary_heating_equipment_type": "Gas Furnace",
            "pathway": "path 1",
            "conditioned_area": 1935.0,
            "program": "eto-2020",
            "electric_utility": "pacific power",
            "gas_utility": "cascade",
            "builder": "dr-horton-portland",
            "hot_water_ef": 2.9,
            "has_tankless_water_heater": False,
            "has_solar_hot_water": False,
            "has_ashp": 0,
            "smart_thermostat_brand": "N/A",
            "generated_solar_pv_kwh": None,
            "has_heat_pump_water_heater": True,
            "gas_furnace_afue": None,
            "grid_harmonization_elements": "",
            "eps_additional_incentives": "No",
            "has_gas_fireplace": "50-59FE",
            "code_data": {
                "heating_therms": 378.621979,
                "heating_kwh": 403.489624,
                "cooling_kwh": 0.0,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 3525.321289,
                "lights_and_appliances_therms": 33.400002,
                "lights_and_appliances_kwh": 5422.372559,
                "electric_cost": 880.258179,
                "gas_cost": 318.281219,
            },
            "improved_data": {
                "heating_therms": 333.42218,
                "heating_kwh": 211.914474,
                "cooling_kwh": 0.0,
                "hot_water_therms": 0.0,
                "hot_water_kwh": 1034.038086,
                "lights_and_appliances_therms": 33.400002,
                "lights_and_appliances_kwh": 5420.018555,
                "pv_kwh": 0.0,
                "solar_hot_water_therms": 0.0,
                "solar_hot_water_kwh": 0.0,
                "electric_cost": 627.50531,
                "gas_cost": 283.371033,
            },
        }

        calculator = EPSCalculator(**kwargs)
        # print(calculator.report())
        # print(calculator.code_data.report())
        # print(calculator.improved_data.report(show_header=False))
        # print(calculator.code_calculations.report())
        # print(calculator.improved_calculations.report())
        # print(calculator.calculations_report())
        # print(calculator.incentives.report())
        # print(calculator.projected.report())
        # print(calculator.incentives.net_zero_report())
        # print(self.dump_net_zero_data(calculator))
        # print(self.dump_output(calculator))

        # Code Calculation Validations (For EPS)
        value = calculator.code_calculations.eps_gas_heat_total_therms
        self.assertEqual(round(value, 3), 500.522)
        value = calculator.code_calculations.eps_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 10867.072)
        value = calculator.code_calculations.eps_heat_pump_total_therms
        self.assertEqual(round(value, 3), 500.522)
        value = calculator.code_calculations.eps_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 11791.063)
        # Code Calculation Validations (For Carbon)
        value = calculator.code_calculations.carbon_gas_heat_total_therms
        self.assertEqual(round(value, 3), 2.928)
        value = calculator.code_calculations.carbon_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 5.096)
        value = calculator.code_calculations.carbon_heat_pump_total_therms
        self.assertEqual(round(value, 3), 2.928)
        value = calculator.code_calculations.carbon_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 5.096)
        # Code Calculation Validations (Consumption Totals)
        value = calculator.code_calculations.consumption_gas_heat_total_therms
        self.assertEqual(round(value, 3), 500.522)
        value = calculator.code_calculations.consumption_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 9351.183)
        value = calculator.code_calculations.consumption_heat_pump_total_therms
        self.assertEqual(round(value, 3), 500.522)
        value = calculator.code_calculations.consumption_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 9351.183)
        value = calculator.code_total_mbtu
        self.assertEqual(round(value, 3), 81.958)

        # Improved Calculation Validations (For EPS)
        value = calculator.improved_calculations.eps_gas_heat_total_therms
        self.assertEqual(round(value, 3), 455.322)
        value = calculator.improved_calculations.eps_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 7110.607)
        value = calculator.improved_calculations.eps_heat_pump_total_therms
        self.assertEqual(round(value, 3), 455.322)
        value = calculator.improved_calculations.eps_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 7595.892)
        # Improved Calculation Validations (For Carbon)
        value = calculator.improved_calculations.carbon_gas_heat_total_therms
        self.assertEqual(round(value, 3), 2.664)
        value = calculator.improved_calculations.carbon_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 3.633)
        value = calculator.improved_calculations.carbon_heat_pump_total_therms
        self.assertEqual(round(value, 3), 2.664)
        value = calculator.improved_calculations.carbon_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 3.633)
        # Improved Calculation Validations (Consumption Totals)
        value = calculator.improved_calculations.consumption_gas_heat_total_therms
        self.assertEqual(round(value, 3), 455.322)
        value = calculator.improved_calculations.consumption_gas_heat_total_kwh
        self.assertEqual(round(value, 3), 6665.971)
        value = calculator.improved_calculations.consumption_heat_pump_total_therms
        self.assertEqual(round(value, 3), 455.322)
        value = calculator.improved_calculations.consumption_heat_pump_total_kwh
        self.assertEqual(round(value, 3), 6665.971)
        value = calculator.improved_total_mbtu
        self.assertEqual(round(value, 3), 68.277)

        # Incentive data
        self.assertEqual(calculator.incentives.home_path, "Path 1")
        self.assertEqual(calculator.incentives.home_subtype, "GH+EW")
        self.assertEqual(calculator.incentives.electric_load_profile, "Res Space Conditioning")
        self.assertEqual(calculator.incentives.gas_load_profile, "Res Heating")
        value = calculator.incentives.measure_life
        self.assertEqual(round(value, 2), 35.0)
        value = calculator.incentives.percentage_improvement
        self.assertEqual(round(value, 4), 0.1662)
        value = calculator.incentives.full_territory_builder_incentive
        self.assertEqual(round(value, 2), 1465.3)
        value = calculator.incentives.electric_utility_allocation_pct
        self.assertEqual(round(value, 2), 0.67)
        value = calculator.incentives.gas_utility_allocation_pct
        self.assertEqual(round(value, 2), 0.33)
        value = calculator.incentives.electric_utility_allocation_pct
        self.assertEqual(round(value, 4), 0.6682)
        value = calculator.incentives.gas_utility_allocation_pct
        self.assertEqual(round(value, 4), 0.3318)
        value = calculator.incentives.builder_electric_incentive
        self.assertEqual(round(value, 2), 729.0)
        value = calculator.incentives.builder_gas_incentive
        self.assertEqual(round(value, 2), 486.0)
        value = calculator.incentives.actual_builder_incentive
        self.assertEqual(round(value, 2), 1215.3)
        value = calculator.total_verifier_incentive
        self.assertEqual(round(value, 2), 300.0)
        value = calculator.incentives.verifier_electric_incentive
        self.assertEqual(round(value, 2), 200.0)
        value = calculator.incentives.verifier_gas_incentive
        self.assertEqual(round(value, 2), 100.0)
        value = calculator.incentives.actual_verifier_incentive
        self.assertEqual(round(value, 2), 300.0)

        # EPS Final Results
        self.assertEqual(round(calculator.eps_score, 0), 70.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 87.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.16)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 1215.0)
        self.assertEqual(round(calculator.carbon_score, 2), 6.3)
        self.assertEqual(round(calculator.code_carbon_score, 2), 8.02)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 910.88)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 75.91)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 107.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 9.3)
