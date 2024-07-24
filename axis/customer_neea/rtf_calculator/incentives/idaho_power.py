"""idaho_power.py: Django Idaho Power Incentives"""


import logging

from .base import BPAIncentivesCalculator

__author__ = "Steven K"
__date__ = "08/20/2019 08:33"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class IdahoPowerIncentivesCalculator(BPAIncentivesCalculator):
    """Idaho Power Incentive"""

    @property
    def incentive_paying_organization(self):
        return self.electric_utility

    def utility_report(self):
        """Utility Specifics"""
        data = ["", "Idaho Power Utility Considerations", ""]
        msg = "{:<15}{:<20}{:<20}{:<20}"
        data.append(
            msg.format("% Improvement", "Heating Fuel", "Heating Type", "Utility Incentive")
        )
        data.append(
            msg.format(
                self.round2p__percent_improvement,
                self.heating_fuel,
                self.heating_type,
                "Yes" if self.has_incentive else "No",
            )
        )
        return data

    @property
    def required_pct_improvement(self):
        """Required % improvement"""
        return 0.1

    @property
    def has_incentive(self):
        """Do we have an incentive"""
        if self.heating_fuel == "electric" and self.has_heat_pump:
            return self.percent_improvement >= self.required_pct_improvement
        return False

    @property
    def builder_incentive(self):
        """Amount paid by a utility to a builder"""
        if not self.has_incentive:
            return 0.0

        incentive_tiers = [
            {"condition": lambda x: 0.10 <= x < 0.15, "incentive": 1200.0},
            {"condition": lambda x: 0.15 < x < 0.2, "incentive": 1500.0},
            {"condition": lambda x: x >= 0.2, "incentive": 2000.0},
        ]

        for incentive_tier in incentive_tiers:
            if incentive_tier["condition"](self.percent_improvement):
                return incentive_tier["incentive"]

        return 0.0
