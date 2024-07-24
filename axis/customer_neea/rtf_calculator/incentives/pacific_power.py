"""pacific_power.py: Django Pacific Power Incentives"""


import logging

from .base import BPAIncentivesCalculator

__author__ = "Steven K"
__date__ = "08/20/2019 08:33"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class PacificPowerIncentivesCalculator(BPAIncentivesCalculator):
    """Pacific Power Incentive"""

    @property
    def incentive_paying_organization(self):
        return self.electric_utility

    def utility_report(self):
        """Utility Specifics"""
        data = ["", "Pacific Power Utility Considerations", ""]
        msg = "{!s:<15}{!s:<20}{!s:<20}{!s:<20}{!s:<20}"
        data.append(msg.format("% Improvement", "State", "Heating Fuel", "Heating Type", "DWH"))
        data.append(
            msg.format(
                self.round2p__percent_improvement,
                self.us_state,
                self.heating_fuel,
                self.heating_type,
                self.water_heater_type,
            )
        )
        data.append("")
        data.append(
            msg.format("Gas Utility", "Cooling Type", "Cooling Fuel", "Utility Incentive", "")
        )
        data.append(
            msg.format(
                self.gas_utility,
                self.cooling_type,
                self.cooling_fuel,
                "Yes" if self.has_incentive else "No",
                "",
            )
        )
        return data

    @property
    def has_incentive(self):  # pylint: disable=too-many-return-statements
        """Do we have an incentive"""
        if self.us_state.lower() != "wa" or self.water_heater_type == "gas":
            return False

        if self.heating_fuel == "electric":
            return True
        elif self.heating_fuel == "gas" and self.gas_utility == "cascade-gas":
            if self.cooling_type is None or self.cooling_fuel.lower() != "electric":
                return False
            if self.percent_improvement < self.required_pct_improvement:
                return False
            return True
        return False

    @property
    def builder_incentive(self):
        """Amount paid by a utility to a builder"""
        if self.has_incentive:
            if self.heating_fuel == "electric":
                if self.percent_improvement < 0.20:
                    if self.percent_improvement < 0.10:
                        return max([0.0, round(self.total_kwh_savings * 0.5, 2)])
                    return 1875.00
                return 3125.00
            return 625.00
        return 0.00
