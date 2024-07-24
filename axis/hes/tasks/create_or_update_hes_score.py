import logging

from celery import shared_task, chord, group

from axis.hes.models import HESSimulationStatus
from axis.hes.enumerations import IN_PROGRESS
from simulation.enumerations import Orientation

from .calculate_worst_case import calculate_worst_case
from .generate_label import generate_label
from .get_results import get_results
from .submit_hpxml_inputs import submit_hpxml_inputs

__author__ = "Benjamin S"
__date__ = "6/3/2022 14:25"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
    "Benjamin S",
]

log = logging.getLogger(__name__)


@shared_task(
    time_limit=60 * 10, default_retry_delay=2, ignore_result=True, store_errors_even_if_ignored=True
)
def create_or_update_hes_score(
    *,
    hes_sim_status_id: int,
    credential_id: int,
    orientation: Orientation | None = None,
    external_id: str = None,
):
    """Generate a Home Energy Score result for a simulation. Because we don't have the home's orientation in our data,
      we calculate this result by running the home facing each of the four cardinal directions, and return the worst
      result.

    :param int hes_sim_status_id: The database ID of the HESSimulationStatus that will
    :param int credential_id: The database ID of the HESCredentials that will be used to auth to the HES API
    :param Orientation orientation: If passed, instead of simulating all four orientations, only this orientation
      will be simulated, and it will be treated as the worst case result.
    :param str external_id: If passed, the HEScore will get this value set for its "external id" field, which can
      be used to store any custom value the creator of the home record wishes.
    """

    hes_sim_status = HESSimulationStatus.objects.filter(pk=hes_sim_status_id).first()
    if hes_sim_status is None:
        raise ValueError(f"No HESSimulationStatus could be found with ID {hes_sim_status_id}")

    # If the simulation is currently in progress, we presumably called this task twice in quick succession;
    # don't trigger another run. If this happens unexpectedly, that probably indicates that we got an unhandled
    # error of some kind during a simulation and failed to update the associated HESSimulationStatus correctly.
    if hes_sim_status.status == IN_PROGRESS:
        raise Exception("HES simulation status is currently 'in progress' and won't be restarted")

    # If an orientation was passed, we'll just trigger _submit_hpxml_for_orientation() for that orientation
    # and that orientation will be set to the worst-case. Otherwise we'll trigger it for each of the cardinal
    # directions.
    orientations = [orientation] if orientation is not None else Orientation.cardinal_directions()
    submit_hpxml_calls = [
        _submit_hpxml_for_orientation(
            status_id=hes_sim_status.pk,
            credential_id=credential_id,
            orientation=_o,
            external_id=external_id,
        )
        for _o in orientations
    ]
    return chord(group(*submit_hpxml_calls))(
        calculate_worst_case.si(status_id=hes_sim_status.pk, orientation=orientation)
    )


def _submit_hpxml_for_orientation(
    status_id: int, orientation: Orientation, credential_id: int, external_id: str
):
    """Submit. These are a chain of events with immutable signatures"""
    return (
        submit_hpxml_inputs.si(status_id, credential_id, orientation, external_id)
        | generate_label.si(status_id, credential_id, orientation)
        | get_results.si(status_id, credential_id, orientation)
    )
