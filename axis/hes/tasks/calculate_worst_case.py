import logging

from celery import shared_task
from django.apps import apps
from django.contrib.contenttypes.models import ContentType

from axis.filehandling.models import CustomerDocument
from axis.hes.enumerations import FAILED
from .exceptions import TaskFailed

__author__ = "Steven K"
__date__ = "11/12/2019 09:05"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)
app = apps.get_app_config("hes")


@shared_task(time_limit=60 * 10)
def calculate_worst_case(status_id, orientation=None) -> None:
    """Once all four simulations have been hit then calculate the worst case."""
    from ..models import HESSimulationStatus

    simulation_status = HESSimulationStatus.objects.filter(pk=status_id).first()

    if not simulation_status:
        raise TaskFailed(f"HESSimulation pk {status_id} does not exist")

    if orientation:
        hes_simulations = [simulation_status.get_hes_simulation(orientation)]
    else:
        hes_simulations = simulation_status.hes_simulations.all()

    if None in hes_simulations:
        raise TaskFailed("Unable to `calculate_worst_case` - missing simulations")

    worst_case = None
    errors = []
    for hes_simulation in hes_simulations:
        if hes_simulation.status == FAILED:
            errors.append(hes_simulation.orientation)
        elif hes_simulation.base_score is None:
            errors.append(hes_simulation.orientation)
        elif worst_case is None or hes_simulation.base_score < worst_case.base_score:
            worst_case = hes_simulation
        elif hes_simulation.base_score == worst_case.base_score:
            if hes_simulation.source_energy_total_base > worst_case.source_energy_total_base:
                worst_case = hes_simulation
    if worst_case and simulation_status.worst_case_simulation_id != worst_case.pk:
        simulation_status.worst_case_simulation = worst_case
        simulation_status.save()
        log.debug(
            "Setting worst case orientation [%(status)s] for home_status (%(home_status_id)s)"
            " to %(orientation)r",
            {
                "status": simulation_status.pk,
                "home_status_id": simulation_status.home_status_id,
                "orientation": worst_case.orientation,
            },
        )
    else:
        log.debug(
            "Leaving worst case orientation [%(status)s] as %(orientation)r",
            {
                "status": simulation_status.pk,
                "orientation": worst_case.orientation if worst_case else "---",
            },
        )

    if len(errors):
        log.error(
            "Errors found %s in simulations (%s)- Setting failure",
            len(errors),
            ", ".join(errors),
        )

    try:
        simulation_pdf = worst_case.customer_documents.get(
            document__contains="hes_label_", document__endswith=".pdf"
        )
    except (
        CustomerDocument.DoesNotExist,
        CustomerDocument.MultipleObjectsReturned,
        AttributeError,
    ):
        return

    if not simulation_status.home_status or not simulation_status.home_status.home:
        return

    home_content_type = ContentType.objects.get_for_model(simulation_status.home_status.home)
    existing = CustomerDocument.objects.filter(
        document__contains="hes_label_",
        document__endswith=".pdf",
        content_type=home_content_type,
        object_id=simulation_status.home_status.home.pk,
    ).first()

    CustomerDocument.objects.store(
        content_object=simulation_status.home_status.home,
        company=simulation_status.company,
        document=simulation_pdf.document.read(),
        filename=simulation_pdf.filename,
        filesize=simulation_pdf.filesize,
        type=simulation_pdf.type,
        pk=existing.pk if existing else None,
    )
