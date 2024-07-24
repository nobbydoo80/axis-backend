"""eto_2017.py - Axis"""

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


class EPSReport2017Serializer(EPSReportCoreSerializer):
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
        ans = self._checklist_answers.get("eto-flat_ceiling_r_value-2017")
        if ans and len(ans):
            return f"R-{float(ans):.0f}"
        ans = self._checklist_answers.get("eto-vaulted_ceiling_r_value-2017")
        if ans and len(ans):
            return f"R-{float(ans):.0f}"
        return ""

    def get_insulated_walls(self, _obj: FastTrackSubmission) -> str:
        ans = self._checklist_answers.get("eto-above_grade_walls_r_value-2017")
        if ans and len(ans):
            return f"R-{float(ans):.0f}"
        return ""

    def get_insulated_floors(self, _obj: FastTrackSubmission) -> str:
        ans = self._checklist_answers.get("eto-framed_floor_r_value")
        if ans and len(ans):
            return f"R-{float(ans):.0f}"

        ans = self._checklist_answers.get("eto-slab_under_insulation_r_value")
        if ans and len(ans):
            return f"R-{float(ans):.0f}"

        ans = self._checklist_answers.get("eto-slab_perimeter_r_value")
        if ans and len(ans):
            return f"R-{float(ans):.0f}"

        return ""

    def get_efficient_windows(self, _obj: FastTrackSubmission) -> str:
        ans = self._checklist_answers.get("eto-window_u_value")
        if ans and len(ans):
            return f"U-{float(ans):.2f}"
        return ""

    def get_efficient_lighting(self, _obj: FastTrackSubmission) -> str:
        ans = self._checklist_answers.get("eto-lighting_pct-2016")
        if ans and len(ans):
            return "{} %".format(round(float(ans)))
        return ""

    def get_water_heater(self, _obj: FastTrackSubmission) -> str:
        ans = self._checklist_answers.get("eto-water_heater_heat_type-2017")
        value = ""
        if ans and len(ans):
            value = ans
        ans = self._checklist_answers.get("eto-water_heater_ef")
        if ans and len(ans):
            value += " {} EF".format(round(float(ans), 1))
        return value

    def get_space_heating(self, _obj: FastTrackSubmission) -> str:
        ans = self._checklist_answers.get("eto-primary_heat_afue")
        value = ""
        if ans and len(ans):
            value = ans
        else:
            ans = self._checklist_answers.get("eto-primary_heat_hspf-2016")
            if ans and len(ans):
                value = "{} HSFP".format(round(float(ans), 1))
            else:
                ans = self._checklist_answers.get("eto-primary_heat_seer-2016")
                if ans and len(ans):
                    value = "{} SEER".format(round(float(ans), 1))
                else:
                    ans = self._checklist_answers.get("eto-primary_heat_cop-2016")
                    if ans and len(ans):
                        value = "{} COP".format(round(float(ans), 1))

        ans = self._checklist_answers.get("eto-primary_heat_type-2016")
        if ans and len(ans):
            if "pump" in ans.lower():
                value += " Heat Pump"
            elif "radiant" in ans.lower():
                value += " Radiant"
            elif "furnace" in ans.lower():
                value += " Furnace"
            else:
                value += " {}".format(ans)
        return value

    def get_envelope_tightness(self, _obj: FastTrackSubmission) -> str:
        ans = self._checklist_answers.get("eto-duct_leakage_ach50")
        if ans and len(ans):
            return "{} ACH @ 50Pa".format(round(float(ans), 1))
        return ""
