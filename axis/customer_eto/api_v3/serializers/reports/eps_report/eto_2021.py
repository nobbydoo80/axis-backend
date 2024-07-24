"""eto_2021.py - Axis"""

__author__ = "Steven K"
__date__ = "11/30/21 13:41"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from functools import cached_property

from .eto_2018 import EPSReport2018Serializer
from .simulation import EPSReport2021SimulationSerializer


log = logging.getLogger(__name__)


class EPSReport2021Serializer(EPSReport2018Serializer):
    @cached_property
    def _simulation_data(self) -> dict:
        home_status = self.instance.home_status
        serializer = EPSReport2021SimulationSerializer(data=home_status.floorplan.simulation)
        return serializer.to_representation(home_status.floorplan.simulation)
