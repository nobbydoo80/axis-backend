"""neea_calculator_v3.py - Axis"""

__author__ = "Steven K"
__date__ = "7/9/21 07:58"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from rest_framework.response import Response

from .neea_calculator_v2 import NEEACalculatorV2View
from .serializers.neea_calculator_v3 import NEEACalculatorV3Serializer

log = logging.getLogger(__name__)


class NEEACalculatorV3View(NEEACalculatorV2View):
    """THe NEEA Standard Protocol Calculator"""

    template_name = "customer_neea/neea_calculator_v3.html"

    @property
    def serializer(self):
        """Return the Serializer"""
        return NEEACalculatorV3Serializer

    def get_export_class(self):
        from axis.customer_neea.reports import NEEACalculatorV3EstimatorExport

        return NEEACalculatorV3EstimatorExport

    def get_response(self, serializer, calculator):
        return Response(
            {
                "serializer": serializer,
                "style": self.style,
                "result": calculator.result_data(),
                "hot_water_report": calculator.hot_water_report(),
                "appliance_report": calculator.appliance_report(),
                "thermostat_report": calculator.thermostat_report(),
                "heating_cooling_report": calculator.heating_cooling_report(),
                "incentive_report": calculator.incentives.report(),
                "total_report": calculator.total_report(),
                "summary": calculator.report(),
            }
        )


class NEEACalculatorV3DownloadView(NEEACalculatorV3View):
    """THe NEEA Standard Protocol Calculator Download"""

    def post(self, request, **kwargs):
        return self.get_download_report(request, **kwargs)
