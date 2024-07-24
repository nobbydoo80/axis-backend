"""inland_power.py: Django Inland Power Incentives"""


import logging

from .base import BPAIncentivesCalculator

__author__ = "Steven K"
__date__ = "08/20/2019 09:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class InlandPowerCalculator(BPAIncentivesCalculator):
    """Inland Power Incentive"""

    @property
    def incentive_paying_organization(self):
        return self.electric_utility

    def utility_report(self):
        """Utility Specifics"""
        data = ["", "Inland Power Considerations", ""]
        msg = "{!s:<15}{!s:<20}{!s:<20}{!s:<20}"
        data.append(
            msg.format("% Improvement", "Heating Fuel", "Utility Incentive", "Water Heater Type")
        )
        data.append(
            msg.format(
                self.round2p__percent_improvement,
                self.heating_fuel,
                "Yes" if self.has_incentive else "No",
                "Gas" if self.water_heater_type == "gas" else "Electric",
            )
        )

        return data

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
            return super(InlandPowerCalculator, self).total_incentive
        return 0.0
