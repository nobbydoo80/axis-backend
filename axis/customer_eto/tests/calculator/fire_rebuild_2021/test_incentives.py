"""test_incentives.py - Axis"""

__author__ = "Steven K"
__date__ = "12/4/21 08:58"
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
from axis.customer_eto.calculator.eps_fire_2021.constants import FireConstants
from axis.customer_eto.calculator.eps_fire_2021.incentives import Incentives2021Fire
from axis.customer_eto.enumerations import GasUtility, ElectricUtility, PNWUSStates

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
            "constants": FireConstants(ElectricUtility.PACIFIC_POWER, PNWUSStates.OR),
        }

    def test_full_territory_builder_incentive(self):
        input_data = self.input_data.copy()

        with self.subTest("Too Low % Improvement"):
            input_data.update({"percent_improvement": 0.0999})
            c = Incentives2021Fire(**input_data)
            self.assertEqual(c.full_territory_builder_incentive, 0.0)

        with self.subTest("Min threshold"):
            input_data.update({"percent_improvement": 0.1})
            c = Incentives2021Fire(**input_data)
            self.assertEqual(c.full_territory_builder_incentive, 1123.02 * 2)

        with self.subTest("Capped threshold"):
            input_data.update({"percent_improvement": 0.45})
            c = Incentives2021Fire(**input_data)
            self.assertEqual(c.full_territory_builder_incentive, 8171.0)

    def test_home_path(self):
        input_data = self.input_data.copy()

        with self.subTest("Path 1"):
            input_data.update({"percent_improvement": 0.1})
            c = Incentives2021Fire(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_1)

            input_data.update({"percent_improvement": 0.1999})
            c = Incentives2021Fire(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_1)

        with self.subTest("Path 2"):
            input_data.update({"percent_improvement": 0.2})
            c = Incentives2021Fire(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_2)

            input_data.update({"percent_improvement": 0.2999})
            c = Incentives2021Fire(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_2)

        with self.subTest("Path 3"):
            input_data.update({"percent_improvement": 0.3})
            c = Incentives2021Fire(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_3)

            input_data.update({"percent_improvement": 0.3499})
            c = Incentives2021Fire(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_3)

        with self.subTest("Path 4"):
            input_data.update({"percent_improvement": 0.35})
            c = Incentives2021Fire(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_4)

            input_data.update({"percent_improvement": 0.999})
            c = Incentives2021Fire(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_4)

    def test_load_profile(self):
        """We don't test all just a good sample"""
        input_data = self.input_data.copy()
        with self.subTest("Path 1 GH+GW"):
            input_data.update(
                {"percent_improvement": 0.15, "heating_therms": 1.1, "hot_water_therms": 1.1}
            )
            c = Incentives2021Fire(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_1)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
            self.assertEqual(
                c.load_profile.electric_load_profile,
                ElectricLoadProfile.RESIDENTIAL_CENTRAL_AC,
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
                0.290,
            )
            self.assertEqual(
                c.load_profile.gas_allocation,
                0.710,
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
            c = Incentives2021Fire(**input_data)
            self.assertEqual(c.home_path, HomePath.PATH_2)
            self.assertEqual(c.sub_type, HomeSubType.GHEW)
            self.assertEqual(
                c.load_profile.electric_load_profile,
                ElectricLoadProfile.RESIDENTIAL_WATER_HEAT,
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
                0.320,
            )
            self.assertEqual(
                c.load_profile.gas_allocation,
                0.680,
            )

        with self.subTest("Path 3 EH+GW"):
            input_data.update(
                {
                    "percent_improvement": 0.325,
                    "heating_therms": 0.99,
                    "hot_water_kwh": 0.0,
                    "hot_water_therms": 1.1,
                }
            )
            c = Incentives2021Fire(**input_data)
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
                35.0,
            )
            self.assertEqual(
                c.load_profile.electric_allocation,
                0.910,
            )
            self.assertEqual(
                c.load_profile.gas_allocation,
                0.090,
            )
        with self.subTest("Path 4 EH+EW"):
            input_data.update(
                {
                    "percent_improvement": 0.35,
                    "heating_therms": 0.99,
                    "hot_water_kwh": 1.1,
                    "hot_water_therms": 0.99,
                }
            )
            c = Incentives2021Fire(**input_data)
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
                34.0,
            )
            self.assertEqual(c.load_profile.electric_allocation, 1.0)
            self.assertEqual(
                c.load_profile.gas_allocation,
                0.0,
            )

    def test_verifier_incentives(self):
        """Test out the new verifier incentives"""
        with self.subTest("< 10% Improvement"):
            input_data = self.input_data.copy()
            input_data.update(
                {"percent_improvement": 0.099, "heating_therms": 0.99, "hot_water_kwh": 1.1}
            )
            c = Incentives2021Fire(**input_data)
            self.assertEqual(c.initial_verifier_incentive, 0)
            self.assertEqual(c.verifier_incentive, 0)
        with self.subTest("10% Improvement"):
            input_data = self.input_data.copy()
            input_data.update(
                {"percent_improvement": 0.10, "heating_therms": 0.99, "hot_water_kwh": 1.1}
            )
            c = Incentives2021Fire(**input_data)
            self.assertEqual(c.initial_verifier_incentive, 300.0)
            self.assertEqual(c.verifier_incentive, 300.0)
        with self.subTest("< 20% Improvement"):
            input_data = self.input_data.copy()
            input_data.update(
                {"percent_improvement": 0.199, "heating_therms": 0.99, "hot_water_kwh": 1.1}
            )
            c = Incentives2021Fire(**input_data)
            self.assertEqual(c.initial_verifier_incentive, 300.0)
            self.assertEqual(c.verifier_incentive, 300.0)
        with self.subTest("20% Improvement"):
            input_data = self.input_data.copy()
            input_data.update(
                {"percent_improvement": 0.20, "heating_therms": 0.99, "hot_water_kwh": 1.1}
            )
            c = Incentives2021Fire(**input_data)
            self.assertEqual(c.initial_verifier_incentive, c.full_territory_builder_incentive * 0.2)
            self.assertEqual(c.verifier_incentive, 705.0)

    def test_incentive_report(self):
        input_data = self.input_data.copy()
        input_data.update(
            {"percent_improvement": 0.46, "heating_therms": 0.99, "hot_water_kwh": 1.1}
        )

        c = Incentives2021Fire(**input_data)

        self.assertIn("2022 Fire Rebuild Builder Incentive", c.incentive_report)
        self.assertIn("Builder Incentive", c.incentive_report)
        self.assertIn("$ 8,171.00", c.incentive_report)
        self.assertIn("Verifier Incentive", c.incentive_report)
        self.assertIn("$ 1,634.20", c.incentive_report)
