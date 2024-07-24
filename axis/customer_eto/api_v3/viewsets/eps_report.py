"""eps_report.py - Axis"""

__author__ = "Steven K"
__date__ = "9/23/21 15:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import io
import logging

from django.apps import apps
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from axis.customer_eto.api_v3.serializers.reports import (
    EPSReport2020Serializer,
    EPSReport2018Serializer,
    EPSReport2017Serializer,
    EPSReport2016Serializer,
    EPSReport2014Serializer,
    EPSReport2021Serializer,
    EPSReport2022Serializer,
    EPSReportLegacy2022Serializer,
)
from axis.customer_eto.models import FastTrackSubmission
from axis.customer_eto.reports import EPSLegacyReportGenerator, EPSReportGenerator
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)

app = apps.get_app_config("customer_eto")


def get_eps_report(pk, user, return_virtual_workbook=False):
    """Get the EPS Report"""
    instance = FastTrackSubmission.objects.get(home_status=pk)

    program_slug = instance.home_status.eep_program.slug

    meets_legacy_criteria = (
        instance.home_status.state == EEPProgramHomeStatus.COMPLETE_STATE
        and instance.home_status.certification_date
        and instance.home_status.certification_date < app.LEGACY_EPS_REPORT_CUTOFF_DATE
    )

    filename = f"EPSReport_{instance.home_status.home.street_line1.replace(' ', '_')}.pdf"

    if not return_virtual_workbook and instance.home_status.state == "complete":
        # We should have the document in our home documents.
        customer_document = instance.home_status.home.customer_documents.filter(
            document__contains="eps_report"
        ).first()
        if customer_document:
            response = HttpResponse(
                content=customer_document.document, content_type="application/pdf"
            )
            response["Content-Disposition"] = "attachment; filename={}".format(filename)
            return response

    if program_slug == "eto-2022":
        serializer = EPSReport2022Serializer(instance=instance)
        if meets_legacy_criteria:
            serializer = EPSReportLegacy2022Serializer(instance=instance)
    elif program_slug in ["eto-2021", "eto-fire-2021"]:
        serializer = EPSReport2021Serializer(instance=instance)
    elif program_slug == "eto-2020":
        serializer = EPSReport2020Serializer(instance=instance)
    elif program_slug in ["eto-2019", "eto-2018"]:
        serializer = EPSReport2018Serializer(instance=instance)
    elif program_slug == "eto-2017":
        serializer = EPSReport2017Serializer(instance=instance)
    elif program_slug == "eto-2016":
        serializer = EPSReport2016Serializer(instance=instance)
    elif program_slug in ["eto", "eto-2015"]:
        serializer = EPSReport2014Serializer(instance=instance)
    else:
        raise ValidationError(f"Unable to get Serializer from {program_slug}")

    virtual_workbook = io.BytesIO()

    eps_report_kwargs = {
        "return_document": False,
        "left_margin": 0.4,
        "right_margin": 8.1,
    }

    legacy_programs = [
        "eto",
        "eto-2015",
        "eto-2016",
        "eto-2017",
        "eto-2019",
        "eto-2018",
        "eto-2020",
        "eto-2021",
        "eto-fire-2021",
    ]

    if instance.home_status.eep_program.slug in legacy_programs or meets_legacy_criteria:
        report = EPSLegacyReportGenerator(**eps_report_kwargs)
    else:
        report = EPSReportGenerator()

    report.build(response=virtual_workbook, user=user, **serializer.data)

    if return_virtual_workbook:
        return virtual_workbook, filename

    response = HttpResponse(content=virtual_workbook.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename={}".format(filename)
    return response


class EPSReportViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    http_method_names = ["get", "options", "trace"]

    @action(methods=["get"], detail=True, permission_classes=[IsAuthenticated])
    def report(self, request, pk):
        """Return the XML that is sent to Project Tracker"""
        return get_eps_report(pk, request.user)
