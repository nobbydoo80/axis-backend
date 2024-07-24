"""builder_program_metrics.py: """

from drf_yasg import openapi

from axis.core.api_v3.schema.axis import AxisSchema
from axis.core.api_v3.options import AxisFrontEndOptions

__author__ = "Rajesh Pethe"
__date__ = "09/21/2020 14:51:44"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
    "Steven Klass",
]


class MetricsAutoSchema(AxisSchema):
    def add_manual_parameters(self, parameters=None):
        manual_parameters = [
            openapi.Parameter(
                "date_start",
                required=True,
                description="Date Created is greater then or equal",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
            ),
            openapi.Parameter(
                "date_end",
                required=True,
                description="Date Created is less then or equal",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
            ),
            openapi.Parameter(
                "us_state",
                required=False,
                description="State abbr",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
            ),
            openapi.Parameter(
                "utility",
                required=False,
                description="Utility company ID",
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
            ),
            openapi.Parameter(
                "style",
                required=False,
                description="Group results by Rater or Utility",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
            ),
        ]
        return manual_parameters

    def get_operation(self, operation):
        if self.request.user.is_superuser:
            return super(MetricsAutoSchema, self).get_operation(operation)
        frontend_options = AxisFrontEndOptions(request=self.request, view=self.view)
        available_elements = frontend_options.get_available_elements()

        return super(MetricsAutoSchema, self).get_operation(operation)


class BuilderMetricsAutoSchema(MetricsAutoSchema):
    def add_manual_parameters(self, parameters=None):
        manual_parameters = []
        if self.view.action == "home_status_metrics":
            manual_parameters += [
                openapi.Parameter(
                    "created_date__gte",
                    required=False,
                    description="Date Created is greater then or equal",
                    type=openapi.TYPE_STRING,
                    in_=openapi.IN_QUERY,
                ),
                openapi.Parameter(
                    "created_date__lte",
                    required=False,
                    description="Date Created is less then or equal",
                    type=openapi.TYPE_STRING,
                    in_=openapi.IN_QUERY,
                ),
            ]
        else:
            manual_parameters += [
                openapi.Parameter(
                    "certification_date__gte_or_isnull",
                    required=False,
                    description="Date Certification is greater then or equal",
                    type=openapi.TYPE_STRING,
                    in_=openapi.IN_QUERY,
                ),
                openapi.Parameter(
                    "certification_date__lte_or_isnull",
                    required=False,
                    description="Date Certification is less then or equal",
                    type=openapi.TYPE_STRING,
                    in_=openapi.IN_QUERY,
                ),
            ]

        manual_parameters += [
            openapi.Parameter(
                "us_state",
                required=False,
                description="State abbr",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
            ),
            openapi.Parameter(
                "utility",
                required=False,
                description="Utility company ID",
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_QUERY,
            ),
        ]
        return manual_parameters
