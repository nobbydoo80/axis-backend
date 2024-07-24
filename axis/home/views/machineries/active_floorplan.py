from typing import List

from django.core.exceptions import ObjectDoesNotExist
from django.urls.base import reverse

from axis.customer_neea.utils import NEEA_BPA_SLUGS
from axis.examine.machinery import ReadonlyMachineryMixin
from axis.hes.utils import get_hes_status
from axis.home.models import EEPProgramHomeStatus
from axis.floorplan.models import Floorplan
from simulation.enumerations import AnalysisEngine, AnalysisType, AnalysisStatus
from simulation.models import Analysis

from .home_status_floorplan import HomeStatusFloorplanExamineMachinery

__author__ = "Artem Hruzd"
__date__ = "06-24-19 5:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class ActiveFloorplanExamineMachinery(ReadonlyMachineryMixin, HomeStatusFloorplanExamineMachinery):
    def get_objects(self) -> List[Floorplan]:
        try:
            homestatus = EEPProgramHomeStatus.objects.get(id=int(self.context["home_status_id"]))
        except ObjectDoesNotExist:
            return []
        if homestatus.floorplan:
            return [homestatus.floorplan]
        return []

    def get_helpers(self, instance: Floorplan) -> List[dict]:
        helpers = super(ActiveFloorplanExamineMachinery, self).get_helpers(instance)
        try:
            home_status_id = int(self.context["home_status_id"])
        except ValueError:
            home_status_id = None

        helpers["home_status_id"] = home_status_id

        home_status = EEPProgramHomeStatus.objects.filter(id=home_status_id).first()
        helpers["show_ceiling_r_values"] = False
        if home_status and home_status.eep_program.slug in NEEA_BPA_SLUGS:
            helpers["show_ceiling_r_values"] = True

        helpers["hes_score_data"] = get_hes_status(
            home_status_id=home_status_id,
            simulation_id=instance.simulation_id,
            user_id=self.context["request"].user.id,
        )
        helpers["open_studio_eri_data"] = self._get_open_studio_eri_helper_data(instance)
        helpers["show_simulation_specifics"] = self.context["request"].user.is_superuser
        return helpers

    def get_default_actions(self, instance: Floorplan) -> List[dict]:
        """Get the set of actions that can be performed in the Floorplan section. See this
        class's Action() method for the format of the returned dicts"""
        actions = super().get_default_actions(instance)

        # We offer HES and OpenStudio-ERI if a Simulation is present
        if instance.simulation_id:
            actions.append(self.Action(**self._get_hes_action_kwargs(instance.simulation_id)))

            # TODO: This is a temporary measure to keep our usual users from accessing
            #  the OS-ERI feature while it is still in development, but allow Bob to
            #  demo it for customers
            if self.context["request"].user.is_superuser:
                actions.append(self.Action(**self._get_oseri_action_kwargs()))

        return actions

    def _get_hes_action_kwargs(self, simulation_id: int) -> dict:
        """Gets the configuration for the Home Energy Score action"""
        try:
            home_status_id = int(self.context["home_status_id"])
        except ValueError:
            home_status_id = None

        hes_data = get_hes_status(
            home_status_id=home_status_id,
            simulation_id=simulation_id,
            user_id=self.context["request"].user.id,
        )

        icon = None
        text = "HES: " + hes_data["status"]
        instruction = "simulateHES"
        disabled = hes_data["disabled"]

        if hes_data["can_update"] and hes_data["has_simulation"]:
            icon = "repeat"
        elif hes_data["can_create"]:
            if not hes_data["has_hes_credentials"]:
                text = "Update HES Credentials"
                instruction = "updateProfile"
                disabled = False
            else:
                icon = "list-ul"
                text = "Request HES Score"

        return {
            "name": text,
            "disabled": disabled,
            "icon": icon if not disabled else None,
            "instruction": instruction,
        }

    def _get_oseri_action_kwargs(self) -> dict:
        """Gets the configuration for the OpenStudio-ERI action"""

        eri_analysis = self._get_open_studio_eri_result()

        if eri_analysis is None:
            return {
                "name": "Get OpenStudio-ERI Score",
                "instruction": "simulateOpenStudio",
                "icon": "list-ul",
            }

        if eri_analysis.status in [
            AnalysisStatus.PENDING,
            AnalysisStatus.STARTED,
            AnalysisStatus.RETRY,
        ]:
            return {
                "name": f"OpenStudio-ERI: score {eri_analysis.get_status_display()}...",
                "disabled": True,
                "instruction": "none",
            }

        if eri_analysis.status == AnalysisStatus.FAILED:
            return {
                "icon": "repeat",
                "name": "OpenStudio-ERI: ERROR (click to re-run)",
                "instruction": "simulateOpenStudio",
            }

        # If we got here, then the OS-ERI run was successful
        return {
            "icon": "repeat",
            "name": "Regenerate OpenStudio-ERI score",
            "instruction": "simulateOpenStudio",
        }

    def _get_open_studio_eri_helper_data(self, floorplan: Floorplan) -> dict:
        if not floorplan.simulation:
            return

        oseri_result = self._get_open_studio_eri_result()
        return {
            "status": oseri_result.get_status_display() if oseri_result is not None else None,
            "error_msg": oseri_result.result if oseri_result is not None else None,
            "generate_url": reverse(
                "api_v3:simulations-open-studio-eri",
                args=[floorplan.simulation_id],
            ),
        }

    def _get_eep_program_home_status(self) -> EEPProgramHomeStatus | None:
        try:
            return EEPProgramHomeStatus.objects.get(pk=self.context["home_status_id"])
        except ValueError:
            return None

    def _get_open_studio_eri_result(self) -> Analysis | None:
        if self.instance and self.instance.simulation:
            return self.instance.simulation.analyses.filter(
                engine=AnalysisEngine.EPLUS,
                type__in=[
                    AnalysisType.OS_ERI_2014AEG_DESIGN,
                    AnalysisType.OS_ERI_2014AE_DESIGN,
                    AnalysisType.OS_ERI_2014A_DESIGN,
                    AnalysisType.OS_ERI_2014_DESIGN,
                    AnalysisType.OS_ERI_2019AB_DESIGN,
                    AnalysisType.OS_ERI_2019A_DESIGN,
                    AnalysisType.OS_ERI_2019_DESIGN,
                ],
            ).first()
