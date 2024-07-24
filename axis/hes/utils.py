"""utils.py: Django """


import logging
from functools import lru_cache

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from django.contrib.auth import get_user_model

from axis.hes.models import HESSimulationStatus, HESSimulation
from axis.hes.enumerations import NEW, COMPLETE, FAILED
from axis.home.models import EEPProgramHomeStatus
from simulation.enumerations import Orientation
from simulation.models import Simulation

__author__ = "Steven K"
__date__ = "11/24/2019 14:00"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from simulation.serializers.hpxml import HesHpxmlSimulationSerializer, Transaction, EventType
from simulation.serializers.hpxml.exceptions import SimulationCannotBeSerialized

log = logging.getLogger(__name__)

User = get_user_model()


@lru_cache
def get_hes_status(home_status_id: int = None, simulation_id: int = None, user_id: int = None):
    """Generic way to get the HES Status and what a user can / can't do.

    TODO: The logic here would be much easier to understand if each attribute were implemented
          as its own little function.
    """

    data = {
        "can_create": False,
        "can_update": False,
        # Can be "Score has not been generated", "Missing annotations", "Missing HES Credentials", or any valid value
        # of the HESSimulationStatus.status field
        "status": "Score has not been generated",
        # True if an HESSimulationStatus exists matching the passed values
        "has_simulation": False,
        "simulation_endpoint": reverse("apiv2:hes-generate"),
        "simulation_id": simulation_id,
        "has_hes_credentials": False,
        "company_id": None,
        "simulation_status_id": None,
        "wc_simulation_id": None,
        "disabled": True,
        "errors": [],
        "is_valid": True,
        "can_download_hpxml": False,
        "hpxml_url": None,
    }
    home_status = None
    simulation = None

    user = None
    if user_id:
        user = User.objects.get(id=user_id)
        data["company_id"] = user.company_id
        try:
            data["has_hes_credentials"] = user.hes_credentials is not None
        except ObjectDoesNotExist:
            data["status"] = "Missing HES Credentials"
            pass

        if user.is_superuser:
            data["can_download_hpxml"] = True
            data["hpxml_url"] = reverse("apiv2:hes-hpxml", kwargs={"sim_id": simulation_id})

    if home_status_id:
        home_status = EEPProgramHomeStatus.objects.get(id=home_status_id)
        simulation = home_status.floorplan.simulation
        data["simulation_id"] = home_status.floorplan.simulation_id

    elif simulation_id:
        simulation = Simulation.objects.get(id=simulation_id)

    if simulation:
        data["company_id"] = simulation.company_id

    # What can the user do
    if simulation and user:
        if user.is_superuser or "hes.add_hessimulationstatus" in user.get_all_permissions():
            data["can_create"] = True
            data["disabled"] = False

    hes_simulation_status = HESSimulationStatus.objects.filter(
        home_status=home_status, simulation=simulation
    ).first()
    if hes_simulation_status:
        data["can_create"] = False
        data["has_simulation"] = True
        data["simulation_status_id"] = hes_simulation_status.pk
        if hes_simulation_status.worst_case_simulation_id:
            data["wc_simulation_id"] = hes_simulation_status.worst_case_simulation_id
            data["wc_orientation"] = hes_simulation_status.worst_case_orientation

        data["status"] = hes_simulation_status.status

        data["disabled"] = hes_simulation_status.status not in [NEW, COMPLETE, FAILED]
        if hes_simulation_status.status == FAILED:
            data["errors"] += hes_simulation_status.hes_simulations.values_list("error", flat=True)

        # What can the user do
        if user and "hes.change_hessimulationstatus" in user.get_all_permissions():
            data["can_update"] = True
            allowed_status = [COMPLETE, FAILED] if user.is_superuser else [COMPLETE]
            if hes_simulation_status.status in allowed_status:
                data["disabled"] = False

        if (
            hes_simulation_status.status == COMPLETE
            and hes_simulation_status.worst_case_simulation_id
        ):
            url = reverse("apiv2:hes-report", kwargs={"pk": hes_simulation_status.pk})
            data["report_download_url"] = url
    elif simulation:
        # This is where we want to make sure that we can serialize this data.
        try:
            HesHpxmlSimulationSerializer(
                instance=simulation,
                orientation=Orientation.UNKNOWN,
                transaction=Transaction.CREATE,
                event_type=EventType.PRECONSTRUCTION,
            ).hpxml
        except (SimulationCannotBeSerialized, ValueError) as err:
            data["errors"].append(str(err))
        except Exception as err:
            data["errors"].append(str(err))
            log.exception(
                f"Unable to serialize simulation ({simulation.id}) on home ({home_status.home_id})"
            )

    if home_status and home_status.is_missing_hes_score_annotations():
        data["status"] = "Missing annotations"
        data["can_create"] = False
        data["disabled"] = True

    return data


def handle_task_error(
    exception: str | BaseException,
    simulation_status: HESSimulationStatus,
    hes_simulation: HESSimulation,
    function_name: str,
):
    """This should typically be called whenever a task in this module encounters an error. It
    ensures that the error will be logged in a standard format and that the error will be saved
    to the associated HESSimulation"""
    error_text = f"{function_name} HESSimulationStatus ID: {simulation_status.pk} -- {exception}"
    log.error(error_text)
    hes_simulation.error = str(exception)
    hes_simulation.status = FAILED
    hes_simulation.save()
    return error_text
