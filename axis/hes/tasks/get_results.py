import logging

from celery import shared_task
from django.apps import apps
from django.utils.timezone import now

from axis.hes.hes import DOEInterface, DOEAPIError
from axis.hes.enumerations import ACTIVE
from axis.hes.utils import handle_task_error
from .functions import get_hes_sim_and_status

__author__ = "Steven K"
__date__ = "11/12/2019 09:05"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)
app = apps.get_app_config("hes")


@shared_task(time_limit=60 * 10)
def get_results(status_id, credential_id, orientation):
    """Pulls the resulting data"""
    [hes_simulation, simulation_status] = get_hes_sim_and_status(status_id, orientation)

    simulation_fields = [f.name for f in hes_simulation._meta.fields if f.name not in ["id"]]

    doe = DOEInterface(credential_id=credential_id)
    data = doe.retrieve_label_results(building_id=hes_simulation.building_id)
    save_required = False

    for key, value in data.items():
        if key in simulation_fields and value is not None and getattr(hes_simulation, key) != value:
            setattr(hes_simulation, key, value)
            save_required = True
        elif key not in simulation_fields:
            log.warning(f"Key not found {key}: {value} in returned HES Data")

    try:
        data = doe.retrieve_extended_results(building_id=hes_simulation.building_id)
    except DOEAPIError as error:
        return handle_task_error(error, simulation_status, hes_simulation, "submit_hpxml_inputs")

    for key, value in data.items():
        if key in simulation_fields and value is not None and getattr(hes_simulation, key) != value:
            setattr(hes_simulation, key, value)
            save_required = True
        elif key not in simulation_fields:
            log.warning(f"Extended Key not found {key}: {value} in returned HES Data")

    if hes_simulation.status != ACTIVE:
        hes_simulation.status = ACTIVE
        save_required = True

    if save_required:
        hes_simulation.save()

    _type = "updated" if save_required else "verified"
    msg = "Successfully %(type)s Simulation Results for building id %(building_id)s"
    return msg % {"type": _type, "building_id": hes_simulation.building_id}
