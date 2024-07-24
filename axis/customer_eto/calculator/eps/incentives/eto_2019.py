"""eto_2019.py: Django ETO EPS Calculator Incentives"""


import logging

from axis.customer_eto.calculator.eps.incentives.eto_2018 import Incentives2018

__author__ = "Steven K"
__date__ = "08/21/2019 08:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class Incentives2019(Incentives2018):
    """Incentives for 2019"""

    def __init__(self, **kwargs):
        self.has_heat_pump_water_heater = kwargs.pop("has_heat_pump_water_heater", False)
        self.hot_water_ef = kwargs.pop("hot_water_ef", 0.0)
        self.use_alternate_allocation_method = kwargs.pop("use_alternate_allocation_method", False)

        super(Incentives2019, self).__init__(**kwargs)

        self.alternate_electric_incentive_allocation = None
        self.alternate_gas_incentive_allocation = None
        if self.constants:
            _val = self.constants.ALTERNATE_METHOD_ELECTRIC_INCENTIVE_ALLOCATION
            self.alternate_electric_incentive_allocation = _val
            _val = self.constants.ALTERNATE_METHOD_GAS_INCENTIVE_ALLOCATION
            self.alternate_gas_incentive_allocation = _val

    @property
    def electric_utility_allocation_pct(self):
        """Break out the utility allocation percentage"""
        if self.use_alternate_allocation_method:
            return self.alternate_electric_incentive_allocation
        return super(Incentives2019, self).electric_utility_allocation_pct

    @property
    def gas_utility_allocation_pct(self):
        """Break out the utility allocation percentage"""
        if self.use_alternate_allocation_method:
            return self.alternate_gas_incentive_allocation
        return super(Incentives2019, self).gas_utility_allocation_pct

    @property
    def builder_electric_incentive(self):
        """Builder Electric Incentive"""
        value = super(Incentives2019, self).actual_builder_electric_incentive
        if self.us_state == "OR" and self.has_heat_pump_water_heater:
            value -= 250.0
        return round(max([value, 0.0]), 0)

    @property
    def _report_alt_allocation_data(self):
        """Do we want to tell why we are doing this"""
        data = []
        if self.use_alternate_allocation_method:
            data.append("\nNote:  Using alternate allocation method")
        return data
