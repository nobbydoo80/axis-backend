import logging
from typing import Tuple
from django.apps import apps
from simulation.enumerations import Orientation
from axis.hes.tasks import create_or_update_hes_score
from axis.home.models import EEPProgramHomeStatus
from ..models import HESCredentials, HESSimulationStatus

__author__ = "Benjamin S"
__date__ = "07/11/2022 16:56"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Benjamin S",
]

log = logging.getLogger(__name__)
app = apps.get_app_config("hes")


def trigger_generation_task_for_home_status(
    *,
    hes_api_credentials: HESCredentials,
    home_status: EEPProgramHomeStatus,
    external_id: str = None,
    orientation: Orientation = None,
):
    if orientation is None:
        from ..functions import get_orientation_from_annotation

        orientation = get_orientation_from_annotation(home_status)

    floorplan = home_status.floorplan
    if floorplan is None:
        raise Exception(f"Home status '{home_status.pk}' has no floorplan")

    sim_id = floorplan.simulation_id
    if sim_id is None:
        raise Exception(f"Floorplan of home status '{home_status.pk}' has no simulation")

    hes_sim_status, is_sim_status_new = _get_hes_sim_status(home_status, sim_id)
    log.info(
        f"{'Creating' if is_sim_status_new else 'Updating'} Simulation Status {hes_sim_status.id}"
    )

    task = create_or_update_hes_score.delay(
        hes_sim_status_id=hes_sim_status.pk,
        credential_id=hes_api_credentials.pk,
        orientation=orientation,
        external_id=external_id,
    )
    log.info(
        f"create_or_update_hes_score task ({task.id}) created for Simulation Status {hes_sim_status.id}"
    )

    return task, hes_sim_status, is_sim_status_new


def _get_hes_sim_status(
    home_status: EEPProgramHomeStatus, simulation_id: int
) -> Tuple[HESSimulationStatus, bool]:
    """Get a HESSimulationStatus for the simulation we're running, or create one if none exists.
    :return tuple: Two values - first is the HESSimulationStatus, the second is True if the status object
    was newly created"""
    simulation_status, is_simulation_status_new = HESSimulationStatus.objects.get_or_create(
        home_status=home_status, simulation_id=simulation_id
    )

    if not is_simulation_status_new:
        # If the simulation status was created anew, it won't have any simulation results attached, but if we are
        # re-running a set of simulations, then we need to delete any simulations from the previous run.
        simulation_status.hes_simulations.all().delete()
        simulation_status.worst_case_simulation = None
        simulation_status.save()

    return simulation_status, is_simulation_status_new
