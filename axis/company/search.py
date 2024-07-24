"""search.py: Django company"""


from appsearch.registry import ModelSearch, search

from axis.company.models import COMPANY_MODELS

__author__ = "Steven Klass"
__date__ = "01/31/2013 07:01"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class OrganizationSearch(ModelSearch):
    display_fields = (
        "name",
        "office_phone",
        ("Street", "street_line1"),
        ("City", "city__name"),
        ("State", "state"),
        ("ZIP Code", "zipcode"),
    )

    search_fields = (
        "name",
        ("Address", "street_line1"),
        ("Street Line 2", "street_line2"),
        {"city": (("City", "name"),)},
        "state",
        ("ZIP Code", "zipcode"),
    )


class HvacOrganizationSearch(OrganizationSearch):
    search_fields = (
        "name",
        ("Address", "street_line1"),
        ("Street Line 2", "street_line2"),
        {"city": (("City", "name"),)},
        "state",
        ("ZIP Code", "zipcode"),
        ("H-QUITO Accredited", "hquito_accredited"),
    )


# Skip over the base Company model
for company_model in COMPANY_MODELS[1:]:
    if company_model.COMPANY_TYPE == "hvac":
        search.register(company_model, HvacOrganizationSearch)
    else:
        search.register(company_model, OrganizationSearch)
