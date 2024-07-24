"""urls.py: Django report"""


import logging

from django.urls import path, include

from .views import ECBReportView, SubdivisionReportList

__author__ = "Steven Klass"
__date__ = "3/3/12 5:56 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

app_name = "report"

urlpatterns = [
    path(
        "energy_costs/subdivision/",
        include(
            [
                path("", SubdivisionReportList.as_view(), name="subdivision"),
                path(
                    "<int:subdivision_id>/<int:company_id>/",
                    include(
                        [
                            path("", ECBReportView.as_view(), name="energy_cost"),
                            path("svg/", ECBReportView.as_view(svg=True), name="energy_cost_svg"),
                            path(
                                "svg/download/",
                                ECBReportView.as_view(svg=True, download=True),
                                name="energy_cost_svg_dl",
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ),
]
