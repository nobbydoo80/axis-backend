"""incentives.py - Axis"""

__author__ = "Steven K"
__date__ = "8/13/21 16:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from functools import cached_property
from tabulate import tabulate

from axis.customer_eto.eep_programs.washington_code_credit import ThermostatType, FireplaceType

log = logging.getLogger(__name__)


class Incentives:
    def __init__(self, eligible_gas_points, thermostat_type, fireplace_efficiency):
        self.eligible_gas_points = eligible_gas_points
        self.thermostat_type = thermostat_type
        self.fireplace_efficiency = fireplace_efficiency

    @cached_property
    def constants(self):
        from .constants import defaults

        return defaults

    @cached_property
    def code_credit_incentive(self):
        """
        =(C13*2)*Reference!C8
        :return:
        """
        return (self.eligible_gas_points * 2) * self.constants.INCENTIVE_PER_CODE_CREDIT_MULTIPLIER

    @cached_property
    def thermostat_incentive(self):
        """
        =IF(
            OR(
                'Step 2 - Select Code Credits'!C8:D8=Reference!N3,
                'Step 2 - Select Code Credits'!C8:D8=Reference!N4,
                'Step 2 - Select Code Credits'!C8:D8=Reference!N5,
                'Step 2 - Select Code Credits'!C8:D8=Reference!N14,
                C19=0
               )
            ,0,
            Reference!C9
            )

        :return:
        """
        if (
            self.thermostat_type
            in [
                ThermostatType.PROGRAMABLE,
                ThermostatType.PROGRAMABLE_WIFI,
                ThermostatType.OTHER,
                None,
            ]
            or self.code_credit_incentive <= 0.0
        ):
            return 0.0
        return self.constants.THERMOSTAT_INCENTIVE_VALUE

    @cached_property
    def fireplace_incentive(self):
        """
        =IF(
            OR(
                'Step 2 - Select Code Credits'!C9:D9=Reference!O3,
                C9=Reference!O4,
                C9=Reference!O5,
                C19=0),
            0,
            Reference!C10)

        """
        if not self.eligible_gas_points:
            return 0.0
        if (
            self.fireplace_efficiency
            in [
                FireplaceType.FP_70_75,
                FireplaceType.FP_GT75,
            ]
            and self.code_credit_incentive > 0.0
        ):
            return self.constants.FIREPLACE_INCENTIVE_VALUE
        return 0.0

    @cached_property
    def total_builder_incentive(self):
        return sum(
            [self.code_credit_incentive, self.thermostat_incentive, self.fireplace_incentive]
        )

    @cached_property
    def verifier_incentive(self):
        if self.total_builder_incentive:
            return self.constants.VERIFIER_INCENTIVE_VALUE
        return 0.00

    @cached_property
    def incentive_data(self):
        return {
            "code_credit_incentive": self.code_credit_incentive,
            "thermostat_incentive": self.thermostat_incentive,
            "fireplace_incentive": self.fireplace_incentive,
            "total_builder_incentive": self.total_builder_incentive,
            "verifier_incentive": self.verifier_incentive,
        }

    @cached_property
    def incentive_report(self):
        table = [
            (
                label.replace("_", " ").capitalize(),
                f"$ {round(item, 2):>4.2f}",
            )
            for label, item in self.incentive_data.items()
        ]
        return tabulate(table, headers=["Incentive Category", "Amount"])
