"""test_savings.py - Axis"""

__author__ = "Steven K"
__date__ = "3/4/22 13:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from decimal import Decimal

from django.test import TestCase
from simulation.enumerations import EnergyUnit
from simulation.utils.conversions import convert_kwh_to

from axis.customer_eto.calculator.eps_2022.savings import (
    HeatingCoolingSavings,
    HotWaterSavings,
    LightsAndApplianceSavings,
    FireplaceSavings,
    Savings,
)
from axis.customer_eto.enumerations import QualifyingThermostat, Fireplace2020

log = logging.getLogger(__name__)


class EPS2022CalculatorHeatingCoolingSavingsTests(TestCase):
    @property
    def input_options(self):
        return {
            "code_heating_therms": 23.3,
            "code_heating_kwh": 1501.2,
            "code_cooling_kwh": 2503.6,
            "improved_heating_therms": 18.1,
            "improved_heating_kwh": 1223.3,
            "improved_cooling_kwh": 2356.4,
            "thermostat": QualifyingThermostat.NONE,
        }.copy()

    def test_no_thermostat(self):
        data = HeatingCoolingSavings(**self.input_options)
        self.assertEqual(data.thermostat_heating_adjustment, 0.0)
        self.assertEqual(data.thermostat_cooling_adjustment, 0.0)
        self.assertEqual(data.thermostat_heating_kwh_savings, 0.0)
        self.assertEqual(data.thermostat_heating_therm_savings, 0.0)
        self.assertEqual(data.thermostat_cooling_kwh_savings, 0.0)
        self.assertEqual(
            data.total_heating_kwh_savings,
            self.input_options["code_heating_kwh"] - self.input_options["improved_heating_kwh"],
        )
        self.assertEqual(
            data.total_heating_therm_savings,
            self.input_options["code_heating_therms"]
            - self.input_options["improved_heating_therms"],
        )
        self.assertEqual(
            data.total_cooling_kwh_savings,
            self.input_options["code_cooling_kwh"] - self.input_options["improved_cooling_kwh"],
        )

    def test_gas_thermostat(self):
        opts = self.input_options
        opts["thermostat"] = QualifyingThermostat.DUCTED_FURNACE
        data = HeatingCoolingSavings(**opts)
        self.assertEqual(data.thermostat_heating_adjustment, 0.06)
        self.assertEqual(data.thermostat_cooling_adjustment, 0.06)
        self.assertEqual(data.thermostat_heating_kwh_savings, opts["improved_heating_kwh"] * 0.06)
        self.assertEqual(
            data.thermostat_heating_therm_savings, opts["improved_heating_therms"] * 0.06
        )
        self.assertEqual(data.thermostat_cooling_kwh_savings, opts["improved_cooling_kwh"] * 0.06)
        self.assertEqual(
            data.total_heating_kwh_savings,
            self.input_options["code_heating_kwh"]
            - (self.input_options["improved_heating_kwh"] - opts["improved_heating_kwh"] * 0.06),
        )
        self.assertEqual(
            data.total_heating_therm_savings,
            self.input_options["code_heating_therms"]
            - (
                self.input_options["improved_heating_therms"]
                - opts["improved_heating_therms"] * 0.06
            ),
        )
        self.assertEqual(
            data.total_cooling_kwh_savings,
            self.input_options["code_cooling_kwh"]
            - (self.input_options["improved_cooling_kwh"] - opts["improved_cooling_kwh"] * 0.06),
        )

    def test_electric_thermostat(self):
        opts = self.input_options
        opts["thermostat"] = QualifyingThermostat.DUCTED_ASHP
        data = HeatingCoolingSavings(**opts)
        self.assertEqual(data.thermostat_heating_adjustment, 0.12)
        self.assertEqual(data.thermostat_cooling_adjustment, 0.06)
        self.assertEqual(data.thermostat_heating_kwh_savings, opts["improved_heating_kwh"] * 0.12)
        self.assertEqual(
            data.thermostat_heating_therm_savings, opts["improved_heating_therms"] * 0.12
        )
        self.assertEqual(data.thermostat_cooling_kwh_savings, opts["improved_cooling_kwh"] * 0.06)
        self.assertEqual(
            data.total_heating_kwh_savings,
            self.input_options["code_heating_kwh"]
            - (self.input_options["improved_heating_kwh"] - opts["improved_heating_kwh"] * 0.12),
        )
        self.assertEqual(
            data.total_heating_therm_savings,
            self.input_options["code_heating_therms"]
            - (
                self.input_options["improved_heating_therms"]
                - opts["improved_heating_therms"] * 0.12
            ),
        )
        self.assertEqual(
            data.total_cooling_kwh_savings,
            self.input_options["code_cooling_kwh"]
            - (self.input_options["improved_cooling_kwh"] - opts["improved_cooling_kwh"] * 0.06),
        )


