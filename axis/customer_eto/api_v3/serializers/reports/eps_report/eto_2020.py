"""eto_2020.py - Axis"""

__author__ = "Steven K"
__date__ = "9/30/21 12:47"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from functools import cached_property

from .eto_2018 import EPSReport2018Serializer
from .simulation import EPSReport2020SimulationSerializer


log = logging.getLogger(__name__)


class EPSReport2020Serializer(EPSReport2018Serializer):
    @cached_property
    def _simulation_data(self) -> dict:
        home_status = self.instance.home_status
        serializer = EPSReport2020SimulationSerializer(data=home_status.floorplan.simulation)
        return serializer.to_representation(home_status.floorplan.simulation)
