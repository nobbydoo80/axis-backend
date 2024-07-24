"""eto_2016.py - Axis"""

__author__ = "Steven K"
__date__ = "10/14/21 15:14"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from .eto_2014 import EPSReport2014Serializer

from axis.customer_eto.models import FastTrackSubmission


log = logging.getLogger(__name__)


class EPSReport2016Serializer(EPSReport2014Serializer):
    def get_efficient_lighting(self, _obj: FastTrackSubmission) -> str:
        ans = self._checklist_answers.get("eto-lighting_pct-2016")
        if ans:
            return "{} %".format(round(float(ans)))
        return ""

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
