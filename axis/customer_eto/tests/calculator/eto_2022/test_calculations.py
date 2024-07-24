"""test_calculations.py - Axis"""

__author__ = "Steven K"
__date__ = "3/4/22 13:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from django.test import TestCase

from axis.customer_eto.calculator.eps_2022.calculations import Calculations
from axis.customer_eto.enumerations import HeatType

log = logging.getLogger(__name__)


class EPS2022CalculationTests(TestCase):
    @property
    def input_options(self):
        return {
            "heat_type": HeatType.GAS,
            "code_heating_therms": 1,
            "code_heating_kwh": 3,
            "code_cooling_kwh": 5,
            "code_hot_water_therms": 7,
            "code_hot_water_kwh": 9,
            "code_lights_and_appliance_therms": 11,
            "code_lights_and_appliance_kwh": 13,
            "improved_heating_therms": 2,
            "improved_heating_kwh": 4,
            "improved_cooling_kwh": 6,
            "improved_hot_water_therms": 8,
            "improved_hot_water_kwh": 10,
            "improved_lights_and_appliance_therms": 12,
            "improved_lights_and_appliance_kwh": 14,
            "improved_pv_kwh": 15,
        }.copy()

    def test_gas_basics(self):
        data = Calculations(**self.input_options)
        # print(data.consumption_report)
        # Code
        self.assertIn(
            "Total MMBTU (EPS)                   2.00        2.07             2.10",
            data.consumption_report,
        )
        # Improved
        self.assertIn(
            "Total MMBTU (EPS)                   2.26        2.34             2.33",
            data.consumption_report,
        )
        self.assertEqual(data.eps_score, 2)
        self.assertEqual(data.code_eps_score, 2)

    def test_electric_basics(self):
        opts = self.input_options
        opts["heat_type"] = HeatType.ELECTRIC
        data = Calculations(**self.input_options)
        # Code
        self.assertIn(
            "Total MMBTU (EPS)                   2.00        2.07             2.10",
            data.consumption_report,
        )
        # Improved
        self.assertIn(
            "Total MMBTU (EPS)                   2.26        2.34             2.33",
            data.consumption_report,
        )
        self.assertEqual(data.eps_score, 2)
        self.assertEqual(data.code_eps_score, 2)
