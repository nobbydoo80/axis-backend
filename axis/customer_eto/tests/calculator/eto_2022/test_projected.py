"""test_projected.py - Axis"""

__author__ = "Steven K"
__date__ = "3/4/22 14:49"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from django.test import TestCase

from axis.customer_eto.calculator.eps_2022.projected import Projected
from axis.customer_eto.enumerations import ElectricUtility, GasUtility, ClimateLocation, HeatType

log = logging.getLogger(__name__)


class EPS2022ProjectedTests(TestCase):
    @property
    def input_options(self):
        return {
            "climate_location": ClimateLocation.PORTLAND,
            "heat_type": HeatType.GAS,
            "conditioned_area": 2500.0,
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "gas_utility": GasUtility.NW_NATURAL,
        }.copy()

    def test_simplified_locations(self):
        opts = self.input_options
        with self.subTest("Redmond"):
            for cl in [ClimateLocation.BURNS, ClimateLocation.PENDLETON, ClimateLocation.REDMOND]:
                opts["climate_location"] = cl
                data = Projected(**opts)
                self.assertEqual(data.simplified_location, ClimateLocation.REDMOND)

        with self.subTest("PORTLAND"):
            for cl in [
                ClimateLocation.ASTORIA,
                ClimateLocation.EUGENE,
                ClimateLocation.NORTH_BEND,
                ClimateLocation.PORTLAND,
                ClimateLocation.SALEM,
            ]:
                opts["climate_location"] = cl
                data = Projected(**opts)
                self.assertEqual(data.simplified_location, ClimateLocation.PORTLAND)

        with self.subTest("MEDFORD"):
            for cl in [ClimateLocation.MEDFORD]:
                opts["climate_location"] = cl
                data = Projected(**opts)
                self.assertEqual(data.simplified_location, ClimateLocation.MEDFORD)

    def test_projected_energy_consumption(self):
        opts = self.input_options

        with self.subTest("Portland Gas Heat"):
            opts.update({"heat_type": HeatType.GAS, "climate_location": ClimateLocation.PORTLAND})
            data = Projected(**opts)
            self.assertAlmostEqual(data.similar_size_eps, 121, 2)
        with self.subTest("Portland Electric Heat"):
            opts.update(
                {"heat_type": HeatType.ELECTRIC, "climate_location": ClimateLocation.PORTLAND}
            )
            data = Projected(**opts)
            self.assertAlmostEqual(data.similar_size_eps, 128, 2)

        with self.subTest("Medford Gas Heat"):
            opts.update({"heat_type": HeatType.GAS, "climate_location": ClimateLocation.MEDFORD})
            data = Projected(**opts)
            self.assertAlmostEqual(data.similar_size_eps, 121, 2)
        with self.subTest("Medford Electric Heat"):
            opts.update(
                {"heat_type": HeatType.ELECTRIC, "climate_location": ClimateLocation.MEDFORD}
            )
            data = Projected(**opts)
            self.assertAlmostEqual(data.similar_size_eps, 137, 2)

        with self.subTest("Redmond Gas Heat"):
            opts.update({"heat_type": HeatType.GAS, "climate_location": ClimateLocation.REDMOND})
            data = Projected(**opts)
            self.assertAlmostEqual(data.similar_size_eps, 130, 2)
        with self.subTest("Redmond Electric Heat"):
            opts.update(
                {"heat_type": HeatType.ELECTRIC, "climate_location": ClimateLocation.REDMOND}
            )
            data = Projected(**opts)
            self.assertAlmostEqual(data.similar_size_eps, 151, 2)
