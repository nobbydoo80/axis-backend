"""clark.py: Django Clark County Incentives"""


import logging

from .base import BPAIncentivesCalculator

__author__ = "Steven K"
__date__ = "08/20/2019 08:33"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class ClarkIncentivesCalculator(BPAIncentivesCalculator):
    """Clark PUD Incentive Calculator"""

    @property
    def incentive_paying_organization(self):
        return self.electric_utility

    def utility_report(self):
        """Utility Specifics"""
        data = ["", "Clark Utility Considerations", ""]
        msg = "{:<15}{:<20}{:20}"
        data.append(msg.format("% Improvement", "Heating Fuel", "Utility Incentive"))
        data.append(
            msg.format(
                self.round2p__percent_improvement,
                self.heating_fuel,
                "Yes" if self.has_incentive else "No",
            )
        )
        return data

    @property
    def has_incentive(self):
        """Do we have an incentive"""
        if self.heating_fuel == "electric":
            return self.percent_improvement >= self.required_pct_improvement
        elif self.heating_fuel == "gas":
            if self.gas_utility == "nw-natural-gas":
                return self.percent_improvement >= self.required_pct_improvement
        return False

    @property
    def builder_incentive(self):
        """Amount paid by a utility to a builder"""
        if self.has_incentive:
            incentive = super(ClarkIncentivesCalculator, self).total_incentive
            if self.heating_fuel == "electric" and self.percent_improvement >= 0.30:
                incentive += 500.00
            return incentive
        return 0.0
