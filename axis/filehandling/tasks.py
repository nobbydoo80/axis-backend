"""tasks.py: Django filehandling"""
__author__ = "Steven Klass"
__date__ = "6/11/12 7:07 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import io
import mimetypes
import os
import random
import time
import zipfile
from typing import List

from celery import shared_task
from celery.utils.log import get_task_logger

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone

from .log_storage import LogStorage
from .models import ResultObjectLog, AsynchronousProcessedDocument, CustomerDocument
from .utils import get_physical_file


logger = get_task_logger(__name__)
User = get_user_model()


@shared_task
def file_uploading_test(company_id, user_id, result_object_id, **kwargs):
    """This is the blueprint for all AsynchronousProcessedDocument tasks"""

    from .models import AsynchronousProcessedDocument

    log = kwargs.get("log", logger)

    result_object = AsynchronousProcessedDocument.objects.get(id=result_object_id)
    result_log = ResultObjectLog(result_object_id=result_object.id)

    if None in [company_id, user_id, result_object_id]:
        lerrors = "Missing items {0}".format(", ".join([company_id, user_id, result_object_id]))
        result_log.update(errors=lerrors, raise_errors=True)
        return

    user = User.objects.get(id=user_id)
    company = result_object.company
    document = result_object.document

    try:
        filename, notes = get_physical_file(document.name)
        result_log.update(result_list=notes, raise_errors=True)
    except AttributeError:
        filename, notes = document, ["Using document string {0}".format(document)]
        result_log.update(warnings=notes, raise_errors=True)

    msg = "{user} submitted {document} for processing with task {task} [{task_id}]"
    log.info(
        msg.format(
            user=user,
            document=filename,
            task=result_object.task_name,
            task_id=result_object.task_id,
        )
    )
    #
    # -- Here is where the real work begins --
    #

    log.info("Starting on %s for %s", result_object.filename(), company)

    sleep = kwargs.get("sleep", 0.001)

    items = 0

    if mimetypes.guess_type(filename) in [("text/x-c", None)]:
        lerrors = "Expected text file - I think this is binary!"
        result_log.update(errors=lerrors, raise_errors=True)
        return

    with io.open(filename, encoding="utf-8", errors="ignore") as f:
        results = f.readlines()

    for item in results:
        stat = "{}/{}".format(results.index(item) + 1, len(results))
        result_log.update(latest="{} Processing item".format(stat))
        number = random.randrange(1, 10)
        if number < 6:
            result_log.update(info=item.strip())
        elif number < 9:
            result_log.update(warnings=item.strip())
        items += 1
        time.sleep(sleep)
    if not len(result_log.get_errors()):
        result_log.update(latest="Successfully added {} items".format(items))
    #
    # -- End of real work --
    #

    msg = "Completed processing {document} for {company}"
    log.info(msg.format(document=result_object.filename(), company=company))
    return msg.format(document=result_object.filename(), company=company)


@shared_task(bind=True, time_limit=60 * 60)
def download_multiple_customer_documents_task(
    self, result_object_id: int, customer_documents_ids: List[int]
):
    task_meta = {"processing": {"current": 0, "total": 1}, "writing": {"current": 0, "total": 1}}

    self.update_state(state="STARTED", meta=task_meta)

    app_log = LogStorage(model_id=result_object_id)

    async_document = AsynchronousProcessedDocument.objects.get(id=result_object_id)
    customer_documents = CustomerDocument.objects.filter(id__in=customer_documents_ids)

    task_meta["processing"]["current"] = 1
    self.update_state(state="STARTED", meta=task_meta)

    today = timezone.now().today().strftime("%Y%m%d")
    filename = "all_documents_{}.zip".format(today)
    in_memory = io.BytesIO()
    zf = zipfile.ZipFile(in_memory, "w")
    # create empty folder
    zf.writestr(f"all_documents/", "")
    for customer_document in customer_documents:
        with default_storage.open(customer_document.document.file.name, "rb") as fh:
            app_log.info(f"Reading {os.path.split(fh.name)[1]}")
            name = os.path.join("all_documents", os.path.split(fh.name)[1])
            zf.writestr(name, fh.read())

    zf.close()
    app_log.info(f"Saving Zip file as {filename}")
    in_memory.seek(0)
    async_document.document.save(filename, ContentFile(in_memory.read(), name=filename))
    async_document.task_id = self.request.id
    async_document.save()

    task_meta["writing"]["current"] = 1
    self.update_state(state="DONE", meta=task_meta)
