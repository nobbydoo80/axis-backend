"""test_incentives.py - Axis"""

__author__ = "Steven K"
__date__ = "3/4/22 13:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.test import TestCase

from axis.customer_eto.calculator.eps_2022.incentives import Incentives
from axis.customer_eto.enumerations import ElectricUtility, GasUtility, HeatType

log = logging.getLogger(__name__)


class EPS2022IncentiveTests(TestCase):
    @property
    def input_options(self):
        return {
            "percent_improvement": 0.0,
            "therm_percent_improvement": 0.0,
            "solar_production": 0.0,
            "improved_total_kwh": 0.0,
            "fire_rebuild": False,
            "net_zero": False,
            "solar_ready": False,
            "storage_ready": False,
            "ev_ready": False,
            "corbid_builder": False,
            "has_heat_pump_water_heater": False,
            "triple_pane_windows": False,
            "exterior_rigid_insulation": False,
            "sealed_attic": False,
            "electric_utility": ElectricUtility.NONE,
            "gas_utility": GasUtility.NONE,
            "heat_type": HeatType.GAS,
        }.copy()

    def test_baseline_builder_incentive(self):
        with self.subTest("No incentive value"):
            # Note planning for < .10
            opts = self.input_options
            opts.update({"percent_improvement": 0.099})
            data = Incentives(**opts)
            self.assertAlmostEqual(data.baseline_builder_incentive, 0.0, 2)
        with self.subTest("Min value"):
            # Note planning for < .10
            opts = self.input_options
            opts.update({"percent_improvement": 0.10001})
            data = Incentives(**opts)
            self.assertAlmostEqual(data.baseline_builder_incentive, 1123.05, 2)
        with self.subTest("Max value fire"):
            opts = self.input_options
            opts.update({"percent_improvement": 0.10001, "fire_rebuild": True})
            data = Incentives(**opts)
            self.assertAlmostEqual(data.baseline_builder_incentive, 1123.05 * 2, 2)
        with self.subTest("Max value"):
            opts = self.input_options
            opts.update({"percent_improvement": 0.3501})
            data = Incentives(**opts)
            self.assertAlmostEqual(data.baseline_builder_incentive, 4085, 2)
        with self.subTest("Max value fire"):
            opts = self.input_options
            opts.update({"percent_improvement": 0.3501, "fire_rebuild": True})
            data = Incentives(**opts)
            self.assertAlmostEqual(data.baseline_builder_incentive, 4085 * 2, 2)

    def test_baseline_verifier_incentive(self):
        with self.subTest("No incentive value"):
            opts = self.input_options
            opts.update({"percent_improvement": 0.099})
            data = Incentives(**opts)
            self.assertAlmostEqual(data.baseline_verifier_incentive, 0.0, 2)
        with self.subTest("Min value"):
            # Note planning for < .10
            opts = self.input_options
            opts.update({"percent_improvement": 0.10001})
            data = Incentives(**opts)
            self.assertAlmostEqual(data.baseline_verifier_incentive, 300.0, 2)
        with self.subTest("Max value fire"):
            opts = self.input_options
            opts.update({"percent_improvement": 0.10001, "fire_rebuild": True})
            data = Incentives(**opts)
            self.assertAlmostEqual(data.baseline_verifier_incentive, 300.0, 2)
        with self.subTest("Max value"):
            opts = self.input_options
            opts.update({"percent_improvement": 0.3501})
            data = Incentives(**opts)
            self.assertAlmostEqual(data.baseline_verifier_incentive, 817.00, 2)

    def test_net_zero_builder_incentive(self):
        with self.subTest("Not eligible"):
            opts = self.input_options
            opts.update(
                {
                    "electric_utility": ElectricUtility.PACIFIC_POWER,
                    "net_zero": True,
                    "percent_improvement": 0.201,
                    "therm_percent_improvement": 0.09,
                    "improved_total_kwh": 10.0,
                    "solar_production": 0.949 * 10.0,
                }
            )
            data = Incentives(**opts).net_zero_builder_incentive
            self.assertTrue(data.reported)
            self.assertFalse(data.eligible)
            self.assertEqual(data.incentive, 0.0)
            self.assertEqual(data.budget, "SLE")
            self.assertEqual(data.label, "Net Zero")
        with self.subTest("Eligible"):
            opts = self.input_options
            opts.update(
                {
                    "electric_utility": ElectricUtility.PACIFIC_POWER,
                    "net_zero": True,
                    "percent_improvement": 0.201,
                    "therm_percent_improvement": 0.101,
                    "improved_total_kwh": 10.0,
                    "solar_production": 0.9501 * 10.0,
                }
            )
            data = Incentives(**opts).net_zero_builder_incentive
            self.assertTrue(data.reported)
            self.assertTrue(data.eligible)
            self.assertEqual(data.incentive, 1000.0)

    def test_solar_ready_builder_incentive(self):
        with self.subTest("Not eligible"):
            opts = self.input_options
            opts.update(
                {
                    "electric_utility": ElectricUtility.PACIFIC_POWER,
                    "solar_ready": False,
                }
            )
            data = Incentives(**opts).solar_ready_builder_incentive
            self.assertFalse(data.reported)
            self.assertFalse(data.eligible)
            self.assertEqual(data.incentive, 0.0)
            self.assertEqual(data.budget, "SLE")
            self.assertEqual(data.label, "Solar Ready")
        with self.subTest("Eligible"):
            opts = self.input_options
            opts.update(
                {
                    "electric_utility": ElectricUtility.PACIFIC_POWER,
                    "solar_ready": True,
                    "percent_improvement": 0.10,
                }
            )
            data = Incentives(**opts).solar_ready_builder_incentive
            self.assertTrue(data.reported)
            self.assertTrue(data.eligible)
            self.assertEqual(data.incentive, 200.0)

    def test_solar_ready_verifier_incentive(self):
        with self.subTest("Not eligible"):
            opts = self.input_options
            opts.update(
                {
                    "electric_utility": ElectricUtility.PACIFIC_POWER,
                    "solar_ready": False,
                }
            )
            data = Incentives(**opts).solar_ready_verifier_incentive
            self.assertFalse(data.reported)
            self.assertFalse(data.eligible)
            self.assertEqual(data.incentive, 0.0)
            self.assertEqual(data.budget, "SLE")
            self.assertEqual(data.label, "Solar Ready")
        with self.subTest("Eligible"):
            opts = self.input_options
            opts.update(
                {
                    "electric_utility": ElectricUtility.PACIFIC_POWER,
                    "solar_ready": True,
                    "percent_improvement": 0.10,
                }
            )
            data = Incentives(**opts).solar_ready_verifier_incentive
            self.assertTrue(data.reported)
            self.assertTrue(data.eligible)
            self.assertEqual(data.incentive, 50.0)

    def test_ev_ready_builder_incentive(self):
        with self.subTest("Not eligible"):
            opts = self.input_options
            opts.update({"ev_ready": False})
            data = Incentives(**opts).ev_ready_builder_incentive
            self.assertFalse(data.reported)
            self.assertFalse(data.eligible)
            self.assertEqual(data.incentive, 0.0)
            self.assertEqual(data.budget, "ENH")
            self.assertEqual(data.label, "ESH: EV Ready")
        with self.subTest("Eligible"):
            opts = self.input_options
            opts.update(
                {
                    "ev_ready": True,
                    "electric_utility": ElectricUtility.PACIFIC_POWER,
                    "percent_improvement": 0.10,
                }
            )
            data = Incentives(**opts).ev_ready_builder_incentive
            self.assertTrue(data.reported)
            self.assertTrue(data.eligible)
            self.assertEqual(data.incentive, 200.0)

    def test_solar_storage_builder_incentive(self):
        with self.subTest("Not eligible"):
            opts = self.input_options
            opts.update(
                {
                    "electric_utility": ElectricUtility.NONE,
                    "storage_ready": True,
                    "percent_improvement": 0.10,
                }
            )
            data = Incentives(**opts).solar_storage_builder_incentive
            self.assertTrue(data.reported)
            self.assertFalse(data.eligible)
            self.assertEqual(data.incentive, 0.0)
            self.assertEqual(data.budget, "SLE")
            self.assertEqual(data.label, "ESH: Solar + Storage")
        with self.subTest("Eligible"):
            opts = self.input_options
            opts.update(
                {
                    "electric_utility": ElectricUtility.PACIFIC_POWER,
                    "storage_ready": True,
                    "percent_improvement": 0.10,
                }
            )
            data = Incentives(**opts).solar_storage_builder_incentive
            self.assertTrue(data.reported)
            self.assertTrue(data.eligible)
            self.assertEqual(data.incentive, 200.0)

    def test_corbid_builder_incentive(self):
        with self.subTest("Not eligible"):
            opts = self.input_options
            opts.update({"corbid_builder": False, "percent_improvement": 0.10})
            data = Incentives(**opts).cobid_builder_incentive
            self.assertFalse(data.reported)
            self.assertFalse(data.eligible)
            self.assertEqual(data.incentive, 0.0)
            self.assertEqual(data.budget, "ENH")
            self.assertEqual(data.label, "Builder DEI")
        with self.subTest("Not eligible - pct_improvement"):
            opts = self.input_options
            opts.update({"corbid_builder": True, "percent_improvement": 0.09})
            data = Incentives(**opts).cobid_builder_incentive
            self.assertTrue(data.reported)
            self.assertFalse(data.eligible)
            self.assertEqual(data.incentive, 0.0)
            self.assertEqual(data.budget, "ENH")
            self.assertEqual(data.label, "Builder DEI")
        with self.subTest("Eligible"):
            opts = self.input_options
            opts.update({"corbid_builder": True, "percent_improvement": 0.10})
            data = Incentives(**opts).cobid_builder_incentive
            self.assertTrue(data.reported)
            self.assertTrue(data.eligible)
            self.assertEqual(data.incentive, 500.0)

    def test_corbid_verifier_incentive(self):
        with self.subTest("Not eligible"):
            opts = self.input_options
            opts.update({"corbid_verifier": False, "percent_improvement": 0.10})
            data = Incentives(**opts).cobid_verifier_incentive
            self.assertFalse(data.reported)
            self.assertFalse(data.eligible)
            self.assertEqual(data.incentive, 0.0)
            self.assertEqual(data.budget, "ENH")
            self.assertEqual(data.label, "Verifier DEI")
        with self.subTest("Not eligible"):
            opts = self.input_options
            opts.update({"corbid_verifier": True, "percent_improvement": 0.09})
            data = Incentives(**opts).cobid_verifier_incentive
            self.assertTrue(data.reported)
            self.assertFalse(data.eligible)
            self.assertEqual(data.incentive, 0.0)
            self.assertEqual(data.budget, "ENH")
            self.assertEqual(data.label, "Verifier DEI")
        with self.subTest("Eligible"):
            opts = self.input_options
            opts.update({"corbid_verifier": True, "percent_improvement": 0.10})
            data = Incentives(**opts).cobid_verifier_incentive
            self.assertTrue(data.reported)
            self.assertTrue(data.eligible)
            self.assertEqual(data.incentive, 250.0)

    def test_heat_pump_water_heater_incentive(self):
        with self.subTest("Not eligible"):
            opts = self.input_options
            opts.update({"has_heat_pump_water_heater": False})
            data = Incentives(**opts).heat_pump_water_heater_incentive
            self.assertFalse(data.reported)
            self.assertFalse(data.eligible)
            self.assertEqual(data.incentive, 0.0)
            self.assertEqual(data.budget, "ENH")
            self.assertEqual(data.label, "Heat Pump Water Heater")
        with self.subTest("Eligible"):
            opts = self.input_options
            opts.update(
                {
                    "has_heat_pump_water_heater": True,
                    "electric_utility": ElectricUtility.PACIFIC_POWER,
                    "percent_improvement": 0.10,
                }
            )
            data = Incentives(**opts).heat_pump_water_heater_incentive
            self.assertTrue(data.reported)
            self.assertTrue(data.eligible)
            self.assertEqual(data.incentive, -250.0)

    def test_fire_rebuild_triple_pane_incentive(self):
        with self.subTest("Not eligible"):
            opts = self.input_options
            opts.update(
                {
                    "triple_pane_windows": True,
                    "fire_rebuild": False,
                    "percent_improvement": 0.10,
                }
            )
            data = Incentives(**opts).fire_rebuild_triple_pane_incentive
            self.assertTrue(data.reported)
            self.assertFalse(data.eligible)
            self.assertEqual(data.incentive, 0.0)
            self.assertEqual(data.budget, "ENH")
            self.assertEqual(data.label, " - Triple Pane Windows")
        with self.subTest("Eligible"):
            opts = self.input_options
            opts.update(
                {
                    "triple_pane_windows": True,
                    "fire_rebuild": True,
                    "percent_improvement": 0.10,
                }
            )
            data = Incentives(**opts).fire_rebuild_triple_pane_incentive
            self.assertTrue(data.reported)
            self.assertTrue(data.eligible)
            self.assertEqual(data.incentive, 750.0)

    def test_fire_rebuild_insulation_incentive(self):
        with self.subTest("Not eligible"):
            opts = self.input_options
            opts.update(
                {
                    "exterior_rigid_insulation": True,
                    "fire_rebuild": False,
                    "percent_improvement": 0.10,
                }
            )
            data = Incentives(**opts).fire_rebuild_insulation_incentive
            self.assertTrue(data.reported)
            self.assertFalse(data.eligible)
            self.assertEqual(data.incentive, 0.0)
            self.assertEqual(data.budget, "ENH")
            self.assertEqual(data.label, " - Exterior Rigid Insulation")
        with self.subTest("Eligible"):
            opts = self.input_options
            opts.update(
                {
                    "exterior_rigid_insulation": True,
                    "fire_rebuild": True,
                    "percent_improvement": 0.10,
                }
            )
            data = Incentives(**opts).fire_rebuild_insulation_incentive
            self.assertTrue(data.reported)
            self.assertTrue(data.eligible)
            self.assertEqual(data.incentive, 750.0)

    def test_fire_rebuild_sealed_attic_incentive(self):
        with self.subTest("Not eligible"):
            opts = self.input_options
            opts.update(
                {
                    "sealed_attic": True,
                    "fire_rebuild": False,
                    "percent_improvement": 0.10,
                }
            )
            data = Incentives(**opts).fire_rebuild_sealed_attic_incentive
            self.assertTrue(data.reported)
            self.assertFalse(data.eligible)
            self.assertEqual(data.incentive, 0.0)
            self.assertEqual(data.budget, "ENH")
            self.assertEqual(data.label, " - Sealed Attic")
        with self.subTest("Eligible"):
            opts = self.input_options
            opts.update(
                {
                    "sealed_attic": True,
                    "fire_rebuild": True,
                    "percent_improvement": 0.10,
                }
            )
            data = Incentives(**opts).fire_rebuild_sealed_attic_incentive
            self.assertTrue(data.reported)
            self.assertTrue(data.eligible)
            self.assertEqual(data.incentive, 400.0)

    def test_incentive_reporting(self):
        with self.subTest("Max Incentives"):
            opts = self.input_options
            opts.update(
                {
                    "percent_improvement": 0.38,
                    "therm_percent_improvement": 0.201,
                    "solar_production": 100.0,
                    "improved_total_kwh": 0.9501 * 100.0,
                    "fire_rebuild": True,
                    "net_zero": True,
                    "solar_ready": True,
                    "storage_ready": True,
                    "ev_ready": True,
                    "corbid_builder": True,
                    "corbid_verifier": True,
                    "has_heat_pump_water_heater": False,
                    "triple_pane_windows": True,
                    "exterior_rigid_insulation": True,
                    "sealed_attic": True,
                    "electric_utility": ElectricUtility.PACIFIC_POWER,
                }
            )
            data = Incentives(**opts).incentive_report
            self.assertIn("8,170.00", data)
            self.assertIn("817.00", data)

        with self.subTest("Min Incentives - Ensure additional incentive don't go negative HPWH"):
            opts = self.input_options
            opts.update(
                {
                    "percent_improvement": 0.099,
                    "therm_percent_improvement": 0.1999,
                    "solar_production": 100.0,
                    "improved_total_kwh": 0.9499 * 100.0,
                    "fire_rebuild": False,
                    "net_zero": False,
                    "solar_ready": False,
                    "storage_ready": False,
                    "ev_ready": False,
                    "corbid_builder": False,
                    "corbid_verifier": False,
                    "has_heat_pump_water_heater": True,
                    "triple_pane_windows": False,
                    "exterior_rigid_insulation": False,
                    "sealed_attic": False,
                    "electric_utility": ElectricUtility.PACIFIC_POWER,
                }
            )
            data = Incentives(**opts).incentive_report
            self.assertIn("Builder Performance Incentive   $ 0.00", data)
            self.assertIn("Verifier Performance Incentive  $ 0.00", data)
