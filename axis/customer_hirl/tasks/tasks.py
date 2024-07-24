__author__ = "Autumn Valenta"
__date__ = "08/22/16 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from openpyxl import load_workbook

from axis.customer_hirl.scoring import scoring_registry
from axis.customer_hirl.scoring.base import (
    ScoringExtractionValidationException,
    ScoringExtractionRequirementsFailed,
    ScoringExtractionUnknownVersion,
    ScoringExtractionVersionNotSupported,
)
from axis.filehandling.log_storage import LogStorage
from axis.filehandling.models import AsynchronousProcessedDocument

log = get_task_logger(__name__)

User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")


@shared_task(bind=True, time_limit=60 * 60)
def scoring_upload_task(self, user_id, result_object_id, template_type, data_type, verifier_id):
    """
    Pivotal_NGBS_Scoring_Spreadsheet_Data_Extraction_SOW_200406.pages
    :param self - task
    :param user_id:
    :param result_object_id:
    :param template_type - type of excel file
    :param data_type - data type where we need save annotations
    :param verifier_id - verifier id
    :return:
    """
    task_meta = {"processing": {"current": 0, "total": 1}, "writing": {"current": 0, "total": 1}}

    self.update_state(state="STARTED", meta=task_meta)

    scoring_cls = scoring_registry[template_type]
    app_log = LogStorage(model_id=result_object_id)

    result_object = AsynchronousProcessedDocument.objects.get(id=result_object_id)
    user = User.objects.get(id=user_id)
    verifier = User.objects.get(id=verifier_id)
    byte_file = result_object.document.read()
    wb = load_workbook(ContentFile(byte_file), data_only=True, read_only=True)
    result_object.document.close()

    scoring = scoring_cls(
        workbook=wb,
        user=user,
        data_type=data_type,
        verifier=verifier,
        app_log=app_log,
        document=result_object.document,
        workbook_filename=result_object.filename,
    )

    task_meta["processing"]["current"] = 1
    self.update_state(state="STARTED", meta=task_meta)
    try:
        scoring.process()
    except (
        ScoringExtractionUnknownVersion,
        ScoringExtractionVersionNotSupported,
        ScoringExtractionValidationException,
        ScoringExtractionRequirementsFailed,
    ) as exc:
        self.update_state(state="FAILURE", meta=task_meta)
        raise exc
    except Exception as exc:
        self.update_state(state="FAILURE", meta=task_meta)
        app_log.error(exc)
        raise exc

    task_meta["writing"]["current"] = 1
    self.update_state(state="DONE", meta=task_meta)
