"""searchs.py: customer aps"""


from appsearch.registry import ModelSearch, search
from .models import APSHome, LegacyAPSBuilder, LegacyAPSSubdivision, LegacyAPSHome

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class APSHomeSearch(ModelSearch):
    display_fields = (
        ("Premise ID", "premise_id"),
        ("Meter Set Date", "meterset_date"),
        ("Address", "raw_street_line_1"),
        ("City", "raw_city"),
        ("ZIP Code", "raw_zip"),
        ("Axis Home", "home__id"),
    )

    search_fields = (
        ("Premise ID", "premise_id"),
        ("Meter Set date", "meterset_date"),
        {"home": (("Axis Home (Lot Number)", "lot_number"),)},
        ("Address (APS)", "raw_street_line_1"),
        ("ZIP Code (APS)", "raw_zip"),
        ("Street (Google)", "street_line1"),
        {"city": (("City (Google)", "name"),)},
        "state",
        ("ZIP Code (Google)", "zipcode"),
    )


class LegacyAPSBuilderSearch(ModelSearch):
    display_fields = (
        ("Name", "builder__name"),
        ("Builder ID", "aps_id"),
        ("Street", "mail_addr1"),
        ("City", "mail_city"),
    )

    search_fields = (
        ("Builder ID (Legacy)", "aps_id"),
        {"builder": (("Builder Name (Legacy)", "name"),)},
        ("City", "mail_city"),
        ("ZIP Code", "mail_zip"),
        ("DBA Name (Legacy)", "dba"),
    )


class LegacyAPSSubdivisionSearch(ModelSearch):
    display_fields = (
        ("Name", "sub"),
        ("SubCode", "aps_id"),
        ("BuilderID", "legacy_builder__aps_id"),
        ("Community", "mstr_plan"),
    )

    search_fields = (
        ("Subdivision Name (Legacy)", "sub"),
        ("Subdivision ID (Legacy)", "aps_id"),
        ("Community", "mstr_plan"),
        {"legacy_builder": (("Builder ID (Legacy)", "aps_id"),)},
        ("Community (Legacy)", "mstr_plan"),
    )


class LegacyAPSHomeSearch(ModelSearch):
    display_fields = (
        ("Site ID", "aps_id"),
        ("No", "addr_no"),
        ("Dir", "addr_dir"),
        ("Name", "addr_name"),
        "dev",
        ("Subdivision", "legacy_subdivision__sub"),
        ("Builder", "legacy_builder__builder__name"),
    )

    search_fields = (
        ("Site ID", "aps_id"),
        ("Street Number", "addr_no"),
        ("Street Name", "addr_name"),
        ("Amount Paid", "amt_pd"),
        ("Paid Date", "pd_date"),
        ("Check Number", "ck_numb"),
        ("City", "lt_city"),
        ("ZIP Code", "lt_zip"),
        {
            "legacy_subdivision": (
                ("Subdivision Name (Legacy)", "sub"),
                ("Subdivision ID (Legacy)", "aps_id"),
            )
        },
        {"legacy_builder": (("Builder ID (Legacy)", "aps_id"),)},
        ("Match Axis Homes (set Exists)", "aps_home__home"),
    )


search.register(APSHome, APSHomeSearch)
search.register(LegacyAPSBuilder, LegacyAPSBuilderSearch)
search.register(LegacyAPSSubdivision, LegacyAPSSubdivisionSearch)
search.register(LegacyAPSHome, LegacyAPSHomeSearch)
