"""eto_2018.py: Django ETO EPS Calculator Incentives"""


import logging

from .eto_2017 import Incentives2017

__author__ = "Steven K"
__date__ = "08/21/2019 08:08"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class Incentives2018(Incentives2017):
    """Incentives for 2018"""

    @property
    def home_path(self):
        """
            =IF(AND(D18>=0.08,D18<E23),D22,
              IF(AND(D18>=E23,D18<E24),D23,
              IF(AND(D18>=E24,D18<E25),D24,
              IF(AND(ISNUMBER(D18),D18>=E25),D25,
              "-"))))

        :return:
        """
        if 0.08 <= self.percentage_improvement < 0.20:
            return "Path 1"
        elif 0.20 <= self.percentage_improvement < 0.30:
            return "Path 2"
        elif 0.30 <= self.percentage_improvement < 0.40:
            return "Path 3"
        elif self.percentage_improvement > 0.40:
            return "Path 4"
        log.info("Unknown path due to pct improvement of %f", self.percentage_improvement)
        return "N/A"

    def _report_incentive_table(self):
        _eq = self.constants.EPS_OR_POLY if self.us_state == "OR" else self.constants.EPS_WA_POLY
        return "y = {second_order}x^2 + {first_order}x + {scaler}".format(**_eq)

    @property
    def full_territory_builder_incentive(self):
        """OR = =MIN(4723,IF($D$18>=0.08,(36354*($D$18^2))-(4510.2*$D$18)+710.5,0))"""
        if not isinstance(self.percentage_improvement, (float, int)):
            return "-"

        _eq = self.constants.EPS_OR_POLY if self.us_state == "OR" else self.constants.EPS_WA_POLY

        if self.us_state == "WA":
            if self.gas_utility != "nw natural" or self.heat_type == "heat pump":
                return 0.0

            if self.percentage_improvement < 0.10:
                return 0.0

        else:
            if self.percentage_improvement < 0.08:
                return 0.0

        val = _eq["second_order"] * self.percentage_improvement * self.percentage_improvement
        val += _eq["first_order"] * self.percentage_improvement + _eq["scaler"]

        return min([_eq["min"], val])
