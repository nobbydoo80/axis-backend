"""test_allocation.py - Axis"""

__author__ = "Steven K"
__date__ = "3/4/22 13:36"
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
from axis.customer_eto.calculator.eps_2022.allocations import Allocation
from axis.customer_eto.calculator.eps_2022.incentives import IncentiveItem
from axis.customer_eto.enumerations import ElectricUtility, GasUtility, HeatType

log = logging.getLogger(__name__)


class EPS2022AllocationTests(TestCase):
    @property
    def input_options(self):
        return {
            "percent_improvement": 0.0,
            "heating_therms": 0.0,
            "hot_water_therms": 0.0,
            "electric_utility": ElectricUtility.NONE,
            "gas_utility": GasUtility.NONE,
            "builder_base_incentive": 0.0,
            "builder_additional_incentives": [],
            "verifier_base_incentive": False,
            "verifier_additional_incentives": [],  # IncentiveItem(incentive=10.0, budget="ENH")
            "heat_type": HeatType.GAS,
        }.copy()

    def test_mins(self):
        opts = self.input_options
        data = Allocation(**opts)
        self.assertIn("Total       $ 0.00     $ 0.00", data.allocation_summary)
        self.assertIn("Total       $ 0.00     $ 0.00", data.allocation_report)

    def test_home_path(self):
        opts = self.input_options
        with self.subTest("Path 1"):
            opts.update({"percent_improvement": 0.1})
            c = Allocation(**opts)
            self.assertEqual(c.home_path, HomePath.PATH_1)

            opts.update({"percent_improvement": 0.1999})
            c = Allocation(**opts)
            self.assertEqual(c.home_path, HomePath.PATH_1)

        with self.subTest("Path 2"):
            opts.update({"percent_improvement": 0.2})
            c = Allocation(**opts)
            self.assertEqual(c.home_path, HomePath.PATH_2)

            opts.update({"percent_improvement": 0.2999})
            c = Allocation(**opts)
            self.assertEqual(c.home_path, HomePath.PATH_2)

        with self.subTest("Path 3"):
            opts.update({"percent_improvement": 0.3})
            c = Allocation(**opts)
            self.assertEqual(c.home_path, HomePath.PATH_3)

            opts.update({"percent_improvement": 0.3499})
            c = Allocation(**opts)
            self.assertEqual(c.home_path, HomePath.PATH_3)

        with self.subTest("Path 4"):
            opts.update({"percent_improvement": 0.35})
            c = Allocation(**opts)
            self.assertEqual(c.home_path, HomePath.PATH_4)

            opts.update({"percent_improvement": 0.999})
            c = Allocation(**opts)
            self.assertEqual(c.home_path, HomePath.PATH_4)

    def test_sub_type(self):
        """Test out the sub type."""
        opts = self.input_options
        with self.subTest("GH+GW"):
            opts.update({"heating_therms": 1.1, "hot_water_therms": 1.1})
            c = Allocation(**opts)
            self.assertEqual(c.sub_type, HomeSubType.GHGW)
        with self.subTest("EH+EW"):
            opts.update({"heating_therms": 0.0, "hot_water_therms": 0.0})
            c = Allocation(**opts)
            self.assertEqual(c.sub_type, HomeSubType.EHEW)
        with self.subTest("GH+EW"):
            opts.update({"heating_therms": 1.1, "hot_water_therms": 0.0})
            c = Allocation(**opts)
            self.assertEqual(c.sub_type, HomeSubType.GHEW)
        with self.subTest("EH+GW"):
            opts.update({"heating_therms": 0.0, "hot_water_therms": 1.1})
            c = Allocation(**opts)
            self.assertEqual(c.sub_type, HomeSubType.EHGW)

    def test_load_profile(self):
        """We don't test all just a good sample"""

        opts = self.input_options
        opts["electric_utility"] = ElectricUtility.PACIFIC_POWER
        opts["gas_utility"] = GasUtility.NW_NATURAL
        with self.subTest("Path 1 GH+GW"):
            opts.update(
                {
                    "percent_improvement": 0.15,
                    "heating_therms": 1.1,
                    "hot_water_therms": 1.1,
                }
            )
            c = Allocation(**opts)
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
                36.0,
            )
            self.assertEqual(
                c.load_profile.electric_allocation,
                0.130,
            )
            self.assertEqual(
                c.load_profile.gas_allocation,
                0.870,
            )
        with self.subTest("Path 2 GH+EW"):
            opts.update(
                {
                    "percent_improvement": 0.25,
                    "heating_therms": 1.1,
                    "hot_water_therms": 0.0,
                }
            )
            c = Allocation(**opts)
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
                27.0,
            )
            self.assertEqual(
                c.load_profile.electric_allocation,
                0.62,
            )
            self.assertEqual(
                c.load_profile.gas_allocation,
                0.38,
            )

        with self.subTest("Path 3 EH+GW"):
            opts.update(
                {
                    "percent_improvement": 0.32,
                    "heating_therms": 0.0,
                    "hot_water_therms": 1.1,
                }
            )
            c = Allocation(**opts)
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
                0.79,
            )
            self.assertEqual(
                c.load_profile.gas_allocation,
                0.21,
            )
        with self.subTest("Path 4 EH+EW"):
            opts.update(
                {
                    "percent_improvement": 0.38,
                    "heating_therms": 0.0,
                    "hot_water_therms": 0.0,
                }
            )
            c = Allocation(**opts)
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

    def test_partial_load_profile(self):
        """We don't test all just a good sample"""
        input_data = self.input_options
        input_data["gas_utility"] = GasUtility.CASCADE
        input_data["electric_utility"] = ElectricUtility.NONE
        with self.subTest("Path 1 GHEW Partial"):
            input_data.update(
                {
                    "percent_improvement": 0.12,
                    "heating_therms": 0.99,
                    "hot_water_therms": 0,
                }
            )
            c = Allocation(**input_data)
            self.assertEqual(c.partial_territory, True)
            self.assertEqual(c.home_path, HomePath.PATH_1)
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
                35.0,
            )
            self.assertEqual(
                c.load_profile.electric_allocation,
                0.45,
            )
            self.assertEqual(
                c.load_profile.gas_allocation,
                0.55,
            )
        with self.subTest("Path 2 GHGW Partial"):
            input_data.update(
                {
                    "percent_improvement": 0.25,
                    "heating_therms": 0.9,
                    "hot_water_therms": 1.1,
                }
            )
            c = Allocation(**input_data)
            self.assertEqual(c.partial_territory, True)
            self.assertEqual(c.home_path, HomePath.PATH_2)
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
                32.0,
            )
            self.assertEqual(
                c.load_profile.electric_allocation,
                0.11,
            )
            self.assertEqual(
                c.load_profile.gas_allocation,
                0.89,
            )

    def test_full_allocation_data(self):
        opts = {
            "percent_improvement": 0.25,
            "heating_therms": 0.0,
            "hot_water_therms": 1.0,
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "gas_utility": GasUtility.NW_NATURAL,
            "builder_base_incentive": 100.0,
            "builder_additional_incentives": [IncentiveItem(incentive=50.0, label="Builder DEI")],
            "verifier_base_incentive": 25,
            "verifier_additional_incentives": [IncentiveItem(incentive=5.0, label="Verifier DEI")],
            "heat_type": HeatType.GAS,
        }
        data = Allocation(**opts)
        self.assertEqual(data.home_path, HomePath.PATH_2)
        self.assertEqual(data.sub_type, HomeSubType.EHGW)
        self.assertFalse(data.partial_territory)
        self.assertIn("Pacific Power  $ 69.00    $ 17.00", data.allocation_summary)
        self.assertIn("NW Natural     $ 81.00    $ 13.00", data.allocation_summary)
        self.assertIn("Total          $ 150.00   $ 30.00", data.allocation_summary)

    def test_partial_allocation_data(self):
        opts = {
            "percent_improvement": 0.25,
            "heating_therms": 1.0,
            "hot_water_therms": 0.0,
            "electric_utility": ElectricUtility.NONE,
            "gas_utility": GasUtility.NW_NATURAL,
            "builder_base_incentive": 100.0,
            "builder_additional_incentives": [IncentiveItem(incentive=50.0, label="Builder DEI")],
            "verifier_base_incentive": 25,
            "verifier_additional_incentives": [IncentiveItem(incentive=5.0, label="Verifier DEI")],
            "heat_type": HeatType.ELECTRIC,
        }
        data = Allocation(**opts)
        self.assertEqual(data.home_path, HomePath.PATH_2)
        self.assertEqual(data.sub_type, HomeSubType.GHEW)
        self.assertTrue(data.partial_territory)
        # I'm fairly certain this is wrong. If other should be zero who paying??
        self.assertIn("Other/None  $ 50.00    $ 5.00", data.allocation_summary)
        self.assertIn("NW Natural  $ 55.00    $ 25.00", data.allocation_summary)
        self.assertIn("Total       $ 105.00   $ 30.00", data.allocation_summary)

    def test_solar_allocation_data(self):
        opts = {
            "percent_improvement": 0.34,
            "heating_therms": 0.0,
            "hot_water_therms": 1.0,
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "gas_utility": GasUtility.NW_NATURAL,
            "builder_base_incentive": 100.0,
            "builder_additional_incentives": [IncentiveItem(incentive=50.0, label="Solar Ready")],
            "verifier_base_incentive": 25,
            "verifier_additional_incentives": [IncentiveItem(incentive=5.0, label="Solar Ready")],
            "heat_type": HeatType.GAS,
        }
        data = Allocation(**opts)
        self.assertEqual(data.home_path, HomePath.PATH_3)
        self.assertEqual(data.sub_type, HomeSubType.EHGW)
        self.assertFalse(data.partial_territory)
        self.assertIn("Solar          $ 50.00    $ 5.00", data.allocation_summary)
        self.assertIn("Total          $ 150.00   $ 30.00", data.allocation_summary)

    def test_full_with_solar_allocation_data(self):
        opts = {
            "percent_improvement": 0.2034845306192010,
            "heating_therms": 9.0,
            "hot_water_therms": 0.0,
            "electric_utility": ElectricUtility.PORTLAND_GENERAL,
            "gas_utility": GasUtility.CASCADE,
            "builder_base_incentive": 3596.03225807188000,
            "builder_additional_incentives": [
                IncentiveItem(
                    reported=True,
                    incentive=1000.0,
                    budget="SLE",
                    utility_allocation="SLE",
                    label="Net Zero",
                ),
                IncentiveItem(
                    reported=True,
                    incentive=200.0,
                    budget="SLE",
                    utility_allocation="SLE",
                    label="Solar Ready",
                ),
                IncentiveItem(
                    reported=True,
                    incentive=200.0,
                    budget="ENH",
                    utility_allocation="Ele",
                    label="ESH: Solar + Storage",
                ),
                IncentiveItem(
                    reported=True,
                    incentive=500.0,
                    budget="ENH",
                    utility_allocation="Ele",
                    label="Builder DEI",
                ),
                IncentiveItem(
                    reported=True,
                    incentive=200.0,
                    budget="ENH",
                    utility_allocation="Ele",
                    label="ESH: EV Ready",
                ),
                IncentiveItem(
                    reported=True,
                    incentive=-250.0,
                    budget="ENH",
                    utility_allocation="Allocation",
                    label="Heat Pump Water Heater",
                ),
                IncentiveItem(
                    reported=True,
                    incentive=750.0,
                    budget="ENH",
                    utility_allocation="Allocation",
                    label=" - Triple Pane Windows",
                ),
                IncentiveItem(
                    reported=True,
                    incentive=750.0,
                    budget="ENH",
                    utility_allocation="Allocation",
                    label=" - Exterior Rigid Insulation",
                ),
                IncentiveItem(
                    reported=True,
                    incentive=400.0,
                    budget="ENH",
                    utility_allocation="Allocation",
                    label=" - Sealed Attic",
                ),
            ],
            "verifier_base_incentive": 359.60322580718800,
            "verifier_additional_incentives": [
                IncentiveItem(
                    reported=True,
                    incentive=250.0,
                    budget="ENH",
                    utility_allocation="Allocation",
                    label="Verifier DEI",
                ),
                IncentiveItem(
                    reported=True,
                    incentive=50.0,
                    budget="SLE",
                    utility_allocation="SLE",
                    label="Solar Ready",
                ),
            ],
            "heat_type": HeatType.ELECTRIC,
        }
        data = Allocation(**opts)
        self.assertEqual(data.home_path, HomePath.PATH_2)
        self.assertEqual(data.sub_type, HomeSubType.GHEW)
        self.assertFalse(data.partial_territory)
        self.assertIn("Portland General  $ 4,675.00  $ 473.00", data.allocation_summary)
        self.assertIn("Cascade           $ 1,271.00  $ 137.00", data.allocation_summary)
        self.assertIn("Solar             $ 1,400.00  $ 50.00", data.allocation_summary)
        self.assertIn("Total             $ 7,346.00  $ 660.00", data.allocation_summary)
