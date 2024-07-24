"""incentives.py - Axis"""

__author__ = "Steven K"
__date__ = "12/1/21 16:29"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from functools import cached_property

from axis.customer_eto.calculator.eps_2021.base import HomePath
from axis.customer_eto.calculator.eps_2021.incentives import Incentives2020

log = logging.getLogger(__name__)


class Incentives2021Fire(Incentives2020):
    @property
    def labels(self):
        return {
            "percent_improvement": "Percent Improvement",
            "full_territory_incentive": "2022 Fire Rebuild Builder Incentive",
        }

    @cached_property
    def full_territory_builder_incentive(self) -> float:
        """
        =MIN(8171,2*IF($D$6>=0.1,(36354*($D$6^2))-(4510.2*$D$6)+1210.5))
        :return:
        """
        if self.percent_improvement < 0.10:
            return 0.0

        value = 36354.0 * self.percent_improvement * self.percent_improvement
        value += -4510.2 * self.percent_improvement + 1210.5
        value *= 2
        return min([8171.0, value])

    @cached_property
    def home_path(self) -> HomePath:
        """
        Updated for 35%
        """

        if 0.2 > self.percent_improvement >= 0.10:
            return HomePath.PATH_1
        elif 0.3 > self.percent_improvement >= 0.20:
            return HomePath.PATH_2
        elif 0.35 > self.percent_improvement >= 0.30:
            return HomePath.PATH_3
        elif self.percent_improvement >= 0.35:
            return HomePath.PATH_4

    @cached_property
    def initial_verifier_incentive(self) -> float:
        """=@IFS(AND(D57>=0.1,D57<0.2),300,D57>=0.2,0.2*E48)"""
        if self.percent_improvement < 0.10:
            return 0.0
        if 0.10 <= self.percent_improvement < 0.20:
            return 300.00
        value = self.full_territory_builder_incentive * 0.2
        return max([0.0, value])
