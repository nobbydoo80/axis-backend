# -*- coding: utf-8 -*-
"""customer_hirl_bulk_certificate.py: """

__author__ = "Artem Hruzd"
__date__ = "11/15/2022 00:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import tempfile
import zipfile

from celery import shared_task
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from axis.customer_hirl.api_v3.filters import HIRLProjectFilter
from axis.customer_hirl.reports.certificate import CustomerHIRLCertificate
from axis.filehandling.log_storage import LogStorage
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.home.api_v3.filters import EEPProgramHomeStatusFilter
from axis.home.models import EEPProgramHomeStatus

User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")


@shared_task(bind=True, time_limit=60 * 60 * 3)
def customer_hirl_bulk_certificate_task(self, user_id, result_object_id, query_params=None):
    if not query_params:
        query_params = {}

    task_meta = {
        "processing": {"current": 0, "total": 1},
        "writing": {"current": 0, "total": 1},
    }

    certificate_limit = 100

    self.update_state(state="STARTED", meta=task_meta)

    app_log = LogStorage(model_id=result_object_id)

    user = User.objects.get(id=user_id)

    async_document = AsynchronousProcessedDocument.objects.get(id=result_object_id)
    async_document.task_id = self.request.id
    async_document.task_name = self.name
    async_document.save()

    task_meta["processing"]["current"] = 1
    self.update_state(state="STARTED", meta=task_meta)

    queryset = EEPProgramHomeStatus.objects.filter_by_user(user=user).filter(
        state=EEPProgramHomeStatus.COMPLETE_STATE
    )
    filter_cls = EEPProgramHomeStatusFilter(data=query_params, queryset=queryset)
    queryset = filter_cls.qs

    queryset = queryset.select_related(
        "home",
        "eep_program",
        "customer_hirl_project",
        "customer_hirl_project__registration",
        "customer_hirl_project__registration__builder_organization",
        "customer_hirl_project__registration__developer_organization",
        "customer_hirl_project__registration__architect_organization",
        "customer_hirl_project__registration__community_owner_organization",
    )[:certificate_limit]

    app_log.info(f"Generating {queryset.count()} reports")

    with tempfile.SpooledTemporaryFile() as tmp:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as archive:
            for home_status in queryset:
                customer_hirl_certificate = CustomerHIRLCertificate(
                    home_status=home_status, user=user
                )
                output_stream = customer_hirl_certificate.generate()
                filename = customer_hirl_certificate.get_filename()
                archive.writestr(filename, output_stream.getvalue())
                task_meta["processing"]["current"] += 1
                self.update_state(state="STARTED", meta=task_meta)
        tmp.seek(0)
        app_log.info("Saving report")
        filename = "NGBS Bulk Certificate Download.zip"
        async_document.document.save(filename, ContentFile(tmp.read()))

    app_log.info("Done")
    task_meta["writing"]["current"] = 1
    self.update_state(state="DONE", meta=task_meta)
