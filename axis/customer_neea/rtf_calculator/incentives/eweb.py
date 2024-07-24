"""eweb.py - Axis"""

import logging

from .base import BPAIncentivesCalculator

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "5/3/21 11:55"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


class EWEBCalculator(BPAIncentivesCalculator):
    """Eugene Water & Electric Board Incentive Calculator"""

    def utility_report(self):
        """Utility Specifics"""
        data = ["", " Eugene Water & Electric Board Considerations", ""]

        msg = "{:<12}{:<24}{:<14}{:<12}{:<12}{:12}"

        data.append(
            msg.format(
                "% Improv",
                "Heating Type",
                "Heating Fuel",
                "H20 Heater",
                "EA Cert",
                "Utility Incentive",
            )
        )
        ea = self.earth_advantage_certified if self.earth_advantage_certified else "No"
        data.append(
            msg.format(
                self.round2p__percent_improvement,
                self.heating_type,
                self.heating_fuel,
                self.water_heater_type,
                ea,
                "Yes" if self.has_incentive else "No",
            )
        )
        return data

    @property
    def has_incentive(self):
        """Do we have an incentive"""
        return (
            self.electric_utility == "utility-eugene-water-electric-board"
            and self.heating_fuel == "electric"
            and self.water_heater_type != "gas"
            and self.percent_improvement >= self.required_pct_improvement
            and self.earth_advantage_certified is not None
        )

    @property
    def builder_incentive(self):
        """Amount paid by a utility to a builder"""
        if self.has_incentive:
            base_incentive = super(EWEBCalculator, self).total_incentive
            secondary_tier = 0.0
            if self.has_heat_pump:
                secondary_tier += 1000.00
            if self.water_heater_type.lower() == "hpwh":
                secondary_tier += 800.00
            return max([base_incentive, secondary_tier])
        return 0.0
