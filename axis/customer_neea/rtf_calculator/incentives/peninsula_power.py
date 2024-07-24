"""peninsula_power.py - Axis"""

__author__ = "Steven K"
__date__ = "8/2/21 10:48"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from .base import BPAIncentivesCalculator
from ..constants.default import HPWH_TIER_3

log = logging.getLogger(__name__)


class PeninsulaPowerIncentivesCalculator(BPAIncentivesCalculator):
    """Peninsula Power & Light Incentive Calculator"""

    @property
    def incentive_paying_organization(self):
        return self.electric_utility

    def utility_report(self):
        """Utility Specifics"""
        data = ["", "Peninsula Power & Light Considerations", ""]
        msg = "{:<15}{:<15}{:<15}{:10}"
        data.append(
            msg.format(
                "% Improvement",
                "Heating",
                "Meter No",
                "Incentive",
            )
        )
        data.append(
            msg.format(
                self.round2p__percent_improvement,
                self.heating_fuel.capitalize(),
                self.electric_meter_number if self.electric_meter_number else "Missing",
                "Yes" if self.has_incentive else "No",
            )
        )
        return data

    @property
    def has_incentive(self):
        """Do we have an incentive"""
        correct_heating_type = self.heating_fuel == "electric"
        correct_electric_meter = self.electric_meter_number and len(self.electric_meter_number)

        if all(
            [
                correct_heating_type,
                correct_electric_meter,
            ]
        ):
            return self.percent_improvement >= self.required_pct_improvement
        return False

    @property
    def builder_incentive(self):
        """Amount paid by a utility to a builder"""
        if self.has_incentive:
            return self.total_incentive
        return 0.0
