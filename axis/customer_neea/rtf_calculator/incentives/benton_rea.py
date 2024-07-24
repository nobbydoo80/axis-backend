"""benton_rea.py: Django Benton REA Incentives"""


import logging

from .base import BPAIncentivesCalculator

__author__ = "Steven K"
__date__ = "08/20/2019 08:31"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class BentonREAIncentivesCalculator(BPAIncentivesCalculator):
    """Benton REA Incentive"""

    @property
    def incentive_paying_organization(self):
        return self.electric_utility

    def utility_report(self):
        """Utility Specifics"""
        data = ["", "Benton REA Considerations", ""]
        msg = "{:<15}{:<10}"
        data.append(msg.format("% Improvement", "Heating Fuel"))
        data.append(msg.format(self.round2p__percent_improvement, self.heating_fuel))
        return data

    @property
    def has_incentive(self):
        """Do we have an incentive"""
        if self.heating_fuel == "electric":
            return self.percent_improvement >= self.required_pct_improvement
        return False

    @property
    def builder_incentive(self):
        """Amount paid by a utility to a builder"""
        if self.has_incentive:
            return super(BentonREAIncentivesCalculator, self).total_incentive
        return 0.0
