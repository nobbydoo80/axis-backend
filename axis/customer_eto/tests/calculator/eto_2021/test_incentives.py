"""test_incentives.py - Axis"""

__author__ = "Steven K"
__date__ = "9/15/21 09:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.test import TestCase

from axis.customer_eto.calculator.eps_2021.base import (
    HomePath,
    HomeSubType,
    ElectricLoadProfile,
    GasLoadProfile,
)
from axis.customer_eto.calculator.eps_2021.constants import Constants
from axis.customer_eto.calculator.eps_2021.incentives import Incentives2021WA, Incentives2020
from axis.customer_eto.enumerations import ElectricUtility, GasUtility, PNWUSStates

log = logging.getLogger(__name__)


class IncentiveTests(TestCase):
    @property
    def input_data(self):
        return {
            "percent_improvement": 0.19202531646272857,
            "heating_therms": 18.1,
            "hot_water_therms": 25.2,
            "hot_water_kwh": 1025.2,
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "gas_utility": GasUtility.NW_NATURAL,
            "constants": Constants(ElectricUtility.PACIFIC_POWER, PNWUSStates.OR),
        }

    def test_full_territory_builder_incentive(self):
        input_data = self.input_data.copy()

        with self.subTest("Too Low % Improvement"):
            input_data.update({"percent_improvement": 0.0999})
            c = Incentives2020(**input_data)
            self.assertEqual(c.full_territory_builder_incentive, 0.0)

        with self.subTest("Min threshold"):
            input_data.update({"percent_improvement": 0.1})
            c = Incentives2020(**input_data)
            self.assertEqual(c.full_territory_builder_incentive, 1123.02)

        with self.subTest("Capped threshold"):
            input_data.update({"percent_improvement": 0.45})
            c = Incentives2020(**input_data)
            self.assertEqual(c.full_territory_builder_incentive, 5223.0)

    def test_home_path(self):
        input_data = self.input_data.copy()

        with self.subTest("Path 1"):
            input_data.update({"percent_improvement": 0.1})
            c = Incentives2020(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_1)

            input_data.update({"percent_improvement": 0.1999})
            c = Incentives2020(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_1)

        with self.subTest("Path 2"):
            input_data.update({"percent_improvement": 0.2})
            c = Incentives2020(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_2)

            input_data.update({"percent_improvement": 0.2999})
            c = Incentives2020(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_2)

        with self.subTest("Path 3"):
            input_data.update({"percent_improvement": 0.3})
            c = Incentives2020(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_3)

            input_data.update({"percent_improvement": 0.3999})
            c = Incentives2020(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_3)

        with self.subTest("Path 4"):
            input_data.update({"percent_improvement": 0.4})
            c = Incentives2020(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_4)

            input_data.update({"percent_improvement": 0.999})
            c = Incentives2020(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_4)

    def test_sub_type(self):
        """Test out the sub type."""
        input_data = self.input_data.copy()
        with self.subTest("GH+GW"):
            input_data.update({"heating_therms": 1.1, "hot_water_therms": 1.1})
            c = Incentives2020(**input_data)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
        with self.subTest("EH+EW"):
            input_data.update({"heating_therms": 0.99, "hot_water_kwh": 1.1})
            c = Incentives2020(**input_data)
            self.assertEqual(c.sub_type, HomeSubType.EHEW)
        with self.subTest("GH+EW"):
            input_data.update(
                {"heating_therms": 1.1, "hot_water_kwh": 1.1, "hot_water_therms": 0.99}
            )
            c = Incentives2020(**input_data)
            self.assertEqual(c.sub_type, HomeSubType.GHEW)
        with self.subTest("EH+GW"):
            input_data.update(
                {"heating_therms": 0.99, "hot_water_kwh": 0.0, "hot_water_therms": 1.1}
            )
            c = Incentives2020(**input_data)
            self.assertEqual(c.sub_type, HomeSubType.EHGW)
        with self.subTest("OTHER"):
            input_data.update(
                {"heating_therms": 0.99, "hot_water_kwh": 0.0, "hot_water_therms": 0.99}
            )
            c = Incentives2020(**input_data)
            self.assertEqual(c.sub_type, HomeSubType.OTHER)

    def test_load_profile(self):
        """We don't test all just a good sample"""
        input_data = self.input_data.copy()
        with self.subTest("Path 1 GH+GW"):
            input_data.update(
                {"percent_improvement": 0.15, "heating_therms": 1.1, "hot_water_therms": 1.1}
            )
            c = Incentives2020(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_1)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
            self.assertEqual(
                c.load_profile.electric_load_profile,
                ElectricLoadProfile.RESIDENTIAL_SPACE_CONDITIONING,
            )
            self.assertEqual(
                c.load_profile.gas_load_profile,
                GasLoadProfile.RESIDENTIAL_HEATING,
            )
            self.assertEqual(
                c.load_profile.weighted_avg_measure_life,
                34.0,
            )
            self.assertEqual(
                c.load_profile.electric_allocation,
                0.3453554216774470000,
            )
            self.assertEqual(
                c.load_profile.gas_allocation,
                0.6546445783225530000,
            )
        with self.subTest("Path 2 GH+EW"):
            input_data.update(
                {
                    "percent_improvement": 0.25,
                    "heating_therms": 1.1,
                    "hot_water_kwh": 1.1,
                    "hot_water_therms": 0.99,
                }
            )
            c = Incentives2020(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_2)
            self.assertEqual(c.sub_type, HomeSubType.GHEW)
            self.assertEqual(
                c.load_profile.electric_load_profile,
                ElectricLoadProfile.RESIDENTIAL_SPACE_CONDITIONING,
            )
            self.assertEqual(
                c.load_profile.gas_load_profile,
                GasLoadProfile.RESIDENTIAL_HEATING,
            )
            self.assertEqual(
                c.load_profile.weighted_avg_measure_life,
                29.0,
            )
            self.assertEqual(
                c.load_profile.electric_allocation,
                0.7560419843980000000,
            )
            self.assertEqual(
                c.load_profile.gas_allocation,
                0.2439580156020000000,
            )

        with self.subTest("Path 3 EH+GW"):
            input_data.update(
                {
                    "percent_improvement": 0.35,
                    "heating_therms": 0.99,
                    "hot_water_kwh": 0.0,
                    "hot_water_therms": 1.1,
                }
            )
            c = Incentives2020(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_3)
            self.assertEqual(c.sub_type, HomeSubType.EHGW)
            self.assertEqual(
                c.load_profile.electric_load_profile,
                ElectricLoadProfile.RESIDENTIAL_ASHP,
            )
            self.assertEqual(
                c.load_profile.gas_load_profile,
                GasLoadProfile.HOT_WATER,
            )
            self.assertEqual(
                c.load_profile.weighted_avg_measure_life,
                39.0,
            )
            self.assertEqual(
                c.load_profile.electric_allocation,
                0.8458957826709290000,
            )
            self.assertEqual(
                c.load_profile.gas_allocation,
                0.1541042173290710000,
            )
        with self.subTest("Path 4 EH+EW"):
            input_data.update(
                {
                    "percent_improvement": 0.401,
                    "heating_therms": 0.99,
                    "hot_water_kwh": 1.1,
                    "hot_water_therms": 0.99,
                }
            )
            c = Incentives2020(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_4)
            self.assertEqual(c.sub_type, HomeSubType.EHEW)
            self.assertEqual(
                c.load_profile.electric_load_profile,
                ElectricLoadProfile.RESIDENTIAL_ASHP,
            )
            self.assertEqual(
                c.load_profile.gas_load_profile,
                GasLoadProfile.NONE,
            )
            self.assertEqual(
                c.load_profile.weighted_avg_measure_life,
                37.0,
            )
            self.assertEqual(c.load_profile.electric_allocation, 1.0)
            self.assertEqual(
                c.load_profile.gas_allocation,
                0.0,
            )

    def test_partial_load_profile(self):
        """We don't test all just a good sample"""
        input_data = self.input_data.copy()
        input_data["electric_utility"] = ElectricUtility.NONE
        with self.subTest("Path 1 EH+EW Partial"):
            input_data.update(
                {
                    "percent_improvement": 0.15,
                    "heating_therms": 0.99,
                    "hot_water_kwh": 1.1,
                    "hot_water_therms": 0.99,
                }
            )
            c = Incentives2020(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_1)
            self.assertEqual(c.sub_type, HomeSubType.EHEW)
            self.assertEqual(
                c.load_profile.electric_load_profile,
                ElectricLoadProfile.RESIDENTIAL_ASHP,
            )
            self.assertEqual(
                c.load_profile.gas_load_profile,
                GasLoadProfile.NONE,
            )
            self.assertEqual(
                c.load_profile.weighted_avg_measure_life,
                43.0,
            )
            self.assertEqual(
                c.load_profile.electric_allocation,
                1.0,
            )
            self.assertEqual(
                c.load_profile.gas_allocation,
                0.0,
            )
        with self.subTest("Path 2 EH+GW Partial"):
            input_data.update(
                {
                    "percent_improvement": 0.25,
                    "heating_therms": 0.9,
                    "hot_water_kwh": 0.1,
                    "hot_water_therms": 1.1,
                }
            )
            c = Incentives2020(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_2)
            self.assertEqual(c.sub_type, HomeSubType.EHGW)
            self.assertEqual(
                c.load_profile.electric_load_profile,
                ElectricLoadProfile.RESIDENTIAL_ASHP,
            )
            self.assertEqual(
                c.load_profile.gas_load_profile,
                GasLoadProfile.HOT_WATER,
            )
            self.assertEqual(
                c.load_profile.weighted_avg_measure_life,
                41.0,
            )
            self.assertEqual(
                c.load_profile.electric_allocation,
                0.83,
            )
            self.assertEqual(
                c.load_profile.gas_allocation,
                0.17,
            )

        input_data["electric_utility"] = ElectricUtility.PACIFIC_POWER
        input_data["gas_utility"] = GasUtility.NONE

        with self.subTest("Path 3 GH+EW Partial"):
            input_data.update(
                {
                    "percent_improvement": 0.35,
                    "heating_therms": 1.1,
                    "hot_water_kwh": 1.1,
                    "hot_water_therms": 0.9,
                }
            )
            c = Incentives2020(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_3)
            self.assertEqual(c.sub_type, HomeSubType.GHEW)
            self.assertEqual(
                c.load_profile.electric_load_profile,
                ElectricLoadProfile.RESIDENTIAL_SPACE_CONDITIONING,
            )
            self.assertEqual(
                c.load_profile.gas_load_profile,
                GasLoadProfile.RESIDENTIAL_HEATING,
            )
            self.assertEqual(
                c.load_profile.weighted_avg_measure_life,
                33.0,
            )
            self.assertEqual(
                c.load_profile.electric_allocation,
                0.45,
            )
            self.assertEqual(
                c.load_profile.gas_allocation,
                0.55,
            )
        with self.subTest("Path 4 GH+GW Partial"):
            input_data.update(
                {
                    "percent_improvement": 0.401,
                    "heating_therms": 1.99,
                    "hot_water_kwh": 0.8,
                    "hot_water_therms": 1.1,
                }
            )
            c = Incentives2020(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_4)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
            self.assertEqual(
                c.load_profile.electric_load_profile,
                ElectricLoadProfile.RESIDENTIAL_SPACE_CONDITIONING,
            )
            self.assertEqual(
                c.load_profile.gas_load_profile,
                GasLoadProfile.RESIDENTIAL_HEATING,
            )
            self.assertEqual(
                c.load_profile.weighted_avg_measure_life,
                40.0,
            )
            self.assertEqual(c.load_profile.electric_allocation, 0.08)
            self.assertEqual(
                c.load_profile.gas_allocation,
                0.92,
            )

    def test_builder_allocation_data(self):
        input_data = self.input_data.copy()
        c = Incentives2020(**input_data)

        with self.subTest("Both Utilities"):
            self.assertEqual(c.home_path, HomePath.PATH_1)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
            self.assertEqual(c.electric_utility, ElectricUtility.PACIFIC_POWER)
            self.assertEqual(c.gas_utility, GasUtility.NW_NATURAL)
            builder_data = c.builder_allocation_data
            self.assertEqual(builder_data.electric.allocation, c.load_profile.electric_allocation)
            self.assertEqual(round(builder_data.electric.incentive, 2), 581.90)
            self.assertEqual(builder_data.electric.fuel, "Electric")
            self.assertEqual(
                builder_data.electric.load_profile, c.load_profile.electric_load_profile
            )
            self.assertEqual(builder_data.electric.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(builder_data.gas.allocation, c.load_profile.gas_allocation)
            self.assertEqual(round(builder_data.gas.incentive, 2), 1103.03)
            self.assertEqual(builder_data.gas.fuel, "Gas")
            self.assertEqual(builder_data.gas.load_profile, c.load_profile.gas_load_profile)
            self.assertEqual(builder_data.gas.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(builder_data.incentive, c.full_territory_builder_incentive)
            self.assertEqual(builder_data.waml, c.load_profile.weighted_avg_measure_life)
        with self.subTest("Only Electric"):
            input_data["gas_utility"] = GasUtility.NONE
            input_data["percent_improvement"] = 0.4682
            c = Incentives2020(**input_data)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
            self.assertEqual(c.electric_utility, ElectricUtility.PACIFIC_POWER)
            self.assertEqual(c.gas_utility, GasUtility.NONE)
            builder_data = c.builder_allocation_data
            self.assertEqual(builder_data.electric.allocation, c.load_profile.electric_allocation)
            self.assertEqual(round(builder_data.electric.incentive, 2), 417.84)
            self.assertEqual(builder_data.electric.fuel, "Electric")
            self.assertEqual(
                builder_data.electric.load_profile, c.load_profile.electric_load_profile
            )
            self.assertEqual(builder_data.electric.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(builder_data.gas.allocation, c.load_profile.gas_allocation)
            self.assertEqual(round(builder_data.gas.incentive, 2), 0.0)
            self.assertEqual(builder_data.gas.fuel, "Gas")
            self.assertEqual(builder_data.gas.load_profile, c.load_profile.gas_load_profile)
            self.assertEqual(builder_data.gas.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(round(builder_data.incentive, 2), 417.84)
            self.assertEqual(builder_data.waml, c.load_profile.weighted_avg_measure_life)

        with self.subTest("Only Gas"):
            input_data["gas_utility"] = GasUtility.AVISTA
            input_data["electric_utility"] = ElectricUtility.NONE
            c = Incentives2020(**input_data)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
            self.assertEqual(c.electric_utility, ElectricUtility.NONE)
            self.assertEqual(c.gas_utility, GasUtility.AVISTA)
            builder_data = c.builder_allocation_data
            self.assertEqual(builder_data.electric.allocation, c.load_profile.electric_allocation)
            self.assertEqual(round(builder_data.electric.incentive, 2), 0.0)
            self.assertEqual(builder_data.electric.fuel, "Electric")
            self.assertEqual(
                builder_data.electric.load_profile, c.load_profile.electric_load_profile
            )
            self.assertEqual(builder_data.electric.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(builder_data.gas.allocation, c.load_profile.gas_allocation)
            self.assertEqual(round(builder_data.gas.incentive, 2), 4805.16)
            self.assertEqual(builder_data.gas.fuel, "Gas")
            self.assertEqual(builder_data.gas.load_profile, c.load_profile.gas_load_profile)
            self.assertEqual(builder_data.gas.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(round(builder_data.incentive, 2), 4805.16)
            self.assertEqual(builder_data.waml, c.load_profile.weighted_avg_measure_life)

        with self.subTest("Neither"):
            input_data["gas_utility"] = GasUtility.NONE
            input_data["electric_utility"] = ElectricUtility.NONE
            c = Incentives2020(**input_data)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
            self.assertEqual(c.electric_utility, ElectricUtility.NONE)
            self.assertEqual(c.gas_utility, GasUtility.NONE)

            builder_data = c.builder_allocation_data
            self.assertEqual(builder_data.electric.allocation, c.load_profile.electric_allocation)
            self.assertEqual(round(builder_data.electric.incentive, 2), 0.0)
            self.assertEqual(builder_data.electric.fuel, "Electric")
            self.assertEqual(
                builder_data.electric.load_profile, c.load_profile.electric_load_profile
            )
            self.assertEqual(builder_data.electric.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(builder_data.gas.allocation, c.load_profile.gas_allocation)
            self.assertEqual(round(builder_data.gas.incentive, 2), 0.0)
            self.assertEqual(builder_data.gas.fuel, "Gas")
            self.assertEqual(builder_data.gas.load_profile, c.load_profile.gas_load_profile)
            self.assertEqual(builder_data.gas.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(round(builder_data.incentive, 2), 0.0)
            self.assertEqual(builder_data.waml, c.load_profile.weighted_avg_measure_life)

    def test_initial_verifier_incentive(self):
        input_data = self.input_data.copy()

        with self.subTest("Too Low % Improvement"):
            input_data.update({"percent_improvement": 0.0999})
            c = Incentives2020(**input_data)
            self.assertEqual(c.initial_verifier_incentive, 0.0)

        with self.subTest("Min threshold"):
            input_data.update({"percent_improvement": 0.1})
            c = Incentives2020(**input_data)
            self.assertEqual(c.initial_verifier_incentive, 300.00)

        with self.subTest("Capped threshold"):
            input_data.update({"percent_improvement": 0.41})
            c = Incentives2020(**input_data)
            self.assertEqual(round(c.initial_verifier_incentive, 2), 1889.20)

    def test_verifier_allocation_data(self):
        input_data = self.input_data.copy()
        c = Incentives2020(**input_data)

        with self.subTest("Both Utilities"):
            self.assertEqual(c.home_path, HomePath.PATH_1)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
            self.assertEqual(c.electric_utility, ElectricUtility.PACIFIC_POWER)
            self.assertEqual(c.gas_utility, GasUtility.NW_NATURAL)
            verifier_data = c.verifier_allocation_data
            self.assertEqual(verifier_data.electric.allocation, c.load_profile.electric_allocation)
            self.assertEqual(round(verifier_data.electric.incentive, 2), 103.61)
            self.assertEqual(verifier_data.electric.fuel, "Electric")
            self.assertEqual(
                verifier_data.electric.load_profile, c.load_profile.electric_load_profile
            )
            self.assertEqual(verifier_data.electric.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(verifier_data.gas.allocation, c.load_profile.gas_allocation)
            self.assertEqual(round(verifier_data.gas.incentive, 2), 196.39)
            self.assertEqual(verifier_data.gas.fuel, "Gas")
            self.assertEqual(verifier_data.gas.load_profile, c.load_profile.gas_load_profile)
            self.assertEqual(verifier_data.gas.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(verifier_data.incentive, c.initial_verifier_incentive)
            self.assertEqual(verifier_data.waml, c.load_profile.weighted_avg_measure_life)
        with self.subTest("Only Electric"):
            input_data["gas_utility"] = GasUtility.NONE
            c = Incentives2020(**input_data)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
            self.assertEqual(c.electric_utility, ElectricUtility.PACIFIC_POWER)
            self.assertEqual(c.gas_utility, GasUtility.NONE)
            verifier_data = c.verifier_allocation_data

            self.assertEqual(verifier_data.electric.allocation, 1.0)
            self.assertEqual(
                round(verifier_data.electric.incentive, 2), c.initial_verifier_incentive
            )
            self.assertEqual(verifier_data.electric.fuel, "Electric")
            self.assertEqual(
                verifier_data.electric.load_profile, c.load_profile.electric_load_profile
            )
            self.assertEqual(verifier_data.electric.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(verifier_data.gas.allocation, 0.0)
            self.assertEqual(round(verifier_data.gas.incentive, 2), 0.0)
            self.assertEqual(verifier_data.gas.fuel, "Gas")
            self.assertEqual(verifier_data.gas.load_profile, c.load_profile.gas_load_profile)
            self.assertEqual(verifier_data.gas.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(verifier_data.incentive, c.initial_verifier_incentive)
            self.assertEqual(verifier_data.waml, c.load_profile.weighted_avg_measure_life)

        with self.subTest("Only Gas"):
            input_data["gas_utility"] = GasUtility.AVISTA
            input_data["electric_utility"] = ElectricUtility.NONE
            c = Incentives2020(**input_data)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
            self.assertEqual(c.electric_utility, ElectricUtility.NONE)
            self.assertEqual(c.gas_utility, GasUtility.AVISTA)
            verifier_data = c.verifier_allocation_data

            self.assertEqual(verifier_data.electric.allocation, 0.0)
            self.assertEqual(round(verifier_data.electric.incentive, 2), 0.0)
            self.assertEqual(verifier_data.electric.fuel, "Electric")
            self.assertEqual(
                verifier_data.electric.load_profile, c.load_profile.electric_load_profile
            )
            self.assertEqual(verifier_data.electric.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(verifier_data.gas.allocation, 1.0)
            self.assertEqual(round(verifier_data.gas.incentive, 2), c.initial_verifier_incentive)
            self.assertEqual(verifier_data.gas.fuel, "Gas")
            self.assertEqual(verifier_data.gas.load_profile, c.load_profile.gas_load_profile)
            self.assertEqual(verifier_data.gas.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(verifier_data.incentive, c.initial_verifier_incentive)
            self.assertEqual(verifier_data.waml, c.load_profile.weighted_avg_measure_life)

        with self.subTest("Neither"):
            input_data["gas_utility"] = GasUtility.NONE
            input_data["electric_utility"] = ElectricUtility.NONE
            c = Incentives2020(**input_data)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
            self.assertEqual(c.electric_utility, ElectricUtility.NONE)
            self.assertEqual(c.gas_utility, GasUtility.NONE)
            verifier_data = c.verifier_allocation_data

            self.assertEqual(verifier_data.electric.allocation, 0.0)
            self.assertEqual(round(verifier_data.electric.incentive, 2), 0.0)
            self.assertEqual(verifier_data.electric.fuel, "Electric")
            self.assertEqual(
                verifier_data.electric.load_profile, c.load_profile.electric_load_profile
            )
            self.assertEqual(verifier_data.electric.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(verifier_data.gas.allocation, 0.0)
            self.assertEqual(round(verifier_data.gas.incentive, 2), 0.0)
            self.assertEqual(verifier_data.gas.fuel, "Gas")
            self.assertEqual(verifier_data.gas.load_profile, c.load_profile.gas_load_profile)
            self.assertEqual(verifier_data.gas.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(verifier_data.incentive, 0.0)
            self.assertEqual(verifier_data.waml, c.load_profile.weighted_avg_measure_life)

    def test_incentive_report(self):
        input_data = self.input_data.copy()
        input_data.update(
            {"percent_improvement": 0.46, "heating_therms": 0.99, "hot_water_kwh": 1.1}
        )

        c = Incentives2020(**input_data)
        self.assertIn("Builder Incentive", c.incentive_report)
        self.assertIn("$ 5,223.00", c.incentive_report)
        self.assertIn("Verifier Incentive", c.incentive_report)
        self.assertIn("$ 1,889.20", c.incentive_report)


class IncentiveWATests(TestCase):
    @property
    def input_data(self):
        return {
            "percent_improvement": 0.09202531646272857,
            "heating_therms": 18.1,
            "hot_water_therms": 25.2,
            "hot_water_kwh": 1025.2,
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "gas_utility": GasUtility.NW_NATURAL,
            "constants": Constants(ElectricUtility.PACIFIC_POWER, PNWUSStates.WA),
        }

    def test_full_territory_builder_incentive(self):
        input_data = self.input_data.copy()

        with self.subTest("Too Low % Improvement"):
            input_data.update({"percent_improvement": 0.05})
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.full_territory_builder_incentive, 0.0)

        with self.subTest("Bad Utility"):
            input_data.update({"percent_improvement": 0.20})
            input_data["gas_utility"] = GasUtility.AVISTA
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.full_territory_builder_incentive, 0.0)

        input_data["gas_utility"] = GasUtility.NW_NATURAL
        with self.subTest("Hot Water Therms"):
            input_data.update({"percent_improvement": 0.15, "hot_water_therms": 1.0})
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.full_territory_builder_incentive, 1700.0)

        with self.subTest("Hot Water Therms Capped"):
            input_data.update({"percent_improvement": 1.15, "hot_water_therms": 1.0})
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.full_territory_builder_incentive, 2150.0)

        with self.subTest("Hot Water kwh"):
            input_data.update(
                {"percent_improvement": 0.15, "hot_water_therms": 0.0, "hot_water_kwh": 2.0}
            )
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.full_territory_builder_incentive, 1480.0)

        with self.subTest("Hot Water kwh Capped"):
            input_data.update(
                {"percent_improvement": 1.15, "hot_water_therms": 0.0, "hot_water_kwh": 2.0}
            )
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.full_territory_builder_incentive, 1920.0)

    def test_home_path(self):
        input_data = self.input_data.copy()

        with self.subTest("Path 1"):
            input_data.update({"percent_improvement": 0.05})
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_1)

            input_data.update({"percent_improvement": 0.0999})
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_1)

        with self.subTest("Path 2"):
            input_data.update({"percent_improvement": 0.1})
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_2)

            input_data.update({"percent_improvement": 0.1499})
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_2)

        with self.subTest("Path 3"):
            input_data.update({"percent_improvement": 0.15})
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_3)

            input_data.update({"percent_improvement": 0.1999})
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_3)

        with self.subTest("Path 4"):
            input_data.update({"percent_improvement": 0.2})
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_4)

            input_data.update({"percent_improvement": 0.999})
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_4)

    def test_load_profile(self):
        """We don't test all just a good sample"""
        input_data = self.input_data.copy()
        with self.subTest("Path 1 GH+GW"):
            input_data.update(
                {"percent_improvement": 0.09, "heating_therms": 1.1, "hot_water_therms": 1.1}
            )
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_1)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
            self.assertEqual(
                c.load_profile.electric_load_profile,
                ElectricLoadProfile.RESIDENTIAL_LIGHTING,
            )
            self.assertEqual(
                c.load_profile.gas_load_profile,
                GasLoadProfile.RESIDENTIAL_HEATING,
            )
            self.assertEqual(
                c.load_profile.weighted_avg_measure_life,
                44.0,
            )
            self.assertEqual(
                c.load_profile.electric_allocation,
                0.0,
            )
            self.assertEqual(
                c.load_profile.gas_allocation,
                1.0,
            )
        with self.subTest("Path 2 GH+EW"):
            input_data.update(
                {
                    "percent_improvement": 0.12,
                    "heating_therms": 1.1,
                    "hot_water_kwh": 1.1,
                    "hot_water_therms": 0.99,
                }
            )
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_2)
            self.assertEqual(c.sub_type, HomeSubType.GHEW)
            self.assertEqual(
                c.load_profile.electric_load_profile,
                ElectricLoadProfile.RESIDENTIAL_LIGHTING,
            )
            self.assertEqual(
                c.load_profile.gas_load_profile,
                GasLoadProfile.RESIDENTIAL_HEATING,
            )
            self.assertEqual(
                c.load_profile.weighted_avg_measure_life,
                38.0,
            )
            self.assertEqual(
                c.load_profile.electric_allocation,
                0.0,
            )
            self.assertEqual(
                c.load_profile.gas_allocation,
                1.0,
            )

        with self.subTest("Path 3 EH+GW"):
            input_data.update(
                {
                    "percent_improvement": 0.18,
                    "heating_therms": 0.99,
                    "hot_water_kwh": 0.0,
                    "hot_water_therms": 1.1,
                }
            )
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_3)
            self.assertEqual(c.sub_type, HomeSubType.EHGW)
            self.assertEqual(
                c.load_profile.electric_load_profile,
                ElectricLoadProfile.RESIDENTIAL_LIGHTING,
            )
            self.assertEqual(
                c.load_profile.gas_load_profile,
                GasLoadProfile.RESIDENTIAL_HEATING,
            )
            self.assertEqual(
                c.load_profile.weighted_avg_measure_life,
                39.0,
            )
            self.assertEqual(
                c.load_profile.electric_allocation,
                0.0,
            )
            self.assertEqual(
                c.load_profile.gas_allocation,
                1.0,
            )
        with self.subTest("Path 4 EH+EW"):
            input_data.update(
                {
                    "percent_improvement": 0.21,
                    "heating_therms": 0.99,
                    "hot_water_kwh": 1.1,
                    "hot_water_therms": 0.99,
                }
            )
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_4)
            self.assertEqual(c.sub_type, HomeSubType.EHEW)
            self.assertEqual(
                c.load_profile.electric_load_profile,
                ElectricLoadProfile.RESIDENTIAL_LIGHTING,
            )
            self.assertEqual(
                c.load_profile.gas_load_profile,
                GasLoadProfile.RESIDENTIAL_HEATING,
            )
            self.assertEqual(
                c.load_profile.weighted_avg_measure_life,
                41.0,
            )
            self.assertEqual(c.load_profile.electric_allocation, 0.0)
            self.assertEqual(
                c.load_profile.gas_allocation,
                1.0,
            )

    def test_builder_allocation_data(self):
        input_data = self.input_data.copy()

        with self.subTest("Both Utilities"):
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_1)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
            self.assertEqual(c.electric_utility, ElectricUtility.PACIFIC_POWER)
            self.assertEqual(c.gas_utility, GasUtility.NW_NATURAL)
            builder_data = c.builder_allocation_data
            self.assertEqual(builder_data.electric.allocation, c.load_profile.electric_allocation)
            self.assertEqual(builder_data.electric.incentive, 0.0)
            self.assertEqual(builder_data.electric.fuel, "Electric")
            self.assertEqual(
                builder_data.electric.load_profile, c.load_profile.electric_load_profile
            )
            self.assertEqual(builder_data.electric.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(builder_data.gas.allocation, c.load_profile.gas_allocation)
            self.assertEqual(builder_data.gas.incentive, c.full_territory_builder_incentive)
            self.assertEqual(builder_data.gas.fuel, "Gas")
            self.assertEqual(builder_data.gas.load_profile, c.load_profile.gas_load_profile)
            self.assertEqual(builder_data.gas.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(builder_data.incentive, c.full_territory_builder_incentive)
            self.assertEqual(round(builder_data.incentive, 2), 1178.23)
            self.assertEqual(builder_data.waml, c.load_profile.weighted_avg_measure_life)
        with self.subTest("Only Electric"):
            input_data["gas_utility"] = GasUtility.NONE
            input_data["percent_improvement"] = 0.4682
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
            self.assertEqual(c.electric_utility, ElectricUtility.PACIFIC_POWER)
            self.assertEqual(c.gas_utility, GasUtility.NONE)
            builder_data = c.builder_allocation_data
            self.assertEqual(builder_data.electric.allocation, c.load_profile.electric_allocation)
            self.assertEqual(builder_data.electric.incentive, 0.0)
            self.assertEqual(builder_data.electric.fuel, "Electric")
            self.assertEqual(
                builder_data.electric.load_profile, c.load_profile.electric_load_profile
            )
            self.assertEqual(builder_data.electric.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(builder_data.gas.allocation, c.load_profile.gas_allocation)
            self.assertEqual(builder_data.gas.incentive, 0.0)
            self.assertEqual(builder_data.gas.fuel, "Gas")
            self.assertEqual(builder_data.gas.load_profile, c.load_profile.gas_load_profile)
            self.assertEqual(builder_data.gas.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(builder_data.incentive, 0.0)
            self.assertEqual(builder_data.waml, c.load_profile.weighted_avg_measure_life)

        with self.subTest("Only Gas (NWN)"):
            input_data["gas_utility"] = GasUtility.NW_NATURAL
            input_data["electric_utility"] = ElectricUtility.NONE
            input_data["percent_improvement"] = 0.0844
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
            self.assertEqual(c.electric_utility, ElectricUtility.NONE)
            self.assertEqual(c.gas_utility, GasUtility.NW_NATURAL)
            builder_data = c.builder_allocation_data
            self.assertEqual(builder_data.electric.allocation, c.load_profile.electric_allocation)
            self.assertEqual(builder_data.electric.incentive, 0.0)
            self.assertEqual(builder_data.electric.fuel, "Electric")
            self.assertEqual(
                builder_data.electric.load_profile, c.load_profile.electric_load_profile
            )
            self.assertEqual(builder_data.electric.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(builder_data.gas.allocation, c.load_profile.gas_allocation)
            self.assertEqual(builder_data.gas.incentive, c.full_territory_builder_incentive)
            self.assertEqual(builder_data.gas.fuel, "Gas")
            self.assertEqual(builder_data.gas.load_profile, c.load_profile.gas_load_profile)
            self.assertEqual(builder_data.gas.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(round(builder_data.incentive, 2), 1109.60)
            self.assertEqual(builder_data.waml, c.load_profile.weighted_avg_measure_life)

        with self.subTest("Neither"):
            input_data["gas_utility"] = GasUtility.NONE
            input_data["electric_utility"] = ElectricUtility.NONE
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
            self.assertEqual(c.electric_utility, ElectricUtility.NONE)
            self.assertEqual(c.gas_utility, GasUtility.NONE)

            builder_data = c.builder_allocation_data
            self.assertEqual(builder_data.electric.allocation, c.load_profile.electric_allocation)
            self.assertEqual(builder_data.electric.incentive, 0.0)
            self.assertEqual(builder_data.electric.fuel, "Electric")
            self.assertEqual(
                builder_data.electric.load_profile, c.load_profile.electric_load_profile
            )
            self.assertEqual(builder_data.electric.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(builder_data.gas.allocation, c.load_profile.gas_allocation)
            self.assertEqual(round(builder_data.gas.incentive, 2), 0.0)
            self.assertEqual(builder_data.gas.fuel, "Gas")
            self.assertEqual(builder_data.gas.load_profile, c.load_profile.gas_load_profile)
            self.assertEqual(builder_data.gas.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(round(builder_data.incentive, 2), 0.0)
            self.assertEqual(builder_data.waml, c.load_profile.weighted_avg_measure_life)

    def test_initial_verifier_incentive(self):
        input_data = self.input_data.copy()

        with self.subTest("Too Low % Improvement"):
            input_data.update({"percent_improvement": 0.0499})
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.initial_verifier_incentive, 0.0)

        input_data["percent_improvement"] = 0.101
        with self.subTest("Bad Utility"):
            input_data.update({"gas_utility": GasUtility.AVISTA})
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.initial_verifier_incentive, 0.0)

        input_data["gas_utility"] = GasUtility.NW_NATURAL
        with self.subTest("Max / Default"):
            input_data.update({"percent_improvement": 0.1})
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.initial_verifier_incentive, 100.0)

    def test_verifier_allocation_data(self):
        input_data = self.input_data.copy()
        input_data["percent_improvement"] = 0.11

        with self.subTest("Both Utilities"):
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_2)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
            self.assertEqual(c.electric_utility, ElectricUtility.PACIFIC_POWER)
            self.assertEqual(c.gas_utility, GasUtility.NW_NATURAL)
            verifier_data = c.verifier_allocation_data
            self.assertEqual(verifier_data.electric.allocation, c.load_profile.electric_allocation)
            self.assertEqual(verifier_data.electric.incentive, 0.0)
            self.assertEqual(verifier_data.electric.fuel, "Electric")
            self.assertEqual(
                verifier_data.electric.load_profile, c.load_profile.electric_load_profile
            )
            self.assertEqual(verifier_data.electric.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(verifier_data.gas.allocation, c.load_profile.gas_allocation)
            self.assertEqual(verifier_data.gas.incentive, c.initial_verifier_incentive)
            self.assertEqual(verifier_data.gas.fuel, "Gas")
            self.assertEqual(verifier_data.gas.load_profile, c.load_profile.gas_load_profile)
            self.assertEqual(verifier_data.gas.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(verifier_data.incentive, c.initial_verifier_incentive)
            self.assertEqual(round(verifier_data.incentive, 2), 100.00)
            self.assertEqual(verifier_data.waml, c.load_profile.weighted_avg_measure_life)
        with self.subTest("Only Electric"):
            input_data["gas_utility"] = GasUtility.NONE
            input_data["percent_improvement"] = 0.4682
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
            self.assertEqual(c.electric_utility, ElectricUtility.PACIFIC_POWER)
            self.assertEqual(c.gas_utility, GasUtility.NONE)
            verifier_data = c.verifier_allocation_data
            self.assertEqual(verifier_data.electric.allocation, c.load_profile.electric_allocation)
            self.assertEqual(verifier_data.electric.incentive, 0.0)
            self.assertEqual(verifier_data.electric.fuel, "Electric")
            self.assertEqual(
                verifier_data.electric.load_profile, c.load_profile.electric_load_profile
            )
            self.assertEqual(verifier_data.electric.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(verifier_data.gas.allocation, c.load_profile.gas_allocation)
            self.assertEqual(verifier_data.gas.incentive, 0.0)
            self.assertEqual(verifier_data.gas.fuel, "Gas")
            self.assertEqual(verifier_data.gas.load_profile, c.load_profile.gas_load_profile)
            self.assertEqual(verifier_data.gas.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(verifier_data.incentive, 0.0)
            self.assertEqual(verifier_data.waml, c.load_profile.weighted_avg_measure_life)

        with self.subTest("Only Gas (NWN)"):
            input_data["gas_utility"] = GasUtility.NW_NATURAL
            input_data["electric_utility"] = ElectricUtility.NONE
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
            self.assertEqual(c.electric_utility, ElectricUtility.NONE)
            self.assertEqual(c.gas_utility, GasUtility.NW_NATURAL)
            verifier_data = c.verifier_allocation_data
            self.assertEqual(verifier_data.electric.allocation, c.load_profile.electric_allocation)
            self.assertEqual(verifier_data.electric.incentive, 0.0)
            self.assertEqual(verifier_data.electric.fuel, "Electric")
            self.assertEqual(
                verifier_data.electric.load_profile, c.load_profile.electric_load_profile
            )
            self.assertEqual(verifier_data.electric.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(verifier_data.gas.allocation, c.load_profile.gas_allocation)
            self.assertEqual(verifier_data.gas.incentive, c.initial_verifier_incentive)
            self.assertEqual(verifier_data.gas.fuel, "Gas")
            self.assertEqual(verifier_data.gas.load_profile, c.load_profile.gas_load_profile)
            self.assertEqual(verifier_data.gas.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(round(verifier_data.incentive, 2), 100.00)
            self.assertEqual(verifier_data.waml, c.load_profile.weighted_avg_measure_life)

        with self.subTest("Neither"):
            input_data["gas_utility"] = GasUtility.NONE
            input_data["electric_utility"] = ElectricUtility.NONE
            c = Incentives2021WA(**input_data)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
            self.assertEqual(c.electric_utility, ElectricUtility.NONE)
            self.assertEqual(c.gas_utility, GasUtility.NONE)

            verifier_data = c.verifier_allocation_data
            self.assertEqual(verifier_data.electric.allocation, c.load_profile.electric_allocation)
            self.assertEqual(verifier_data.electric.incentive, 0.0)
            self.assertEqual(verifier_data.electric.fuel, "Electric")
            self.assertEqual(
                verifier_data.electric.load_profile, c.load_profile.electric_load_profile
            )
            self.assertEqual(verifier_data.electric.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(verifier_data.gas.allocation, c.load_profile.gas_allocation)
            self.assertEqual(round(verifier_data.gas.incentive, 2), 0.0)
            self.assertEqual(verifier_data.gas.fuel, "Gas")
            self.assertEqual(verifier_data.gas.load_profile, c.load_profile.gas_load_profile)
            self.assertEqual(verifier_data.gas.waml, c.load_profile.weighted_avg_measure_life)

            self.assertEqual(round(verifier_data.incentive, 2), 0.0)
            self.assertEqual(verifier_data.waml, c.load_profile.weighted_avg_measure_life)

    def test_incentive_report(self):
        input_data = self.input_data.copy()
        input_data.update(
            {"percent_improvement": 0.46, "heating_therms": 0.99, "hot_water_kwh": 1.1}
        )

        c = Incentives2021WA(**input_data)

        self.assertIn("Gas Percent Improvement", c.incentive_report)
        self.assertIn("$ 2,150.00", c.incentive_report)
        self.assertIn("Verifier Incentive", c.incentive_report)
        self.assertIn("$ 100.00", c.incentive_report)
