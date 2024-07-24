"""__init__.py: Django Calculator Tests"""


import logging

from django.test import TestCase

from axis.core.tests.client import AxisClient
from ...calculator.eps.base import EPSInputException
from axis.customer_eto.calculator.eps.calculator import EPSCalculator
from axis.remrate_data.models import Simulation
from .test_eto_2016 import MIN_ATTRS

__author__ = "Steven K"
__date__ = "12/16/2019 09:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class SWWAEPSCalculatorTests(TestCase):
    """Test out ETO SWWA Calculator parser"""

    client_class = AxisClient
    fixtures = [
        "eto_simulation_data.json",
    ]

    def get_calculator(self, **kwargs):
        kwargs["mode"] = "swwa"
        return EPSCalculator(**kwargs)

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

    def test_inline(self):
        """This is the one test we got from them"""
        kwargs = self.site_data.copy()
        kwargs["code_data"] = self.code_values
        kwargs["improved_data"] = self.improved_values
        calculator = self.get_calculator(**kwargs)
        self.assertEqual(round(calculator.eps_score, 0), 56.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 72.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.24)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.0)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 1.0)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 450.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 450.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 100.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 100.0)
        self.assertEqual(round(calculator.carbon_score, 2), 7.53)
        self.assertEqual(round(calculator.code_carbon_score, 2), 9.17)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 816.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 68.0)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 121.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 16.09)

    def _validate_min_attrs(self, calculator):
        for item in MIN_ATTRS:
            try:
                self.assertGreaterEqual(getattr(calculator, item), 0)
            except AssertionError:
                print(item)
                self.assertGreaterEqual(getattr(calculator, item), 0)

    def test_invalid_location(self):
        for location in ["Medford", "REDmonD"]:
            kwargs = self.site_data.copy()
            kwargs["code_data"] = self.code_values
            kwargs["improved_data"] = self.improved_values
            kwargs["location"] = location
            self.assertRaises(EPSInputException, self.get_calculator, **kwargs)

    def test_invalid_gas_companies(self):
        for company in ["cascade", "other/none"]:
            kwargs = self.site_data.copy()
            kwargs["code_data"] = self.code_values
            kwargs["improved_data"] = self.improved_values
            kwargs["gas_utility"] = company
            calculator = self.get_calculator(**kwargs)
            self.assertEqual(round(calculator.total_builder_incentive, 2), 0.0)
            self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 0.0)
            self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 0.0)
            self.assertEqual(round(calculator.total_verifier_incentive, 2), 0.0)
            self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 0.0)
            self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 0.0)

    def test_invalid_electric_utility(self):
        for item in ["Pacific Power", "Portland General", "Other/None"]:
            kwargs = self.site_data.copy()
            kwargs["code_data"] = self.code_values
            kwargs["improved_data"] = self.improved_values
            kwargs["electric_utility"] = item
            calculator = self.get_calculator(**kwargs)
            self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 0.0)
            self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 0.0)

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
        self.assertRaisesRegex(
            EPSInputException,
            "Input simulation ID 7 is the wrong type 'Standard Building'.  Must be 'UDRH As Is Building'",
            EPSCalculator,
            **kwargs,
        )

        kwargs.update({"simulation_id": 3})
        EPSCalculator(**kwargs)

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

        self.assertEqual(calculator.code_calculations.solar_hot_water_kwh_unadjusted, "N/A")
        self.assertEqual(calculator.code_calculations.solar_hot_water_therms_unadjusted, "N/A")
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

        self.assertEqual(calculator.improved_calculations.solar_hot_water_kwh_unadjusted, 0)
        self.assertEqual(calculator.improved_calculations.solar_hot_water_therms_unadjusted, 0)
        self.assertEqual(calculator.improved_calculations.pv_kwh_unadjusted, 0)

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
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.4)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.0)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 1.0)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 725.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 725.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 100.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 100.0)
        self.assertEqual(round(calculator.carbon_score, 2), 9.37)
        self.assertEqual(round(calculator.code_carbon_score, 2), 11.98)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1068.73)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 89.06)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 112.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 14.9)

    def test_swwa_awards_flat_builder_incentive_for_heat_pump_home(self):
        # Don't actually have to test fancy logic in this one -- the flat incentive is just part of
        # the performance breakdown table, calculated correctly by default.
        kwargs = self.site_data.copy()

        for pathway in ["path 1", "path 2", "path 3", "path 4", "path 5"]:
            kwargs["pathway"] = pathway
            kwargs["heat_type"] = "heat pump"
            kwargs["hot_water_ef"] = 0.671
            kwargs["code_data"] = self.code_values
            kwargs["improved_data"] = self.improved_values

            calculator = self.get_calculator(**kwargs)

            self.assertEqual(round(calculator.total_builder_incentive, 2), 150.0)
            self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 0.0)
            self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 150.0)
            self.assertEqual(round(calculator.total_verifier_incentive, 2), 0.0)
            self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 0.0)
            self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 0.0)

    def test_swwa_awards_no_builder_incentive_for_tankless(self):
        # This removes incenitves on tankless water heaters
        kwargs = self.site_data.copy()
        kwargs["heat_type"] = "heat pump"
        kwargs["hot_water_type"] = "Tankless"
        kwargs["code_data"] = self.code_values
        kwargs["improved_data"] = self.improved_values

        calculator = self.get_calculator(**kwargs)

        self.assertEqual(round(calculator.total_builder_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 0.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 0.0)

    def test_swwa_awards_no_verifier_incentive_for_heat_pump_home(self):
        kwargs = self.site_data.copy()

        for pathway in ["path 1", "path 2", "path 3", "path 4", "path 5"]:
            kwargs["pathway"] = pathway
            kwargs["heat_type"] = "heat pump"
            kwargs["code_data"] = self.code_values
            kwargs["improved_data"] = self.improved_values

            calculator = self.get_calculator(**kwargs)
            self.assertEqual(round(calculator.total_builder_incentive, 2), 0.0)
            self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 0.0)
            self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 0.0)
            self.assertEqual(round(calculator.total_verifier_incentive, 2), 0.0)
            self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 0.0)
            self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 0.0)

    def test_swwa_only_awards_incentive_for_nw_natural_utility(self):
        kwargs = self.site_data.copy()
        kwargs["pathway"] = "path 1"
        kwargs["heat_type"] = "gas heat"
        kwargs["code_data"] = self.code_values
        kwargs["improved_data"] = self.improved_values
        kwargs["gas_utility"] = "Other/None"
        calculator = self.get_calculator(**kwargs)

        self.assertEqual(calculator.total_builder_incentive, 0)

    def test_swwa_lost_builder_incentive_removes_verifier_incentive(self):
        kwargs = self.site_data.copy()
        kwargs["pathway"] = "path 1"
        kwargs["heat_type"] = "gas heat"
        kwargs["code_data"] = self.code_values
        kwargs["improved_data"] = self.improved_values
        kwargs["gas_utility"] = "Other/None"
        calculator = self.get_calculator(**kwargs)

        self.assertEqual(calculator.total_builder_incentive, 0)
        self.assertEqual(calculator.total_verifier_incentive, 0)

    def test_swwa_awards_flat_verifier_incentive(self):
        kwargs = self.site_data.copy()

        for pathway in ["path 1", "path 2", "path 3", "path 4", "path 5"]:
            kwargs["pathway"] = pathway
            kwargs["heat_type"] = "gas heat"
            kwargs["code_data"] = self.code_values
            kwargs["improved_data"] = self.improved_values

            calculator = self.get_calculator(**kwargs)

            self.assertEqual(calculator.pathway, pathway)
            self.assertNotEqual(calculator.total_verifier_incentive, 0)
            self.assertEqual(calculator.total_verifier_incentive, 100)

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
        self.assertEqual(round(calculator.eps_score, 0), 85.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 115.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.32)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.0)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 1.0)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 550.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 550.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 100.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 100.0)
        self.assertEqual(round(calculator.carbon_score, 2), 3.69)
        self.assertEqual(round(calculator.code_carbon_score, 2), 5.27)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 998.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 83.17)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 141.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 6.56)

    def test_voltaics_and_swh(self):
        kwargs = {
            "site_address": "1234 Sample St. City, WA 12345",
            "location": "portland",
            "heat_type": "heat pump",
            "pathway": "pct",
            "conditioned_area": "3227",
            "electric_utility": "portland general",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.64,
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
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.0)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.0)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 0.0)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 0.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 0.0)
        self.assertEqual(round(calculator.carbon_score, 2), 7.02)
        self.assertEqual(round(calculator.code_carbon_score, 2), 12.0)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 1281.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 106.75)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 141.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 12.31)

    def test_swwa_electic_water_heater_bump(self):
        kwargs = {
            "site_address": "1234 Sample St. City, WA 12345",
            "location": "portland",
            "heat_type": "gas heat",
            "pathway": "pct",
            "conditioned_area": "2356",
            "electric_utility": "portland general",
            "gas_utility": "nw natural",
            "hot_water_ef": 0.64,
        }

        code_data = {
            "heating_therms": 425,
            "heating_kwh": 360,
            "cooling_kwh": 809.0,
            "hot_water_therms": 0.0,
            "hot_water_kwh": 2799.0,
            "lights_and_appliances_therms": 31.0,
            "lights_and_appliances_kwh": 6705.0,
            "electric_cost": 0.0,
            "gas_cost": 0.0,
        }

        improved_data = {
            "heating_therms": 280,
            "heating_kwh": 183,
            "cooling_kwh": 744,
            "hot_water_therms": 0,
            "hot_water_kwh": 997,
            "lights_and_appliances_therms": 31,
            "lights_and_appliances_kwh": 6092,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 0,
            "pv_kwh": 0,
            "electric_cost": 0.0,
            "gas_cost": 0,
        }
        # calculator = EPSCalculator(**kwargs)

        kwargs = kwargs.copy()
        kwargs["code_data"] = code_data
        kwargs["improved_data"] = improved_data
        calculator = self.get_calculator(**kwargs)

        self.assertEqual(round(calculator.eps_score, 0), 59.0)
        self.assertEqual(round(calculator.code_eps_score, 0), 85.0)
        self.assertEqual(round(calculator.floored_percentage_improvement, 2), 0.26)
        self.assertEqual(round(calculator.incentives.electric_utility_allocation_pct, 2), 0.0)
        self.assertEqual(round(calculator.incentives.gas_utility_allocation_pct, 2), 1.0)
        self.assertEqual(round(calculator.total_builder_incentive, 2), 450.0)
        self.assertEqual(round(calculator.incentives.builder_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.builder_gas_incentive, 2), 450.0)
        self.assertEqual(round(calculator.total_verifier_incentive, 2), 100.0)
        self.assertEqual(round(calculator.incentives.verifier_electric_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.verifier_gas_incentive, 2), 100.0)
        self.assertEqual(round(calculator.carbon_score, 2), 6.07)
        self.assertEqual(round(calculator.code_carbon_score, 2), 8.32)
        self.assertEqual(round(calculator.estimated_annual_cost, 2), 0.0)
        self.assertEqual(round(calculator.estimated_monthly_cost, 2), 0.0)
        self.assertEqual(round(calculator.projected_size_or_home_eps, 0), 117.0)
        self.assertEqual(round(calculator.projected_size_or_home_carbon, 2), 10.23)