class EPS2022CalculatorHotWaterSavingsTests(TestCase):
    @property
    def input_options(self):
        return {
            "code_hot_water_therms": 23.3,
            "code_hot_water_kwh": 1501.2,
            "improved_hot_water_therms": 18.1,
            "improved_hot_water_kwh": 1223.3,
        }.copy()

    def test_hot_water_savings(self):
        opts = self.input_options
        data = HotWaterSavings(**opts)
        self.assertEqual(
            data.total_hot_water_kwh_savings,
            opts["code_hot_water_kwh"] - opts["improved_hot_water_kwh"],
        )
        self.assertEqual(
            data.total_hot_water_therm_savings,
            opts["code_hot_water_therms"] - opts["improved_hot_water_therms"],
        )


class EPS2022CalculatorLightsAndApplianceSavingsTests(TestCase):
    @property
    def input_options(self):
        return {
            "code_lights_and_appliance_therms": 5.2,
            "code_lights_and_appliance_kwh": 1975.2,
            "improved_lights_and_appliance_therms": 4.8,
            "improved_lights_and_appliance_kwh": 1387.43,
        }.copy()

    def test_hot_water_savings(self):
        opts = self.input_options
        data = LightsAndApplianceSavings(**opts)
        self.assertEqual(
            data.total_lights_and_appliance_kwh_savings,
            opts["code_lights_and_appliance_kwh"] - opts["improved_lights_and_appliance_kwh"],
        )
        self.assertEqual(
            data.total_lights_and_appliance_therm_savings,
            opts["code_lights_and_appliance_therms"] - opts["improved_lights_and_appliance_therms"],
        )


class EPS2022CalculatorFireplaceSavingsTests(TestCase):
    @property
    def input_options(self):
        return {
            "fireplace": Fireplace2020.NONE,
        }.copy()

    def test_no_fireplace(self):
        opts = self.input_options
        data = FireplaceSavings(**opts)
        self.assertEqual(data.total_fireplace_therm_savings, 0.0)

    def test_basic_fireplace(self):
        opts = self.input_options
        opts["fireplace"] = Fireplace2020.FE_60_69
        data = FireplaceSavings(**opts)
        self.assertEqual(data.total_fireplace_therm_savings, 0.0)

    def test_max_savings_fireplace(self):
        opts = self.input_options
        opts["fireplace"] = Fireplace2020.FE_GTE_70
        data = FireplaceSavings(**opts)
        self.assertEqual(data.total_fireplace_therm_savings, 88.5 - 70.2)


