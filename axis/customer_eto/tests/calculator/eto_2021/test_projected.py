"""test_projected.py - Axis"""

__author__ = "Steven K"
__date__ = "9/16/21 15:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from django.test import TestCase

from axis.customer_eto.calculator.eps_2021.base import round_value
from axis.customer_eto.calculator.eps_2021.constants import Constants
from axis.customer_eto.calculator.eps_2021.projected import Projected2021
from axis.customer_eto.enumerations import (
    ClimateLocation,
    HeatType,
    ElectricUtility,
    GasUtility,
    PNWUSStates,
)

log = logging.getLogger(__name__)


class ProjectedTests(TestCase):
    @property
    def input_data(self) -> dict:
        return {
            "climate_location": ClimateLocation.PORTLAND,
            "heat_type": HeatType.GAS,
            "conditioned_area": 2500.0,
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "gas_utility": GasUtility.NW_NATURAL,
            "constants": Constants(ElectricUtility.PACIFIC_POWER, PNWUSStates.OR),
        }

    def test_projected_energy_consumption(self):
        input = self.input_data.copy()

        with self.subTest("Portland Gas Heat"):
            input.update({"heat_type": HeatType.GAS, "climate_location": ClimateLocation.PORTLAND})
            data = Projected2021(**input)
            self.assertEqual(round(data.similar_size_eps, 2), 121.02)
            self.assertEqual(round(data.similar_size_carbon, 2), 10.77)
            self.assertIn(
                f"{data.similar_size_eps:.{round_value}f}", data.projected_consumption_report
            )
            self.assertIn(
                f"{data.similar_size_carbon:.{round_value}f}", data.projected_consumption_report
            )

        with self.subTest("Portland Electric Heat"):
            input.update(
                {"heat_type": HeatType.ELECTRIC, "climate_location": ClimateLocation.PORTLAND}
            )
            data = Projected2021(**input)
            self.assertEqual(round(data.similar_size_eps, 2), 127.51)
            self.assertEqual(round(data.similar_size_carbon, 2), 11.27)
            self.assertIn(
                f"{data.similar_size_eps:.{round_value}f}", data.projected_consumption_report
            )
            self.assertIn(
                f"{data.similar_size_carbon:.{round_value}f}", data.projected_consumption_report
            )

        with self.subTest("Medford Gas Heat"):
            input.update({"heat_type": HeatType.GAS, "climate_location": ClimateLocation.MEDFORD})
            data = Projected2021(**input)
            self.assertEqual(round(data.similar_size_eps, 2), 121.02)
            self.assertEqual(round(data.similar_size_carbon, 2), 10.77)
            self.assertIn(
                f"{data.similar_size_eps:.{round_value}f}", data.projected_consumption_report
            )
            self.assertIn(
                f"{data.similar_size_carbon:.{round_value}f}", data.projected_consumption_report
            )

        with self.subTest("Medford Electric Heat"):
            input.update(
                {"heat_type": HeatType.ELECTRIC, "climate_location": ClimateLocation.MEDFORD}
            )
            data = Projected2021(**input)
            self.assertEqual(round(data.similar_size_eps, 2), 137.02)
            self.assertEqual(round(data.similar_size_carbon, 2), 12.99)
            self.assertIn(
                f"{data.similar_size_eps:.{round_value}f}", data.projected_consumption_report
            )
            self.assertIn(
                f"{data.similar_size_carbon:.{round_value}f}", data.projected_consumption_report
            )

        with self.subTest("Redmond Gas Heat"):
            input.update({"heat_type": HeatType.GAS, "climate_location": ClimateLocation.REDMOND})
            data = Projected2021(**input)
            self.assertEqual(round(data.similar_size_eps, 2), 130.44)
            self.assertEqual(round(data.similar_size_carbon, 2), 11.30)
            self.assertIn(
                f"{data.similar_size_eps:.{round_value}f}", data.projected_consumption_report
            )
            self.assertIn(
                f"{data.similar_size_carbon:.{round_value}f}", data.projected_consumption_report
            )

        with self.subTest("Redmond Electric Heat"):
            input.update(
                {"heat_type": HeatType.ELECTRIC, "climate_location": ClimateLocation.REDMOND}
            )
            data = Projected2021(**input)
            self.assertEqual(round(data.similar_size_eps, 2), 150.88)
            self.assertEqual(round(data.similar_size_carbon, 2), 12.86)
            self.assertIn(
                f"{data.similar_size_eps:.{round_value}f}", data.projected_consumption_report
            )
            self.assertIn(
                f"{data.similar_size_carbon:.{round_value}f}", data.projected_consumption_report
            )
        # print(data.projected_consumption_report)
