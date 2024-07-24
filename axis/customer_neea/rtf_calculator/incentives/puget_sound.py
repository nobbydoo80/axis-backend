"""puget_sound.py: Django Puget Sound Incentives"""


import logging
from functools import cached_property

from tabulate import tabulate

from .base import BPAIncentivesCalculator

__author__ = "Steven K"
__date__ = "08/20/2019 08:34"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class PugetIncentivesCalculator(BPAIncentivesCalculator):
    """Puget Sound Electric Incentive"""

    @cached_property
    def incentive_paying_organization(self):
        return "puget-sound-energy"

    def utility_report(self):
        """Utility Specifics"""
        data = "Puget Sound Utility Considerations\n"
        data += tabulate(
            [
                [
                    self.round2p__percent_improvement,
                    self.electric_utility,
                    self.gas_utility,
                    self.heating_fuel,
                    self.total_therm_savings,
                    "Yes" if self.has_incentive else "No",
                ]
            ],
            headers=[
                "% Improvement",
                "Electric Utility",
                "Gas Utility",
                "Heating Fuel",
                "Therm Savings",
                "Utility Incentive",
            ],
            floatfmt=".2f",
        )
        return data.split("\n")

    @cached_property
    def required_pct_improvement(self):
        """Required % improvement"""
        return 0.0

    @cached_property
    def has_incentive(self):
        """Do we have an incentive"""
        if self.heating_fuel == "electric":
            return self.electric_utility == "puget-sound-energy"
        elif self.heating_fuel == "gas":
            return all(
                [
                    self.electric_utility == "puget-sound-energy",
                    self.gas_utility == "puget-sound-energy",
                ]
            )
        return False

    @cached_property
    def has_bpa_incentive(self):
        return self.has_incentive

    @cached_property
    def builder_incentive(self):
        """Amount paid by a utility to a builder"""
        if self.has_incentive:
            if self.heating_fuel == "electric":
                # We don't ever want to give out more than the stock BPA incentive.
                return self.round_value(
                    max(
                        [
                            min(
                                [
                                    self.lighting_kwh_incentive
                                    + self.appliance_kwh_incentive
                                    + self.windows_shell_kwh_incentive
                                    + self.smart_thermostat_kwh_incentive
                                    + self.showerhead_kwh_incentive,
                                    self.total_incentive,
                                ]
                            ),
                            0,
                        ]
                    ),
                    2,
                )
            elif self.heating_fuel == "gas":
                return max([5.0 * self.total_therm_savings, 0])
        return 0.0
