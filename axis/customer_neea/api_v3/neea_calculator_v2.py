"""neea_calculator_v2.py - Axis"""

__author__ = "Steven K"
__date__ = "7/9/21 07:58"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging

from django.http import HttpResponse
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import NEEACalculatorPermission
from .serializers.neea_calculator_v2 import (
    NEEACalculatorV2Serializer,
)

log = logging.getLogger(__name__)


class NEEACalculatorV2View(APIView):
    """THe NEEA Standard Protocol Calculator"""

    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    permission_classes = (NEEACalculatorPermission,)
    template_name = "customer_neea/neea_calculator_v2.html"
    style = {"template_pack": "rest_framework/vertical/"}

    @property
    def serializer(self):
        """Return the Serializer"""
        return NEEACalculatorV2Serializer

    def get(self, request, **kwargs):
        """Override the default get"""
        serializer = self.serializer()
        return Response({"serializer": serializer, "style": self.style})

    def get_response(self, serializer, calculator):
        return Response(
            {
                "serializer": serializer,
                "style": self.style,
                "result": calculator.result_data(),
                "hot_water_report": calculator.hot_water_report(),
                "lighting_report": calculator.lighting_report(),
                "appliance_report": calculator.appliance_report(),
                "thermostat_report": calculator.thermostat_report(),
                "shower_head_report": calculator.shower_head_report(),
                "heating_cooling_report": calculator.heating_cooling_report(),
                "incentive_report": calculator.incentives.report(),
                "total_report": calculator.total_report(),
                "summary": calculator.report(),
            }
        )

    def get_export_class(self):
        from axis.customer_neea.reports import NEEACalculatorV2EstimatorExport

        return NEEACalculatorV2EstimatorExport

    def get_download_report(self, request, **kwargs):
        serializer = self.serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"serializer": serializer, "style": self.style, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        calculator = serializer.save()

        export_class = self.get_export_class()

        report = export_class(user=self.request.user, company=self.request.user.company)
        label = "BetterBuiltNW-Performance-Path-Estimate-{}".format(
            datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        )
        workbook = report.write(
            input_data=request.data, result=calculator.result_data(), return_workbook=True
        )

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = "attachment; filename={}.xlsx".format(label)
        workbook.save(response)
        return response

    def post(self, request, **kwargs):
        """Override the default post"""
        serializer = self.serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"serializer": serializer, "style": self.style, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        calculator = serializer.save()

        # We just reinitialize it.  This ensures that if the calculator does anything we
        # are good with what we put in. It was validated 3 lines ago..
        serializer = self.serializer(data=request.data)
        serializer.is_valid()

        return self.get_response(serializer, calculator)


class NEEACalculatorV2DownloadView(NEEACalculatorV2View):
    """THe NEEA Standard Protocol Calculator Download"""

    def post(self, request, **kwargs):
        return self.get_download_report(request, **kwargs)
