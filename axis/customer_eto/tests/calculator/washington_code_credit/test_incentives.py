"""incentives.py - Axis"""

__author__ = "Steven K"
__date__ = "8/15/21 09:31"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from django.test import TestCase

from ....calculator.washington_code_credit.constants.defaults import (
    THERMOSTAT_INCENTIVE_VALUE,
    FIREPLACE_INCENTIVE_VALUE,
    CEC_THERM_SAVINGS_MULTIPLIER,
)
from ....calculator.washington_code_credit.incentives import Incentives
from ....calculator.washington_code_credit.savings import Savings

from ....eep_programs.washington_code_credit import (
    ThermostatType,
    FireplaceType,
)

log = logging.getLogger(__name__)


class WashingtonCodeCreditCalculatorIncentiveTests(TestCase):
    @property
    def input_options(self):
        return {
            "eligible_gas_points": 1,
            "thermostat_type": ThermostatType.PROGRAMABLE,
            "fireplace_efficiency": FireplaceType.FP_70_75,
        }

    def test_thermostat_incentive(self):
        data = self.input_options
        data["fireplace_efficiency"] = FireplaceType.NONE
        data["eligible_gas_points"] = 1
        for label, option in ThermostatType.__members__.items():
            data["thermostat_type"] = option
            incentives = Incentives(**data)
            self.assertIsInstance(incentives.incentive_data, dict)
            self.assertIsNotNone(incentives.incentive_report)
            with self.subTest(f"Thermostat Option - {label}"):
                target_value = THERMOSTAT_INCENTIVE_VALUE
                total_value = 1600 + target_value
                if str(label) in ["OTHER", "PROGRAMABLE", "PROGRAMABLE_WIFI"]:
                    target_value = 0.0
                    total_value = 1600
                self.assertEqual(incentives.thermostat_incentive, target_value)
                self.assertEqual(incentives.incentive_data["thermostat_incentive"], target_value)
                self.assertEqual(incentives.total_builder_incentive, total_value)
                self.assertEqual(incentives.incentive_data["total_builder_incentive"], total_value)
                if total_value:
                    self.assertEqual(incentives.incentive_data["verifier_incentive"], 100)
                    self.assertEqual(incentives.verifier_incentive, 100)

    def test_fireplace_incentive(self):
        data = self.input_options
        data["thermostat_type"] = ThermostatType.PROGRAMABLE
        data["eligible_gas_points"] = 1

        for label, option in FireplaceType.__members__.items():
            data["fireplace_efficiency"] = option
            incentives = Incentives(**data)
            self.assertIsInstance(incentives.incentive_data, dict)
            self.assertIsNotNone(incentives.incentive_report)
            with self.subTest(f"Fireplace Option - {label}"):
                target_value = FIREPLACE_INCENTIVE_VALUE
                total_value = 1600 + target_value
                if str(label) in ["NONE", "FP_LT70"]:
                    target_value = 0.0
                    total_value = 1600
                self.assertEqual(incentives.fireplace_incentive, target_value)
                self.assertEqual(incentives.incentive_data["fireplace_incentive"], target_value)
                self.assertEqual(incentives.total_builder_incentive, total_value)
                self.assertEqual(incentives.incentive_data["total_builder_incentive"], total_value)
                if total_value:
                    self.assertEqual(incentives.incentive_data["verifier_incentive"], 100)
                    self.assertEqual(incentives.verifier_incentive, 100)

        data = self.input_options
        data["eligible_gas_points"] = 0
        with self.subTest(f"Fireplace Option - No Gas Points"):
            incentives = Incentives(**data)
            self.assertIsInstance(incentives.incentive_data, dict)
            self.assertIsNotNone(incentives.incentive_report)
            self.assertEqual(incentives.fireplace_incentive, 0.0)
            self.assertEqual(incentives.incentive_data["fireplace_incentive"], 0.0)

    def test_code_credit_incentive(self):
        data = self.input_options
        expected = {
            0: 0,
            0.5: 800,
            1: 1600,
            6.5: 10400,
        }
        data["eligible_gas_points"] = 0
        data["thermostat_type"] = ThermostatType.PROGRAMABLE
        data["fireplace_efficiency"] = FireplaceType.NONE
        for gas_point, target in expected.items():
            data["eligible_gas_points"] = gas_point
            with self.subTest(f"Gas Code Credit Points {gas_point}"):
                incentives = Incentives(**data)
                self.assertIsInstance(incentives.incentive_data, dict)
                self.assertIsNotNone(incentives.incentive_report)
                self.assertEqual(incentives.fireplace_incentive, 0.0)
                self.assertEqual(incentives.incentive_data["fireplace_incentive"], 0.0)
                self.assertEqual(incentives.thermostat_incentive, 0.0)
                self.assertEqual(incentives.incentive_data["thermostat_incentive"], 0.0)
                self.assertEqual(incentives.total_builder_incentive, target)
                self.assertEqual(incentives.incentive_data["total_builder_incentive"], target)
                if target:
                    self.assertEqual(incentives.incentive_data["verifier_incentive"], 100)
                    self.assertEqual(incentives.verifier_incentive, 100)
                else:
                    self.assertEqual(incentives.incentive_data["verifier_incentive"], 0)
                    self.assertEqual(incentives.verifier_incentive, 0)


