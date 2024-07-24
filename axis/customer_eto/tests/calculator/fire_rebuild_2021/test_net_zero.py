"""test_net_zero.py - Axis"""

__author__ = "Steven K"
__date__ = "12/2/21 08:09"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from django.test import TestCase

from axis.customer_eto.calculator.eps_2021.base import HomePath
from axis.customer_eto.calculator.eps_2021.constants import Constants
from axis.customer_eto.calculator.eps_fire_2021.net_zero import NetZeroFire2021
from axis.customer_eto.eep_programs.fire_rebuild_2021 import FireResilienceBonus
from axis.customer_eto.enumerations import (
    PNWUSStates,
    ElectricUtility,
    PrimaryHeatingEquipment2020,
    SmartThermostatBrands2020,
    GridHarmonization2020,
    AdditionalIncentives2020,
    SolarElements2020,
    HeatType,
    YesNo,
)

log = logging.getLogger(__name__)


class NetZeroCalculatorTests(TestCase):
    @property
    def input_options(self):
        return {
            "total_kwh": 500.0,
            "total_therms": 25.2,
            "cooling_kwh": 25.1,
            "pv_kwh": 500.01,
            "percent_improvement": 0.343427124844,
            "percent_improvement_therms": 0.343427124844,
            "constants": Constants(ElectricUtility.PACIFIC_POWER, PNWUSStates.OR),
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "primary_heating_class": PrimaryHeatingEquipment2020.GAS_FURNACE,
            "thermostat_brand": SmartThermostatBrands2020.NEST_LEARNING,
            "grid_harmonization_elements": GridHarmonization2020.ALL,
            "eps_additional_incentives": AdditionalIncentives2020.AFFORDABLE_HOUSING,
            "solar_elements": SolarElements2020.SOLAR_PV,
            "us_state": PNWUSStates.OR,
            "heat_type": HeatType.GAS,
            "fire_rebuild_qualification": YesNo.NO,
            "fire_resilience_bonus": FireResilienceBonus.NO,
        }

    def test_qualifies_for_net_zero(self):
        input_data = self.input_options.copy()
        net_zero = NetZeroFire2021(**input_data)
        self.assertTrue(net_zero.qualifies_for_net_zero)
        self.assertEqual(net_zero.net_zero_incentive, 750.00)

        net_zero.whole_home_incentive = 7898.49
        net_zero.home_path = HomePath.PATH_3

        # print(net_zero.input_report)
        # print("--")
        # print(net_zero.incentive_report)
        # print("--")
        # print(net_zero.mad_max_report)
        # print("--")
        # print(net_zero.incentive_allocation_report)
        # print("--")
        # print(net_zero.net_zero_allocation_report)

        with self.subTest("Bad State"):
            input_data = self.input_options.copy()
            input_data.update({"us_state": PNWUSStates.WA})
            net_zero = NetZeroFire2021(**input_data)
            self.assertFalse(net_zero.qualifies_for_net_zero)
            self.assertFalse(net_zero._net_zero_elements["Qualifying State"])
            self.assertTrue(net_zero._net_zero_elements["Valid Utility"])
            self.assertTrue(net_zero._net_zero_elements["Overall % Improvement"])
            self.assertTrue(net_zero._net_zero_elements["Acceptable Therms"])
            self.assertTrue(net_zero._net_zero_elements["PV Generation"])
            self.assertTrue(net_zero._net_zero_elements["Valid Solar Elements"])
            self.assertIn("Qualifying State", net_zero.input_report)
            self.assertEqual(net_zero.net_zero_incentive, 0.00)

    def test_triple_pane_window_incentive(self):
        input_data = self.input_options.copy()
        input_data["whole_home_incentive"] = 7898.49
        input_data["home_path"] = HomePath.PATH_3

        with self.subTest("Triple Pane - No Quals"):
            net_zero = NetZeroFire2021(**input_data)
            self.assertFalse(net_zero.has_triple_pane_windows)
            self.assertEqual(net_zero.triple_pane_window_incentive, 0.0)
            self.assertEqual(net_zero.total_fire_resilience_incentive, 0.0)
            self.assertIn("Fire Rebuild?:               No", net_zero.input_report)
            self.assertIn("Triple Pane Window?:         No", net_zero.input_report)
            self.assertIn("Bonus: Triple Pane Windows        $ 0.00", net_zero.incentive_report)

        with self.subTest("Triple Pane - Qualifies no options"):
            input_data["fire_rebuild_qualification"] = YesNo.YES
            net_zero = NetZeroFire2021(**input_data)
            self.assertFalse(net_zero.has_triple_pane_windows)
            self.assertEqual(net_zero.triple_pane_window_incentive, 0.0)
            self.assertEqual(net_zero.total_fire_resilience_incentive, 0.0)
            self.assertIn("Fire Rebuild?:               Yes", net_zero.input_report)
            self.assertIn("Triple Pane Window?:         No", net_zero.input_report)
            self.assertIn("Bonus: Triple Pane Windows        $ 0.00", net_zero.incentive_report)

        with self.subTest("Triple Pane - Qualifies"):
            input_data["fire_resilience_bonus"] = FireResilienceBonus.TRIPLE_PANE
            net_zero = NetZeroFire2021(**input_data)
            self.assertTrue(net_zero.has_triple_pane_windows)
            self.assertEqual(net_zero.triple_pane_window_incentive, 750.0)
            self.assertEqual(net_zero.total_fire_resilience_incentive, 750.0)
            self.assertIn("Fire Rebuild?:               Yes", net_zero.input_report)
            self.assertIn("Triple Pane Window?:         Yes", net_zero.input_report)
            self.assertIn("Bonus: Triple Pane Windows        $ 750.00", net_zero.incentive_report)

    def test_rigid_insulation_incentive(self):
        input_data = self.input_options.copy()
        input_data["whole_home_incentive"] = 7898.49
        input_data["home_path"] = HomePath.PATH_3

        with self.subTest("Rigid Insulation - No Quals"):
            net_zero = NetZeroFire2021(**input_data)
            self.assertFalse(net_zero.rigid_insulation_incentive)
            self.assertEqual(net_zero.rigid_insulation_incentive, 0.0)
            self.assertEqual(net_zero.total_fire_resilience_incentive, 0.0)
            self.assertIn("Fire Rebuild?:               No", net_zero.input_report)
            self.assertIn("Exterior Rigid Insulation?:  No", net_zero.input_report)
            self.assertIn("Bonus: Exterior Rigid Insulation  $ 0.00", net_zero.incentive_report)

        with self.subTest("Rigid Insulation - Qualifies no options"):
            input_data["fire_rebuild_qualification"] = YesNo.YES
            net_zero = NetZeroFire2021(**input_data)
            self.assertFalse(net_zero.has_rigid_insulation)
            self.assertEqual(net_zero.rigid_insulation_incentive, 0.0)
            self.assertEqual(net_zero.total_fire_resilience_incentive, 0.0)
            self.assertIn("Fire Rebuild?:               Yes", net_zero.input_report)
            self.assertIn("Exterior Rigid Insulation?:  No", net_zero.input_report)
            self.assertIn("Bonus: Exterior Rigid Insulation  $ 0.00", net_zero.incentive_report)

        with self.subTest("Rigid Insulation - Qualifies"):
            input_data["fire_resilience_bonus"] = FireResilienceBonus.RIGID_INSULATION
            net_zero = NetZeroFire2021(**input_data)
            self.assertTrue(net_zero.has_rigid_insulation)
            self.assertEqual(net_zero.rigid_insulation_incentive, 750.0)
            self.assertEqual(net_zero.total_fire_resilience_incentive, 750.0)
            self.assertIn("Fire Rebuild?:               Yes", net_zero.input_report)
            self.assertIn("Exterior Rigid Insulation?:  Yes", net_zero.input_report)
            self.assertIn("Bonus: Exterior Rigid Insulation  $ 750.00", net_zero.incentive_report)

    def test_sealed_attic_incentive(self):
        input_data = self.input_options.copy()
        input_data["whole_home_incentive"] = 7898.49
        input_data["home_path"] = HomePath.PATH_3

        with self.subTest("Rigid Insulation - No Quals"):
            net_zero = NetZeroFire2021(**input_data)
            self.assertFalse(net_zero.has_sealed_attic)
            self.assertEqual(net_zero.sealed_attic_incentive, 0.0)
            self.assertEqual(net_zero.total_fire_resilience_incentive, 0.0)
            self.assertIn("Fire Rebuild?:               No", net_zero.input_report)
            self.assertIn("Sealed Attic?:               No", net_zero.input_report)
            self.assertIn("Bonus: Sealed Attic               $ 0.00", net_zero.incentive_report)

        with self.subTest("Rigid Insulation - Qualifies no options"):
            input_data["fire_rebuild_qualification"] = YesNo.YES
            net_zero = NetZeroFire2021(**input_data)
            self.assertFalse(net_zero.has_sealed_attic)
            self.assertEqual(net_zero.sealed_attic_incentive, 0.0)
            self.assertEqual(net_zero.total_fire_resilience_incentive, 0.0)
            self.assertIn("Fire Rebuild?:               Yes", net_zero.input_report)
            self.assertIn("Sealed Attic?:               No", net_zero.input_report)
            self.assertIn("Bonus: Sealed Attic               $ 0.00", net_zero.incentive_report)

        with self.subTest("Rigid Insulation - Qualifies"):
            input_data["fire_resilience_bonus"] = FireResilienceBonus.SEALED_ATTIC
            net_zero = NetZeroFire2021(**input_data)
            self.assertTrue(net_zero.has_sealed_attic)
            self.assertEqual(net_zero.sealed_attic_incentive, 400.0)
            self.assertEqual(net_zero.total_fire_resilience_incentive, 400.0)
            self.assertIn("Fire Rebuild?:               Yes", net_zero.input_report)
            self.assertIn("Sealed Attic?:               Yes", net_zero.input_report)
            self.assertIn("Bonus: Sealed Attic               $ 400.00", net_zero.incentive_report)

    def test_fire_resilience_combo(self):
        input_data = self.input_options.copy()
        input_data["whole_home_incentive"] = 7898.49
        input_data["home_path"] = HomePath.PATH_3

        with self.subTest("Combo - No Quals"):
            net_zero = NetZeroFire2021(**input_data)
            self.assertFalse(net_zero.has_triple_pane_windows)
            self.assertFalse(net_zero.has_rigid_insulation)
            self.assertFalse(net_zero.has_sealed_attic)
            self.assertEqual(net_zero.triple_pane_window_incentive, 0.0)
            self.assertEqual(net_zero.rigid_insulation_incentive, 0.0)
            self.assertEqual(net_zero.sealed_attic_incentive, 0.0)
            self.assertEqual(net_zero.total_fire_resilience_incentive, 0.0)
            self.assertIn("Fire Rebuild?:               No", net_zero.input_report)
            self.assertIn("Triple Pane Window?:         No", net_zero.input_report)
            self.assertIn("Exterior Rigid Insulation?:  No", net_zero.input_report)
            self.assertIn("Sealed Attic?:               No", net_zero.input_report)
            self.assertIn("Bonus: Triple Pane Windows        $ 0.00", net_zero.incentive_report)
            self.assertIn("Bonus: Exterior Rigid Insulation  $ 0.00", net_zero.incentive_report)
            self.assertIn("Bonus: Sealed Attic               $ 0.00", net_zero.incentive_report)

        with self.subTest("Combo - Qualifies no options"):
            input_data["fire_rebuild_qualification"] = YesNo.YES
            net_zero = NetZeroFire2021(**input_data)
            self.assertFalse(net_zero.has_triple_pane_windows)
            self.assertFalse(net_zero.has_rigid_insulation)
            self.assertFalse(net_zero.has_sealed_attic)
            self.assertEqual(net_zero.triple_pane_window_incentive, 0.0)
            self.assertEqual(net_zero.rigid_insulation_incentive, 0.0)
            self.assertEqual(net_zero.sealed_attic_incentive, 0.0)
            self.assertEqual(net_zero.total_fire_resilience_incentive, 0.0)
            self.assertIn("Fire Rebuild?:               Yes", net_zero.input_report)
            self.assertIn("Triple Pane Window?:         No", net_zero.input_report)
            self.assertIn("Exterior Rigid Insulation?:  No", net_zero.input_report)
            self.assertIn("Sealed Attic?:               No", net_zero.input_report)
            self.assertIn("Bonus: Triple Pane Windows        $ 0.00", net_zero.incentive_report)
            self.assertIn("Bonus: Exterior Rigid Insulation  $ 0.00", net_zero.incentive_report)
            self.assertIn("Bonus: Sealed Attic               $ 0.00", net_zero.incentive_report)

        with self.subTest("Combo - Qualifies"):
            input_data[
                "fire_resilience_bonus"
            ] = FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION_AND_SEALED_ATTIC
            net_zero = NetZeroFire2021(**input_data)
            self.assertTrue(net_zero.has_triple_pane_windows)
            self.assertTrue(net_zero.has_rigid_insulation)
            self.assertTrue(net_zero.has_sealed_attic)
            self.assertEqual(net_zero.triple_pane_window_incentive, 750.0)
            self.assertEqual(net_zero.rigid_insulation_incentive, 750.0)
            self.assertEqual(net_zero.sealed_attic_incentive, 400.0)
            self.assertEqual(net_zero.total_fire_resilience_incentive, 1900.0)
            self.assertIn("Fire Rebuild?:               Yes", net_zero.input_report)
            self.assertIn("Triple Pane Window?:         Yes", net_zero.input_report)
            self.assertIn("Exterior Rigid Insulation?:  Yes", net_zero.input_report)
            self.assertIn("Sealed Attic?:               Yes", net_zero.input_report)
            self.assertIn("Bonus: Triple Pane Windows        $ 750.00", net_zero.incentive_report)
            self.assertIn("Bonus: Exterior Rigid Insulation  $ 750.00", net_zero.incentive_report)
            self.assertIn("Bonus: Sealed Attic               $ 400.00", net_zero.incentive_report)

    def test_mad_max(self):
        input_data = self.input_options.copy()
        net_zero = NetZeroFire2021(**input_data)

        self.assertEqual(net_zero.percent_improvement, input_data["percent_improvement"])

        with self.subTest("Home Path 1"):
            input_data["percent_improvement"] = 0.10
            net_zero = NetZeroFire2021(**input_data)
            net_zero.home_path = HomePath.PATH_1
            self.assertAlmostEqual(net_zero.home_max_incentive, 5074.8)
            self.assertIn("10-19.9%", net_zero.mad_max_report)

        with self.subTest("Home Path 2"):
            input_data["percent_improvement"] = 0.20
            net_zero = NetZeroFire2021(**input_data)
            net_zero.home_path = HomePath.PATH_2
            self.assertAlmostEqual(net_zero.home_max_incentive, 6177.20)
            self.assertIn("20-29.9", net_zero.mad_max_report)

        with self.subTest("Home Path 3"):
            input_data["percent_improvement"] = 0.30
            net_zero = NetZeroFire2021(**input_data)
            net_zero.home_path = HomePath.PATH_3
            self.assertAlmostEqual(net_zero.home_max_incentive, 10198.60)
            self.assertIn("30-34.9%", net_zero.mad_max_report)

        with self.subTest("Home Path 4"):
            input_data["percent_improvement"] = 0.35
            net_zero = NetZeroFire2021(**input_data)
            net_zero.home_path = HomePath.PATH_4
            self.assertAlmostEqual(net_zero.home_max_incentive, 11276.0)
            self.assertIn(">=35", net_zero.mad_max_report)