class EPS2022CalculatorSavingsTests(TestCase):
    @property
    def input_options(self):
        return {
            "code_heating_therms": 23.3,
            "code_heating_kwh": 1501.2,
            "code_cooling_kwh": 2503.6,
            "code_hot_water_therms": 25.2,
            "code_hot_water_kwh": 1025.2,
            "code_lights_and_appliance_therms": 5.2,
            "code_lights_and_appliance_kwh": 1975.2,
            "improved_heating_therms": 18.1,
            "improved_heating_kwh": 1223.3,
            "improved_cooling_kwh": 2356.4,
            "improved_hot_water_therms": 18.799999999,
            "improved_hot_water_kwh": 967.73,
            "improved_lights_and_appliance_therms": 4.8,
            "improved_lights_and_appliance_kwh": 1387.43,
            "improved_pv_kwh": 0.0,
            "electric_rate": Decimal("0.1245"),
            "gas_rate": Decimal("1.4"),
            "thermostat": QualifyingThermostat.NONE,
            "fireplace": Fireplace2020.NONE,
        }.copy()

    def test_therms(self):
        opts = self.input_options
        opts.update(
            {
                "code_heating_therms": 20,
                "code_heating_kwh": 0,
                "code_cooling_kwh": 0,
                "code_hot_water_therms": 0,
                "code_hot_water_kwh": 0,
                "code_lights_and_appliance_therms": 0,
                "code_lights_and_appliance_kwh": 0,
                "improved_heating_therms": 18,
                "improved_heating_kwh": 0,
                "improved_cooling_kwh": 0,
                "improved_hot_water_therms": 0,
                "improved_hot_water_kwh": 0,
                "improved_lights_and_appliance_therms": 0,
                "improved_lights_and_appliance_kwh": 0,
                "thermostat": QualifyingThermostat.NONE,
                "fireplace": Fireplace2020.NONE,
            }
        )
        with self.subTest("Heating Therms"):
            data = Savings(**opts)
            self.assertEqual(data.therm.baseline, 20.0)
            self.assertEqual(data.therm.proposed, 18.0)
            self.assertEqual(data.therm.savings, 2.0)
            self.assertEqual(data.therm.pct_improvement, 0.10)

            self.assertEqual(data.kwh.baseline, 0.0)
            self.assertEqual(data.kwh.proposed, 0.0)
            self.assertEqual(data.kwh.savings, 0.0)
            self.assertEqual(data.kwh.pct_improvement, 0.0)

            self.assertAlmostEqual(data.mbtu.baseline, 2.0, 2)
            self.assertAlmostEqual(data.mbtu.proposed, 1.8, 2)
            self.assertAlmostEqual(data.mbtu.savings, 0.2, 2)
            self.assertAlmostEqual(data.mbtu.pct_improvement, 0.10, 2)
            self.assertIn("20.0", data.savings_report)
            self.assertIn("18.0", data.savings_report)
            self.assertIn("2.0", data.savings_report)
            self.assertIn("10.0%", data.savings_report)

        with self.subTest("Hot Water Therms"):
            opts.update(
                {
                    "code_heating_therms": 0,
                    "code_heating_kwh": 0,
                    "code_cooling_kwh": 0,
                    "code_hot_water_therms": 20,
                    "code_hot_water_kwh": 0,
                    "code_lights_and_appliance_therms": 0,
                    "code_lights_and_appliance_kwh": 0,
                    "improved_heating_therms": 0,
                    "improved_heating_kwh": 0,
                    "improved_cooling_kwh": 0,
                    "improved_hot_water_therms": 18,
                    "improved_hot_water_kwh": 0,
                    "improved_lights_and_appliance_therms": 0,
                    "improved_lights_and_appliance_kwh": 0,
                }
            )
            data = Savings(**opts)
            self.assertEqual(data.therm.baseline, 20.0)
            self.assertEqual(data.therm.proposed, 18.0)
            self.assertEqual(data.therm.savings, 2.0)
            self.assertEqual(data.therm.pct_improvement, 0.10)

            self.assertEqual(data.kwh.baseline, 0.0)
            self.assertEqual(data.kwh.proposed, 0.0)
            self.assertEqual(data.kwh.savings, 0.0)
            self.assertEqual(data.kwh.pct_improvement, 0.0)

            self.assertAlmostEqual(data.mbtu.baseline, 2.0, 2)
            self.assertAlmostEqual(data.mbtu.proposed, 1.8, 2)
            self.assertAlmostEqual(data.mbtu.savings, 0.2, 2)
            self.assertAlmostEqual(data.mbtu.pct_improvement, 0.10, 2)
            self.assertIn("20.0", data.savings_report)
            self.assertIn("18.0", data.savings_report)
            self.assertIn("2.0", data.savings_report)
            self.assertIn("10.0%", data.savings_report)

        with self.subTest("Lights and Appliance Therms"):
            opts.update(
                {
                    "code_heating_therms": 0,
                    "code_heating_kwh": 0,
                    "code_cooling_kwh": 0,
                    "code_hot_water_therms": 0,
                    "code_hot_water_kwh": 0,
                    "code_lights_and_appliance_therms": 20,
                    "code_lights_and_appliance_kwh": 0,
                    "improved_heating_therms": 0,
                    "improved_heating_kwh": 0,
                    "improved_cooling_kwh": 0,
                    "improved_hot_water_therms": 0,
                    "improved_hot_water_kwh": 0,
                    "improved_lights_and_appliance_therms": 18,
                    "improved_lights_and_appliance_kwh": 0,
                }
            )
            data = Savings(**opts)
            self.assertEqual(data.therm.baseline, 20.0)
            self.assertEqual(data.therm.proposed, 18.0)
            self.assertEqual(data.therm.savings, 2.0)
            self.assertEqual(data.therm.pct_improvement, 0.10)

            self.assertEqual(data.kwh.baseline, 0.0)
            self.assertEqual(data.kwh.proposed, 0.0)
            self.assertEqual(data.kwh.savings, 0.0)
            self.assertEqual(data.kwh.pct_improvement, 0.0)

            self.assertAlmostEqual(data.mbtu.baseline, 2.0, 2)
            self.assertAlmostEqual(data.mbtu.proposed, 1.8, 2)
            self.assertAlmostEqual(data.mbtu.savings, 0.2, 2)
            self.assertAlmostEqual(data.mbtu.pct_improvement, 0.10, 2)
            self.assertIn("20.0", data.savings_report)
            self.assertIn("18.0", data.savings_report)
            self.assertIn("2.0", data.savings_report)
            self.assertIn("10.0%", data.savings_report)

        with self.subTest("Fireplace"):
            opts.update(
                {
                    "code_heating_therms": 0,
                    "code_heating_kwh": 0,
                    "code_cooling_kwh": 0,
                    "code_hot_water_therms": 0,
                    "code_hot_water_kwh": 0,
                    "code_lights_and_appliance_therms": 0,
                    "code_lights_and_appliance_kwh": 0,
                    "improved_heating_therms": 0,
                    "improved_heating_kwh": 0,
                    "improved_cooling_kwh": 0,
                    "improved_hot_water_therms": 0,
                    "improved_hot_water_kwh": 0,
                    "improved_lights_and_appliance_therms": 0,
                    "improved_lights_and_appliance_kwh": 0,
                    "fireplace": Fireplace2020.FE_GTE_70,
                }
            )
            data = Savings(**opts)
            self.assertEqual(data.therm.baseline, 88.5)
            self.assertEqual(data.therm.proposed, 70.2)
            self.assertAlmostEqual(data.therm.savings, 18.3, 2)
            self.assertAlmostEqual(data.therm.pct_improvement, 0.207, 2)

            self.assertEqual(data.kwh.baseline, 0.0)
            self.assertEqual(data.kwh.proposed, 0.0)
            self.assertEqual(data.kwh.savings, 0.0)
            self.assertEqual(data.kwh.pct_improvement, 0.0)

            self.assertAlmostEqual(data.mbtu.baseline, 8.85, 2)
            self.assertAlmostEqual(data.mbtu.proposed, 7.02, 2)
            self.assertAlmostEqual(data.mbtu.savings, 1.83, 2)
            self.assertAlmostEqual(data.mbtu.pct_improvement, 0.207, 2)
            self.assertIn("88.5", data.savings_report)
            self.assertIn("70.2", data.savings_report)
            self.assertIn("18.3", data.savings_report)
            self.assertIn("20.7%", data.savings_report)

    def test_kwh(self):
        opts = self.input_options
        opts.update(
            {
                "code_heating_therms": 0,
                "code_heating_kwh": 20,
                "code_cooling_kwh": 0,
                "code_hot_water_therms": 0,
                "code_hot_water_kwh": 0,
                "code_lights_and_appliance_therms": 0,
                "code_lights_and_appliance_kwh": 0,
                "improved_heating_therms": 0,
                "improved_heating_kwh": 18,
                "improved_cooling_kwh": 0,
                "improved_hot_water_therms": 0,
                "improved_hot_water_kwh": 0,
                "improved_lights_and_appliance_therms": 0,
                "improved_lights_and_appliance_kwh": 0,
                "thermostat": QualifyingThermostat.NONE,
                "fireplace": Fireplace2020.NONE,
            }
        )
        with self.subTest("Heating Kwh"):
            data = Savings(**opts)
            self.assertEqual(data.therm.baseline, 0.0)
            self.assertEqual(data.therm.proposed, 0.0)
            self.assertEqual(data.therm.savings, 0.0)
            self.assertEqual(data.therm.pct_improvement, 0.0)

            self.assertEqual(data.kwh.baseline, 20.0)
            self.assertEqual(data.kwh.proposed, 18.0)
            self.assertEqual(data.kwh.savings, 2.0)
            self.assertEqual(data.kwh.pct_improvement, 0.10)

            self.assertAlmostEqual(data.mbtu.baseline, convert_kwh_to(20, EnergyUnit.MBTU), 2)
            self.assertAlmostEqual(data.mbtu.proposed, convert_kwh_to(18, EnergyUnit.MBTU), 2)
            self.assertAlmostEqual(data.mbtu.savings, convert_kwh_to(2, EnergyUnit.MBTU), 2)
            self.assertAlmostEqual(data.mbtu.pct_improvement, 0.10, 2)
            self.assertIn("20.0", data.savings_report)
            self.assertIn("18.0", data.savings_report)
            self.assertIn("2.0", data.savings_report)
            self.assertIn("10.0%", data.savings_report)

        with self.subTest("Cooling"):
            opts.update(
                {
                    "code_heating_therms": 0,
                    "code_heating_kwh": 0,
                    "code_cooling_kwh": 20,
                    "code_hot_water_therms": 0,
                    "code_hot_water_kwh": 0,
                    "code_lights_and_appliance_therms": 0,
                    "code_lights_and_appliance_kwh": 0,
                    "improved_heating_therms": 0,
                    "improved_heating_kwh": 0,
                    "improved_cooling_kwh": 18,
                    "improved_hot_water_therms": 0,
                    "improved_hot_water_kwh": 0,
                    "improved_lights_and_appliance_therms": 0,
                    "improved_lights_and_appliance_kwh": 0,
                }
            )
            data = Savings(**opts)
            self.assertEqual(data.therm.baseline, 0.0)
            self.assertEqual(data.therm.proposed, 0.0)
            self.assertEqual(data.therm.savings, 0.0)
            self.assertEqual(data.therm.pct_improvement, 0.0)

            self.assertEqual(data.kwh.baseline, 20.0)
            self.assertEqual(data.kwh.proposed, 18.0)
            self.assertEqual(data.kwh.savings, 2.0)
            self.assertEqual(data.kwh.pct_improvement, 0.10)

            self.assertAlmostEqual(data.mbtu.baseline, convert_kwh_to(20, EnergyUnit.MBTU), 2)
            self.assertAlmostEqual(data.mbtu.proposed, convert_kwh_to(18, EnergyUnit.MBTU), 2)
            self.assertAlmostEqual(data.mbtu.savings, convert_kwh_to(2, EnergyUnit.MBTU), 2)
            self.assertAlmostEqual(data.mbtu.pct_improvement, 0.10, 2)
            self.assertIn("20.0", data.savings_report)
            self.assertIn("18.0", data.savings_report)
            self.assertIn("2.0", data.savings_report)
            self.assertIn("10.0%", data.savings_report)

        with self.subTest("Hot Water kwh"):
            opts.update(
                {
                    "code_heating_therms": 0,
                    "code_heating_kwh": 0,
                    "code_cooling_kwh": 0,
                    "code_hot_water_therms": 0,
                    "code_hot_water_kwh": 20,
                    "code_lights_and_appliance_therms": 0,
                    "code_lights_and_appliance_kwh": 0,
                    "improved_heating_therms": 0,
                    "improved_heating_kwh": 0,
                    "improved_cooling_kwh": 0,
                    "improved_hot_water_therms": 0,
                    "improved_hot_water_kwh": 18,
                    "improved_lights_and_appliance_therms": 0,
                    "improved_lights_and_appliance_kwh": 0,
                }
            )
            data = Savings(**opts)
            self.assertEqual(data.therm.baseline, 0.0)
            self.assertEqual(data.therm.proposed, 0.0)
            self.assertEqual(data.therm.savings, 0.0)
            self.assertEqual(data.therm.pct_improvement, 0.0)

            self.assertEqual(data.kwh.baseline, 20.0)
            self.assertEqual(data.kwh.proposed, 18.0)
            self.assertEqual(data.kwh.savings, 2.0)
            self.assertEqual(data.kwh.pct_improvement, 0.10)

            self.assertAlmostEqual(data.mbtu.baseline, convert_kwh_to(20, EnergyUnit.MBTU), 2)
            self.assertAlmostEqual(data.mbtu.proposed, convert_kwh_to(18, EnergyUnit.MBTU), 2)
            self.assertAlmostEqual(data.mbtu.savings, convert_kwh_to(2, EnergyUnit.MBTU), 2)
            self.assertAlmostEqual(data.mbtu.pct_improvement, 0.10, 2)
            self.assertAlmostEqual(data.mbtu.pct_improvement, 0.10, 2)
            self.assertIn("20.0", data.savings_report)
            self.assertIn("18.0", data.savings_report)
            self.assertIn("2.0", data.savings_report)
            self.assertIn("10.0%", data.savings_report)

        with self.subTest("Lights and Appliance kwh"):
            opts.update(
                {
                    "code_heating_therms": 0,
                    "code_heating_kwh": 0,
                    "code_cooling_kwh": 0,
                    "code_hot_water_therms": 0,
                    "code_hot_water_kwh": 0,
                    "code_lights_and_appliance_therms": 0,
                    "code_lights_and_appliance_kwh": 20,
                    "improved_heating_therms": 0,
                    "improved_heating_kwh": 0,
                    "improved_cooling_kwh": 0,
                    "improved_hot_water_therms": 0,
                    "improved_hot_water_kwh": 0,
                    "improved_lights_and_appliance_therms": 0,
                    "improved_lights_and_appliance_kwh": 18,
                }
            )
            data = Savings(**opts)
            self.assertEqual(data.therm.baseline, 0.0)
            self.assertEqual(data.therm.proposed, 0.0)
            self.assertEqual(data.therm.savings, 0.0)
            self.assertEqual(data.therm.pct_improvement, 0.0)

            self.assertEqual(data.kwh.baseline, 20.0)
            self.assertEqual(data.kwh.proposed, 18.0)
            self.assertEqual(data.kwh.savings, 2.0)
            self.assertEqual(data.kwh.pct_improvement, 0.10)

            self.assertAlmostEqual(data.mbtu.baseline, convert_kwh_to(20, EnergyUnit.MBTU), 2)
            self.assertAlmostEqual(data.mbtu.proposed, convert_kwh_to(18, EnergyUnit.MBTU), 2)
            self.assertAlmostEqual(data.mbtu.savings, convert_kwh_to(2, EnergyUnit.MBTU), 2)
            self.assertAlmostEqual(data.mbtu.pct_improvement, 0.10, 2)
            self.assertIn("20.0", data.savings_report)
            self.assertIn("18.0", data.savings_report)
            self.assertIn("2.0", data.savings_report)
            self.assertIn("10.0%", data.savings_report)

    def test_costing(self):
        opts = self.input_options
        with self.subTest("Electric Costing"):
            opts["improved_pv_kwh"] = 1000.0
            data = Savings(**opts)
            self.assertEqual(data.electric_costing.baseline_consumption, data.kwh.baseline)
            self.assertAlmostEqual(data.electric_costing.baseline_consumption, data.kwh.baseline, 2)
            self.assertAlmostEqual(
                data.electric_costing.monthly_baseline_cost,
                (data.kwh.baseline / 12.0) * float(data.electric_rate),
                2,
            )
            self.assertAlmostEqual(
                data.electric_costing.annual_baseline_cost,
                data.kwh.baseline * float(data.electric_rate),
                2,
            )
            self.assertAlmostEqual(
                data.electric_costing.annual_savings_cost,
                data.kwh.savings * float(data.electric_rate),
                2,
            )

            self.assertAlmostEqual(
                data.electric_costing.proposed_consumption, data.kwh.proposed - 1000.00, 2
            )
            self.assertAlmostEqual(
                data.electric_costing.proposed_monthly, (data.kwh.proposed - 1000.00) / 12.0, 2
            )
            self.assertAlmostEqual(
                data.electric_costing.annual_proposed_cost,
                (data.kwh.proposed - 1000.00) * float(data.electric_rate),
                2,
            )
            self.assertIn(f"{data.electric_costing.proposed_consumption:.1f}", data.cost_report)

        with self.subTest("Gas Costing"):
            data = Savings(**opts)
            self.assertEqual(data.gas_costing.baseline_consumption, data.therm.baseline)
            self.assertAlmostEqual(data.gas_costing.baseline_consumption, data.therm.baseline, 2)
            self.assertAlmostEqual(
                data.gas_costing.monthly_baseline_cost,
                (data.therm.baseline / 12.0) * float(data.gas_rate),
                2,
            )
            self.assertAlmostEqual(
                data.gas_costing.annual_baseline_cost,
                data.therm.baseline * float(data.gas_rate),
                2,
            )
            self.assertAlmostEqual(
                data.gas_costing.annual_savings_cost,
                data.therm.savings * float(data.gas_rate),
                2,
            )

            self.assertAlmostEqual(data.gas_costing.proposed_consumption, data.therm.proposed, 2)
            self.assertAlmostEqual(
                data.gas_costing.proposed_monthly, (data.therm.proposed) / 12.0, 2
            )
            self.assertAlmostEqual(
                data.gas_costing.annual_proposed_cost,
                (data.therm.proposed) * float(data.gas_rate),
                2,
            )

            self.assertIn(f"{data.gas_costing.proposed_consumption:.1f}", data.cost_report)
