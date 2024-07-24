import logging

from celery import shared_task
from django.apps import apps
from django.contrib.contenttypes.models import ContentType

from axis.filehandling.models import CustomerDocument
from axis.hes.hes import DOEInterface, DOEAPIError, DOEValidationError
from axis.hes.enumerations import REPORTED
from axis.hes.utils import handle_task_error
from simulation.enumerations import Orientation
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
def generate_label(status_id: int, credential_id: int, orientation: Orientation):
    """Gets the reports from a simulation"""
    [hes_simulation, simulation_status] = get_hes_sim_and_status(status_id, orientation)

    # Remove the old ones...
    content_type = ContentType.objects.get_for_model(hes_simulation)
    home_content_type = None
    if hes_simulation.home_status and hes_simulation.home_status.home:
        home_content_type = ContentType.objects.get_for_model(hes_simulation.home_status.home)
    objects = CustomerDocument.objects.filter(
        content_type=content_type, object_id=hes_simulation.pk
    )
    if objects.count():
        pdf = objects.filter(type="document", document__endswith=".pdf").first()
        if home_content_type and pdf:
            home_pdf = CustomerDocument.objects.filter(
                document__contains="hes_label_",
                document__endswith=".pdf",
                content_type=home_content_type,
                object_id=hes_simulation.home_status.home.pk,
            )
            if home_pdf.exists():
                home_pdf.delete()
        objects.delete()

    doe = DOEInterface(credential_id=credential_id)

    try:
        data = doe.generate_label(hes_simulation.building_id)
    except DOEValidationError as error:
        return handle_task_error(error, simulation_status, hes_simulation, "validate_inputs")
    except DOEAPIError as error:
        return handle_task_error(error, simulation_status, hes_simulation, "generate_label")

    for file in data.get("files", []):
        data_type = "document" if file["type"] == "pdf" else "image"
        document = file["document"].read()
        CustomerDocument.objects.store(
            content_object=hes_simulation,
            company=hes_simulation.company,
            document=document,
            filename=file["name"],
            filesize=len(document),
            type=data_type,
        )

    hes_simulation.status = REPORTED
    hes_simulation.save()
    return data.get("message")