class WashingtonCodeCreditCalculatorSavingsTests(TestCase):
    @property
    def input_options(self):
        return {
            "eligible_gas_points": 0,
            "thermostat_incentive": 0,
            "fireplace_incentive": 0,
        }

    def test_code_based_therm_savings(self):
        data = self.input_options
        expected = {
            0: 0,
            0.5: 34.2783728876166,
            1: 68.5567457752332,
            6.5: 445.61884753901575,
        }
        for gas_point, target in expected.items():
            data["eligible_gas_points"] = gas_point
            with self.subTest(f"Gas Code Credit Points {gas_point}"):
                savings = Savings(**data)
                self.assertIsInstance(savings.savings_data, dict)
                self.assertIsNotNone(savings.savings_report)
                self.assertEqual(savings.thermostat_therm_savings, 0.0)
                self.assertEqual(savings.savings_data["thermostat_therm_savings"], 0.0)
                self.assertEqual(savings.fireplace_therm_savings, 0.0)
                self.assertEqual(savings.savings_data["fireplace_therm_savings"], 0.0)

                self.assertEqual(savings.code_based_therm_savings, target)
                self.assertEqual(savings.savings_data["code_based_therm_savings"], target)
                self.assertEqual(savings.total_therm_savings, target)
                self.assertEqual(savings.savings_data["total_therm_savings"], target)

    def test_thermostat_code_savings(self):
        data = self.input_options
        expected = {
            0: 0,
            0.5: 336 * 0.06,
            1: 336 * 0.06,
            125: 336 * 0.06,
        }
        for tstat_incentive, target in expected.items():
            data["eligible_gas_points"] = 0.5
            data["thermostat_incentive"] = tstat_incentive
            with self.subTest(f"Thermostat Savings {tstat_incentive}"):
                savings = Savings(**data)
                self.assertIsInstance(savings.savings_data, dict)
                self.assertIsNotNone(savings.savings_report)
                self.assertEqual(savings.fireplace_therm_savings, 0.0)
                self.assertEqual(savings.savings_data["fireplace_therm_savings"], 0.0)

                self.assertEqual(savings.code_based_therm_savings, CEC_THERM_SAVINGS_MULTIPLIER)
                self.assertEqual(
                    savings.savings_data["code_based_therm_savings"], CEC_THERM_SAVINGS_MULTIPLIER
                )

                self.assertEqual(savings.thermostat_therm_savings, target)
                self.assertEqual(savings.savings_data["thermostat_therm_savings"], target)
                self.assertEqual(savings.total_therm_savings, target + CEC_THERM_SAVINGS_MULTIPLIER)
                self.assertEqual(
                    savings.savings_data["total_therm_savings"],
                    target + CEC_THERM_SAVINGS_MULTIPLIER,
                )

    def test_fireplace_therm_savings(self):
        data = self.input_options
        expected = {
            0: 0,
            0.5: 18.3,
            1: 18.3,
            200: 18.3,
        }
        for fplace_incentive, target in expected.items():
            data["eligible_gas_points"] = 0.5
            data["fireplace_incentive"] = fplace_incentive
            with self.subTest(f"Fireplace Savings {fplace_incentive}"):
                savings = Savings(**data)
                self.assertIsInstance(savings.savings_data, dict)
                self.assertIsNotNone(savings.savings_report)

                self.assertEqual(savings.thermostat_therm_savings, 0.0)
                self.assertEqual(savings.savings_data["thermostat_therm_savings"], 0.0)

                self.assertEqual(savings.code_based_therm_savings, CEC_THERM_SAVINGS_MULTIPLIER)
                self.assertEqual(
                    savings.savings_data["code_based_therm_savings"], CEC_THERM_SAVINGS_MULTIPLIER
                )

                self.assertEqual(savings.fireplace_therm_savings, target)
                self.assertEqual(savings.savings_data["fireplace_therm_savings"], target)
                self.assertEqual(savings.total_therm_savings, target + CEC_THERM_SAVINGS_MULTIPLIER)
                self.assertEqual(
                    savings.savings_data["total_therm_savings"],
                    target + CEC_THERM_SAVINGS_MULTIPLIER,
                )
