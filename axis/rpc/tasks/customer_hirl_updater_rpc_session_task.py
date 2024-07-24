# -*- coding: utf-8 -*-
"""customer_hirl_updater_rpc_session_task.py: """

__author__ = "Artem Hruzd"
__date__ = "11/20/2022 20:01"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import os
import time

import rpyc
from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.conf import settings
from django.utils import timezone

from axis.filehandling.log_storage import LogStorage
from axis.rpc.models import RPCService, RPCSession, HIRLRPCUpdaterRequest

User = get_user_model()


def on_failure(self, exc, task_id, args, kwargs, einfo):
    """
    Log failures and hard time limits.
    """

    hirl_rpc_updater_request_id = kwargs["hirl_rpc_updater_request_id"]

    hirl_rpc_updater_request = HIRLRPCUpdaterRequest.objects.get(id=hirl_rpc_updater_request_id)

    hirl_rpc_updater_request.state = HIRLRPCUpdaterRequest.ERROR_STATE
    hirl_rpc_updater_request.save()

    rpc_session = hirl_rpc_updater_request.rpc_session
    if rpc_session:
        rpc_session.state = RPCSession.ERROR_STATE
        rpc_session.finished_at = timezone.now()
        rpc_session.save()

    app_log = LogStorage(
        model_name="rpc.HIRLRPCUpdaterRequest", model_id=hirl_rpc_updater_request.id
    )
    app_log.error(exc)


# every request takes about 10 minutes, so with time_limit=60 minutes we can perform 6 requests for 1 instance
@shared_task(bind=True, time_limit=60 * 60, on_failure=on_failure)
def customer_hirl_updater_rpc_session_task(self, hirl_rpc_updater_request_id: int):
    task_meta = {"processing": {"current": 0, "total": 1}, "writing": {"current": 0, "total": 1}}

    self.update_state(state="STARTED", meta=task_meta)

    hirl_rpc_updater_request = HIRLRPCUpdaterRequest.objects.get(id=hirl_rpc_updater_request_id)
    hirl_rpc_updater_request.task_id = self.request.id
    hirl_rpc_updater_request.save()

    app_log = LogStorage(
        model_name="rpc.HIRLRPCUpdaterRequest", model_id=hirl_rpc_updater_request.id
    )

    task_meta["processing"]["current"] = 1
    self.update_state(state="STARTED", meta=task_meta)

    with transaction.atomic():
        rpc_service = None
        while not rpc_service:
            rpc_service = RPCService.objects.free().select_for_update().first()
            if rpc_service:
                rpc_session = RPCSession.objects.create(
                    service=rpc_service,
                    session_type=RPCSession.CUSTOMER_HIRL_UPDATER_SERVICE_TYPE,
                    state=RPCSession.IN_PROGRESS_STATE,
                )
                hirl_rpc_updater_request.rpc_session = rpc_session
                hirl_rpc_updater_request.save()
            else:
                if settings.CELERY_TASK_ALWAYS_EAGER:
                    # raise exception in case of local testing
                    raise Exception("No free RPC Service. Waiting 10 sec.")

                app_log.info("No free RPC Service. Waiting 10 sec.")
                time.sleep(10)

    app_log.info("Connect to VM")
    updater_service = rpyc.connect(rpc_session.service.host, rpc_session.service.port)
    updater_service._config["sync_request_timeout"] = 60 * 10  # 10 min
    with default_storage.open(hirl_rpc_updater_request.document.file.name, "rb") as f:
        app_log.info("Running updater")
        scoring_path = (
            f"{hirl_rpc_updater_request.scoring_path}_{hirl_rpc_updater_request.project_type}"
        )

        outfile = updater_service.root.upload(contents=f.read(), scoring_path=scoring_path)

    filename = os.path.basename(hirl_rpc_updater_request.document.file.name)

    app_log.info("Saving result")
    hirl_rpc_updater_request.result_document.save(filename, ContentFile(outfile, name=filename))

    hirl_rpc_updater_request.state = HIRLRPCUpdaterRequest.SUCCESS_STATE
    hirl_rpc_updater_request.save()

    rpc_session.state = RPCSession.SUCCESS_STATE
    rpc_session.finished_at = timezone.now()
    rpc_session.save()

    task_meta["writing"]["current"] = 1
    self.update_state(state="DONE", meta=task_meta)
