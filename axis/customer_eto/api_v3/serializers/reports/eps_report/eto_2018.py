"""eto_2018.py - Axis"""

__author__ = "Steven K"
__date__ = "10/14/21 15:15"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
from functools import cached_property

from axis.customer_eto.api_v3.serializers.reports.eps_report.base import EPSReportCoreSerializer
from axis.customer_eto.api_v3.serializers.reports.eps_report.legacy_simulation import (
    EPSReportLegacySimulationSerializer,
)
from axis.customer_eto.models import FastTrackSubmission


log = logging.getLogger(__name__)


class EPSReport2018Serializer(EPSReportCoreSerializer):
    @cached_property
    def _simulation_data(self) -> dict:
        home_status = self.instance.home_status
        serializer = EPSReportLegacySimulationSerializer(data=home_status.floorplan.remrate_target)
        return serializer.to_representation(home_status.floorplan.remrate_target)

    def get_year(self, _obj: FastTrackSubmission) -> int:
        return self._simulation_data.get("construction_year") or datetime.date.today().year

    def get_square_footage(self, _obj: FastTrackSubmission) -> int:
        return self._simulation_data.get("conditioned_area")

    def get_kwh_cost(self, _obj: FastTrackSubmission) -> str:
        return self._simulation_data.get("electric_unit_cost")

    def get_therm_cost(self, _obj: FastTrackSubmission) -> str:
        return self._simulation_data.get("gas_unit_cost")

    def get_insulated_ceiling(self, _obj: FastTrackSubmission) -> str:
        ans = self._checklist_answers.get("ceiling-r-value")
        if ans and len(ans):
            try:
                return f"R-{float(ans):.0f}"
            except ValueError:
                return f"R-{ans}"
        return ""

    def get_insulated_walls(self, _obj: FastTrackSubmission) -> str:
        return self._simulation_data.get("insulated_walls")

    def get_insulated_floors(self, _obj: FastTrackSubmission) -> str:
        return self._simulation_data.get("insulated_floors")

    def get_efficient_windows(self, _obj: FastTrackSubmission) -> str:
        return self._simulation_data.get("efficient_windows")

    def get_efficient_lighting(self, _obj: FastTrackSubmission) -> str:
        return self._simulation_data.get("efficient_lighting")

    def get_water_heater(self, _obj: FastTrackSubmission) -> str:
        return self._simulation_data.get("water_heater_efficiency")

    def get_space_heating(self, _obj: FastTrackSubmission) -> str:
        return self._simulation_data.get("heating_efficiency")

    def get_envelope_tightness(self, _obj: FastTrackSubmission) -> str:
        return self._simulation_data.get("envelope_tightness")
