"""eto_2018.py: Django Core Calculations for EPS Calculator"""


import logging

from axis.customer_eto.calculator.eps.calculations.eto_2017 import Calculations2017

__author__ = "Steven K"
__date__ = "08/21/2019 09:05"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class Calculations2018(Calculations2017):
    """Core calculations for 2018"""

    @property
    def electric_thermostat_savings_unadjusted(self):
        """Electric thermostat savings unadjusted"""
        if not self.is_improved:
            return 0.0
        if self.smart_thermostat and self.smart_thermostat_furnace_type == "ASHP":
            return self.heating_kwh_unadjusted * self.electric_smart_tstat_savings_pct
        return 0.0
