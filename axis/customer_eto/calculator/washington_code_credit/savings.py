"""savings.py - Axis"""

__author__ = "Steven K"
__date__ = "8/13/21 15:41"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from functools import cached_property
from tabulate import tabulate

log = logging.getLogger(__name__)


class Savings:
    def __init__(self, eligible_gas_points, thermostat_incentive, fireplace_incentive):
        self.eligible_gas_points = eligible_gas_points
        self.thermostat_incentive = thermostat_incentive
        self.fireplace_incentive = fireplace_incentive

    @cached_property
    def constants(self):
        from .constants import defaults

        return defaults

    @cached_property
    def code_based_therm_savings(self):
        return (self.constants.CEC_THERM_SAVINGS_MULTIPLIER * self.eligible_gas_points) / 0.5

    @cached_property
    def thermostat_therm_savings(self):
        if self.thermostat_incentive <= 0 or self.eligible_gas_points <= 0.0:
            return 0.0
        return 336 * 0.06

    @cached_property
    def fireplace_therm_savings(self):
        if self.fireplace_incentive <= 0 or self.eligible_gas_points <= 0.0:
            return 0.0
        return 18.3

    @cached_property
    def total_therm_savings(self):
        return sum(
            [
                self.code_based_therm_savings,
                self.thermostat_therm_savings,
                self.fireplace_therm_savings,
            ]
        )

    @cached_property
    def savings_data(self):
        return {
            "eligible_gas_points": self.eligible_gas_points,
            "code_based_therm_savings": self.code_based_therm_savings,
            "thermostat_therm_savings": self.thermostat_therm_savings,
            "fireplace_therm_savings": self.fireplace_therm_savings,
            "total_therm_savings": self.total_therm_savings,
        }

    @cached_property
    def savings_report(self):
        table = [
            (
                label.replace("_", " ").capitalize(),
                round(item, 2),
                "Points" if label == "eligible_gas_points" else "Therms",
            )
            for label, item in self.savings_data.items()
        ]
        return tabulate(table, headers=["Savings Category", "Eligible Credits", "Achieved credits"])
