"""eto_2019.py: Django Core Calculations for EPS Calculator"""


import logging

from .eto_2017 import Calculations2017
from .eto_2018 import Calculations2018

__author__ = "Steven K"
__date__ = "08/21/2019 09:06"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class Calculations2019(Calculations2018):
    """Core calculations for 2019 program"""

    def __init__(self, simulation, **kwargs):
        # pylint: disable=bad-super-call
        super(Calculations2018, self).__init__(simulation, **kwargs)
        self.generated_solar_pv_kwh = kwargs.get("generated_solar_pv_kwh", 0)
        self.qty_shower_head_1p5 = 0
        self.qty_shower_head_1p6 = 0
        self.qty_shower_head_1p75 = 0
        self.qty_shower_wand_1p5 = 0

    @property
    def pv_kwh_unadjusted(self):
        """Photovoltaics kWh unadjusted"""
        if not self.is_improved:
            return "N/A"
        return self.generated_solar_pv_kwh

    @property
    def lights_and_appliances_therms_heat_pump_fuel_weight(self):
        """Lights and appliances therm heat pump fuel weight"""
        return super(Calculations2017, self).lights_and_appliances_therms_heat_pump_fuel_weight
