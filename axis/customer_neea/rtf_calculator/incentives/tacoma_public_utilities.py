"""tacoma_public_utilities.py: Django Tacoma Public Utilities Incentives"""


import logging

from .base import BPAIncentivesCalculator

__author__ = "Steven K"
__date__ = "04/21/2021 08:34"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class TacomaPowerIncentivesCalculator(BPAIncentivesCalculator):
    """Tacoma Public Utilities Incentives"""

    @property
    def incentive_paying_organization(self):
        return self.electric_utility

    def utility_report(self):
        """Utility Specifics"""
        data = ["", "Tacoma Public Utilities Considerations", ""]
        msg = "{:<15}{:<20}{:<20}{:<20}"
        data.append(msg.format("% Improvement", "Heating Fuel", "H20 Heater Type", "Incentive"))
        data.append(
            msg.format(
                self.round2p__percent_improvement,
                self.heating_fuel,
                self.water_heater_type,
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
        if self.heating_fuel == "electric" and self.water_heater_type != "gas":
            return self.percent_improvement >= self.required_pct_improvement
        return False

    @property
    def builder_incentive(self):
        """Amount paid by a utility to a builder"""
        if self.has_incentive:
            return 0.70 * self.total_kwh_savings
        return 0.0
