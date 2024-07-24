"""eps.py - Axis"""

__author__ = "Steven K"
__date__ = "8/19/21 12:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import tempfile
import zipfile

from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.core import management
from django.core.files.base import ContentFile
from django.core.management import CommandError

from axis.core.tests.test_views import DevNull
from axis.filehandling.log_storage import LogStorage
from axis.filehandling.models import AsynchronousProcessedDocument

logger = get_task_logger(__name__)


@shared_task(bind=True, time_limit=60 * 5)
def eps_report_task(
    self, asynchronous_process_document_id, user_id, eep_program_home_status_ids=None
):
    """
    Generate report tasks
    :param self:
    :param asynchronous_process_document_id:
    :param user_id:
    :param eep_program_home_status_ids: list of EEPProgramHomeStatus ids
    """
    if not eep_program_home_status_ids:
        eep_program_home_status_ids = []

    from axis.customer_eto.api_v3.viewsets.eps_report import get_eps_report

    task_meta = {
        "processing": {"current": 0, "total": len(eep_program_home_status_ids)},
        "writing": {"current": 0, "total": 1},
    }

    self.update_state(state="STARTED", meta=task_meta)

    user = get_user_model().objects.get(id=user_id)

    app_log = LogStorage(model_id=asynchronous_process_document_id)

    asynchronous_process_document = AsynchronousProcessedDocument.objects.get(
        id=asynchronous_process_document_id
    )
    asynchronous_process_document.task_id = self.request.id
    asynchronous_process_document.task_name = self.name
    asynchronous_process_document.save()

    app_log.info(
        "{user} requested task [{task_id}]".format(
            user=user.get_full_name(), task_id=asynchronous_process_document.task_id
        )
    )

    app_log.info(f"Generating {len(eep_program_home_status_ids)} reports")

    with tempfile.SpooledTemporaryFile() as tmp:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as archive:
            for home_status_id in eep_program_home_status_ids:
                stream, label = get_eps_report(home_status_id, user, return_virtual_workbook=True)
                archive.writestr(label, stream.getvalue())
                task_meta["processing"]["current"] += 1
                self.update_state(state="STARTED", meta=task_meta)
        tmp.seek(0)
        app_log.info("Saving report")
        filename = "Energy_Performance_Score_Reports.zip"
        asynchronous_process_document.document.save(filename, ContentFile(tmp.read()))

    app_log.info("Done")
    task_meta["writing"]["current"] = 1
    self.update_state(state="DONE", meta=task_meta)
    app_log.update_model(throttle_seconds=None)


@shared_task
def generate_eto_report(*_args, home_status_id: int):
    try:
        management.call_command(
            "generate_eto_report", "--home-status", home_status_id, "--store", stdout=DevNull()
        )
    except CommandError as err:
        if generate_eto_report.request.called_directly:
            raise
        logger.error(
            f"Issue generating final EPS report for home_status_id {home_status_id} - {err}"
        )
