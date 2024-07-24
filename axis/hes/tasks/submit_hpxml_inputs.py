import logging

from celery import shared_task
from django.apps import apps
from django.db.transaction import atomic
from axis.hes.hes import DOEInterface, DOEAPIError
from axis.hes.models import HESSimulation, HESSimulationStatus
from axis.hes.enumerations import UPLOADED, COMPLETE, FAILED
from axis.hes.utils import handle_task_error
from axis.home.models import EEPProgramHomeStatus, Home
from simulation.serializers.hpxml import HesHpxmlSimulationSerializer
from simulation.models import Simulation
from simulation.enumerations import Orientation
from simulation.serializers.hpxml import Transaction, EventType

__author__ = "Steven K"
__date__ = "11/12/2019 09:05"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven K", "Benjamin Stürmer"]

app = apps.get_app_config("hes")
log = logging.getLogger(__name__)


@shared_task(time_limit=60 * 10)
def submit_hpxml_inputs(
    status_id: int, credential_id: int, orientation: Orientation, external_id: str = None
) -> str:
    """Uploads HPXML to DOE in order to generate a Home Energy Score
    :return str: Success or error message
    """
    from ..models import HESSimulationStatus

    sim_status: HESSimulationStatus = HESSimulationStatus.objects.filter(pk=status_id).first()
    if not sim_status:
        raise Exception(
            f"Unable to `submit_hpxml_inputs` HESSimulationStatus {status_id} does not exist"
        )

    sim = sim_status.simulation
    if not sim:
        raise Exception(
            f"Unable to `submit_hpxml_inputs` HESSimulationStatus {status_id} has no Simulation"
        )

    from ..functions import get_external_id_from_annotation

    home_status: EEPProgramHomeStatus = sim_status.home_status
    hpxml = _get_hpxml(
        sim_status.simulation,
        orientation,
        external_id or get_external_id_from_annotation(home_status),
        home_status.home,
    )

    hes_sim, is_hes_simulation_new = HESSimulation.objects.get_or_create(
        home_status=sim_status.home_status,
        simulation_status=sim_status,
        orientation=orientation,
    )

    doe = DOEInterface(credential_id=credential_id)
    try:
        hes_sim.building_id = doe.submit_hpxml_inputs(hpxml)
        hes_sim.status = UPLOADED
    except DOEAPIError as err:
        error_message = (
            "Failed attempting to generate Home Energy Score "
            f"for Simulation {sim_status.simulation.id}: '{err}'"
        )
        log.warning(error_message)
        hes_sim.error = error_message
        hes_sim.status = FAILED
    except Exception as err:
        error_message = (
            "Got an unexpected exception trying to generate Home Energy Score "
            f"for Simulation {sim_status.simulation.id}."
        )
        log.error(error_message + f" Exception was: '{err}'")
        hes_sim.error = error_message + "."

    with atomic():
        hes_sim.save()
        sim_status.save()

    if hes_sim.error:
        return handle_task_error(hes_sim.error, sim_status, hes_sim, "submit_hpxml_inputs")

    return f"Successfully submitted HPXML to {doe.base_url} and received building id {hes_sim.building_id}"


def _get_hpxml(sim: Simulation, orientation: Orientation, external_id: str, home: Home) -> str:
    # If there has ever been a successful HES score calculated for the home, then
    # we are updating an existing HES home. Otherwise we are creating a new one.
    transaction = Transaction.CREATE
    hes_score_status: HESSimulationStatus
    for hes_score_status in sim.hes_score_statuses.all():
        if hes_score_status.status == COMPLETE:
            transaction = Transaction.UPDATE
            break

    address_parts = home.get_home_address_display_parts(
        company=sim.company,
        include_city_state_zip=True,
        include_lot_number=False,
    )

    return HesHpxmlSimulationSerializer(
        instance=sim,
        orientation=orientation,
        # Preconstruction is always the correct event type; according to discussion with
        # Bob and Steve on March 1, 2023, all homes that we run are in a preconstruction
        # state, so we never need to mark a home as "initial" or "corrected", which are
        # assessment types intended only for finished homes that have been assessed.
        event_type=EventType.PRECONSTRUCTION,
        transaction=transaction,
        external_id=external_id,
        context={
            "address": {
                "street_line1": address_parts.street_line1,
                "street_line2": address_parts.street_line2,
                "city_name": address_parts.city,
                "state_code": address_parts.state,
                "zipcode": address_parts.zipcode,
            }
        },
    ).hpxml
