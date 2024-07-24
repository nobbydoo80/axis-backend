"""test_carbon.py - Axis"""

__author__ = "Steven K"
__date__ = "3/16/22 07:57"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from django.test import TestCase

from axis.customer_eto.calculator.eps_2022.carbon import Carbon
from axis.customer_eto.enumerations import ElectricUtility, ClimateLocation, HeatType


class EPS2022CarbonTests(TestCase):
    @property
    def input_options(self):
        return {
            "climate_location": ClimateLocation.REDMOND,
            "heat_type": HeatType.GAS,
            "conditioned_area": 1260,
            "electric_utility": ElectricUtility.NONE,
            "code_total_kwh": 4680,
            "improved_total_kwh": 4518,
            "code_total_therms": 614,
            "improved_total_therms": 416,
        }.copy()

    def test_electric(self):
        opts = self.input_options
        with self.subTest("Electric Other"):
            data = Carbon(**opts)
            self.assertAlmostEqual(data.carbon_score.total, 4.9, 1)
            self.assertIn("4.9", data.report)
            self.assertAlmostEqual(data.code_carbon_score.total, 6.1, 1)
            self.assertIn("6.1", data.report)
            self.assertAlmostEqual(data.similar_size_carbon_score.total, 3.6, 1)
            self.assertIn("3.6", data.report)

        with self.subTest("Electric Pacific"):
            opts["electric_utility"] = ElectricUtility.PACIFIC_POWER
            data = Carbon(**opts)
            self.assertAlmostEqual(data.carbon_score.total, 4.9, 1)
            self.assertIn("4.9", data.report)
            self.assertAlmostEqual(data.code_carbon_score.total, 6.1, 1)
            self.assertIn("6.1", data.report)
            self.assertAlmostEqual(data.similar_size_carbon_score.total, 6.9, 1)
            self.assertIn("6.9", data.report)

        with self.subTest("Electric Portland"):
            opts["electric_utility"] = ElectricUtility.PORTLAND_GENERAL
            data = Carbon(**opts)
            self.assertAlmostEqual(data.carbon_score.total, 4.9, 1)
            self.assertIn("4.9", data.report)
            self.assertAlmostEqual(data.code_carbon_score.total, 6.1, 1)
            self.assertIn("6.1", data.report)
            self.assertAlmostEqual(data.similar_size_carbon_score.total, 6.9, 1)
            self.assertIn("6.9", data.report)

    def test_energy_consumption(self):
        opts = self.input_options
        with self.subTest("Redmond GAS"):
            opts["climate_location"] = ClimateLocation.REDMOND
            opts["heat_type"] = HeatType.GAS
            data = Carbon(**opts)
            self.assertAlmostEqual(data.energy_consumption.gas_home_kwh, 6542.4, 1)
            self.assertAlmostEqual(data.energy_consumption.electric_home_kwh, 0.0, 1)
            self.assertAlmostEqual(data.energy_consumption.gas_home_therms, 570.0, 1)

        with self.subTest("Redmond ELECTRIC"):
            opts["climate_location"] = ClimateLocation.REDMOND
            opts["heat_type"] = HeatType.ELECTRIC
            data = Carbon(**opts)
            self.assertAlmostEqual(data.energy_consumption.gas_home_kwh, 0.0, 1)
            self.assertAlmostEqual(data.energy_consumption.electric_home_kwh, 16845.0, 1)
            self.assertAlmostEqual(data.energy_consumption.gas_home_therms, 0.0, 1)

        with self.subTest("MEDFORD Gas"):
            opts["climate_location"] = ClimateLocation.MEDFORD
            opts["heat_type"] = HeatType.GAS
            data = Carbon(**opts)
            self.assertAlmostEqual(data.energy_consumption.gas_home_kwh, 7711.4, 1)
            self.assertAlmostEqual(data.energy_consumption.electric_home_kwh, 0.0, 1)
            self.assertAlmostEqual(data.energy_consumption.gas_home_therms, 560.8, 1)

        with self.subTest("MEDFORD Electric"):
            opts["climate_location"] = ClimateLocation.MEDFORD
            opts["heat_type"] = HeatType.ELECTRIC
            data = Carbon(**opts)
            self.assertAlmostEqual(data.energy_consumption.gas_home_kwh, 0.0, 1)
            self.assertAlmostEqual(data.energy_consumption.electric_home_kwh, 17541.8, 1)
            self.assertAlmostEqual(data.energy_consumption.gas_home_therms, 0.0, 1)

        with self.subTest("Portland Gas"):
            opts["climate_location"] = ClimateLocation.PORTLAND
            opts["heat_type"] = HeatType.GAS
            data = Carbon(**opts)
            self.assertAlmostEqual(data.energy_consumption.gas_home_kwh, 7711.4, 1)
            self.assertAlmostEqual(data.energy_consumption.electric_home_kwh, 0.0, 1)
            self.assertAlmostEqual(data.energy_consumption.gas_home_therms, 560.8, 1)

        with self.subTest("Portland Electric"):
            opts["climate_location"] = ClimateLocation.PORTLAND
            opts["heat_type"] = HeatType.ELECTRIC
            data = Carbon(**opts)
            self.assertAlmostEqual(data.energy_consumption.gas_home_kwh, 0.0, 1)
            self.assertAlmostEqual(data.energy_consumption.electric_home_kwh, 16309.2, 1)
            self.assertAlmostEqual(data.energy_consumption.gas_home_therms, 0.0, 1)

    def test_zeros(self):
        opts = self.input_options
        opts["code_total_kwh"] = 0
        opts["improved_total_kwh"] = 0
        opts["code_total_therms"] = 0
        opts["improved_total_therms"] = 0
        data = Carbon(**opts)
        self.assertIn("Carbon Score               0.0", data.report)
        self.assertIn("Code Carbon Score          0.0", data.report)
