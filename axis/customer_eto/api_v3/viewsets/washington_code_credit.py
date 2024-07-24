"""washington_code_credit.py - Axis"""

__author__ = "Steven K"
__date__ = "10/18/21 12:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import io
import logging
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.text import slugify

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from axis.customer_eto.api_v3.serializers.reports.washington_code_credit import (
    WashingtonCodeCreditReportSerializer,
)
from axis.customer_eto.models import FastTrackSubmission
from axis.customer_eto.reports.washington_code_credit import WashingtonCodeCreditReport
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.customer_eto.tasks.washington_code_credit import (
    WashingtonCodeCreditBulkReportTask,
)

log = logging.getLogger(__name__)


class WCCReportViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    http_method_names = ["get", "options", "trace", "post"]

    @action(methods=["get"], detail=True, permission_classes=[IsAuthenticated])
    def report(self, request, pk):
        """Return the XML that is sent to Project Tracker"""
        instance = FastTrackSubmission.objects.get(home_status=pk)

        filename = f"WCCReport_{slugify(instance.home_status.home.street_line1)}.pdf"
        if instance.home_status.state == "complete":
            customer_document = instance.home_status.home.customer_documents.filter(
                document__contains="wacc_report"
            ).first()
            if customer_document:
                response = HttpResponse(
                    content=customer_document.document, content_type="application/pdf"
                )
                response["Content-Disposition"] = "attachment; filename={}".format(filename)
                return response

        serializer = WashingtonCodeCreditReportSerializer(instance=instance)
        virtual_workbook = io.BytesIO()

        report = WashingtonCodeCreditReport()
        report.build(response=virtual_workbook, user=request.user, data=serializer.data)

        response = HttpResponse(content=virtual_workbook.getvalue(), content_type="application/pdf")
        filename = f"WCCReport_{slugify(instance.home_status.home.street_line1)}.pdf"
        response["Content-Disposition"] = "attachment; filename={}".format(filename)
        return response

    @action(methods=["post"], detail=False, permission_classes=[IsAuthenticated])
    def bulk_report(self, request, *args, **kwargs):
        """Starts bulk export task and returns"""
        asynchronous_process_document = AsynchronousProcessedDocument(
            download=True, company=request.user.company
        )
        asynchronous_process_document.save()

        home_status_ids = request.POST.get("home_status_ids")
        WashingtonCodeCreditBulkReportTask.apply_async(
            [asynchronous_process_document.id, home_status_ids, request.user.id]
        )

        return HttpResponseRedirect(asynchronous_process_document.get_absolute_url())
