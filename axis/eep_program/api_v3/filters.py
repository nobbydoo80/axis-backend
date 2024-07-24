"""filters.py: """

__author__ = "Artem Hruzd"
__date__ = "07/07/2020 13:11"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps
from django_filters import rest_framework as filters

from axis.eep_program.api_v3 import EEP_PROGRAM_FILTER_FIELDS
from axis.eep_program.models import EEPProgram


customer_hirl_app = apps.get_app_config("customer_hirl")


class EEPProgramSetChoiceFilter(filters.ChoiceFilter):
    """
    Return special list of programs for Customers with additional criteria
    """

    def __init__(self, *args, **kwargs):
        kwargs["choices"] = [
            ("", "All"),
            ("hirl_project_sf_programs", "Customer HIRL Single Family EEP Programs"),
            ("hirl_project_mf_programs", "Customer HIRL Multi Family EEP Programs"),
            ("customer_hirl_land_development", "Customer HIRL Land Development EEP Programs"),
        ]
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value == "hirl_project_sf_programs":
            qs = qs.filter(
                slug__in=customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SF_NEW_CONSTRUCTION_SLUGS
                + customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SF_REMODEL_SLUGS
                + customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_WRI_SF_SLUGS
                + customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SF_CERTIFIED_SLUGS
            )
        elif value == "hirl_project_mf_programs":
            qs = qs.filter(
                slug__in=customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_MF_NEW_CONSTRUCTION_SLUGS
                + customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_MF_REMODEL_SLUGS
                + customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_WRI_MF_SLUGS
            )
        elif value == "customer_hirl_land_development":
            qs = qs.filter(slug__in=customer_hirl_app.LAND_DEVELOPMENT_PROGRAM_LIST)
        return qs


class EEPProgramFilter(filters.FilterSet):
    set = EEPProgramSetChoiceFilter(
        help_text="Return special list of programs for Customers with complex criteria"
    )

    class Meta:
        model = EEPProgram
        fields = EEP_PROGRAM_FILTER_FIELDS
