"""viewsets.py: """

import logging

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponseRedirect

from axis.customer_aps.api_v3.permissions import APSCompanyMemberPermission
from axis.customer_aps.tasks import export_custom_aps_home_data
from axis.filehandling.models import AsynchronousProcessedDocument

__author__ = "Rajesh Pethe"
__date__ = "08/31/2020 18:25:28"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
    "Steven Klass",
]

log = logging.getLogger(__name__)


class APSHomeDataExportViewSet(viewsets.ViewSet):
    """
    Viewset meant to kick start task for generating APS Home data.
    """

    permission_classes = (IsAuthenticated, APSCompanyMemberPermission)

    def list(self, request):
        company = request.user.company

        subdivision_id = request.query_params.get("subdivision", None)
        async_processed_document = AsynchronousProcessedDocument.objects.create(company=company)
        task = export_custom_aps_home_data.delay(
            result_object_id=async_processed_document.pk,
            user_id=request.user.id,
            subdivision_id=subdivision_id,
        )
        return HttpResponseRedirect(async_processed_document.get_absolute_url())
