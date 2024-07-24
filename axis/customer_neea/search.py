"""search.py: Django customer_neea search"""


from appsearch.registry import ModelSearch, search
from .models import (
    LegacyNEEAPartner,
    LegacyNEEAHome,
    LegacyNEEAInspection,
    LegacyNEEAInspectionIncentive,
    LegacyNEEAContact,
    StandardProtocolCalculator,
)

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class LegacyNEEAContactSearch(ModelSearch):
    """Search for legacy contacts"""

    display_fields = (
        ("First Name", "first_name"),
        ("Last Name", "last_name"),
        "email",
        ("Phone", "office_phone"),
    )

    search_fields = (
        ("First Name", "first_name"),
        ("Last Name", "last_name"),
        ("Title", "title"),
        ("Email", "email"),
        {"partner": (("Partner Name", "partner_name"),)},
    )


class LegacyNEEAPartnerSearch(ModelSearch):
    display_fields = (
        ("Name", "partner_name"),
        "address",
        ("Type", "partner_type"),
    )

    search_fields = (
        ("Name", "partner_name"),
        ("Type", "partner_type"),
        ("Utility Type", "utility_type"),
        {
            "address": (
                ("Lot Number", "lot_no"),
                ("Street Direction", "street_modifier"),
                ("Street Number", "county"),
                ("Street Name", "street_name"),
                ("County", "street_no"),
                ("ZIP Code", "zip_code"),
                ("Development Name", "development_name"),
            )
        },
        ("Years Experience", "builder_experience_years"),
        "active",
    )


class LegacyNEEAHomeSearch(ModelSearch):
    display_fields = (
        ("Site ID", "id"),
        ("Address", "address"),
        ("Start Date", "project_start_date"),
        ("Est. Completion Date", "estimated_completion_date"),
        "description",
    )

    search_fields = (
        ("Site ID", "id"),
        {
            "address": (
                ("Lot Number", "lot_no"),
                ("Street Direction", "street_modifier"),
                ("Street Number", "street_no"),
                ("Street Name", "street_name"),
                ("City", "zip_code__city"),
                ("County", "county"),
                ("ZIP Code", "zip_code__zip_code"),
                ("State", "zip_code__state"),
                ("Region", "zip_code__region__name"),
                ("Development Name", "development_name"),
            )
        },
        {"home_type": (("Home type", "name"),)},
        {
            "legacyneeainspection": (
                ("Certification Date", "certification_date"),
                {"bop": (("BOP", "name"),)},
            )
        },
        {"legacyneeapartnertohouse": ({"partner": (("Partner Name", "partner_name"),)},)},
        ("Utility Acct", "electric_utility_account_no"),
        ("Gas Acct", "gas_utility_account_no"),
        ("Start Date", "project_start_date"),
        ("Est. Completion Date", "estimated_completion_date"),
        "description",
    )


class LegacyNEEAInspectionSearch(ModelSearch):
    display_fields = (
        ("Home", "home__address"),
        ("Status", "status__status"),
        ("BOP", "bop__name"),
        "verification_date",
        "certification_date",
    )

    search_fields = (
        {
            "home": (
                {
                    "address": (
                        ("Lot Number", "lot_no"),
                        ("Street Direction", "street_modifier"),
                        ("Street Number", "street_no"),
                        ("Street Name", "street_name"),
                        ("City", "zip_code__city"),
                        ("County", "county"),
                        ("ZIP Code", "zip_code__zip_code"),
                        ("State", "zip_code__state"),
                        ("Region", "zip_code__region__name"),
                        ("Development Name", "development_name"),
                    )
                },
            )
        },
        {"bop_heat_source": (("Heat Source", "heat_source"),)},
        {"status": (("Status", "status"),)},
        "verification_date",
        "certification_date",
        {"bop": (("BOP", "name"),)},
        ("Inspection Notes", "bop_xml"),
    )


class LegacyNEEAInspectionIncentiveSearch(ModelSearch):
    display_fields = (
        ("Home", "inspection__home__address"),
        ("Incentive", "incentive__name"),
        ("BOP", "inspection__bop__name"),
        ("Certification Date", "inspection__certification_date"),
    )

    search_fields = (
        {"incentive": (("Incentive", "name"),)},
        {
            "inspection": (
                {
                    "home": (
                        {
                            "address": (
                                ("Home street number", "street_no"),
                                ("Home ZIP Code", "zip_code"),
                            )
                        },
                    )
                },
                ("Certification date", "certification_date"),
                {"bop": (("BOP", "name"),)},
            )
        },
        ("Model", "model"),
    )


class StandardProtocolCalculatorSearch(ModelSearch):
    display_fields = (
        ("Axis ID", "home_status__home__id"),
        ("Home", "home_status__home__street_line1"),
        ("% Improvement", "percent_improvement"),
        ("Program State", "home_status__state"),
        ("Certification Date", "home_status__certification_date"),
        ("BPA Incentive", "total_incentive"),
    )

    search_fields = (
        {
            "home_status": (
                {
                    "home": (
                        ("Lot Number", "lot_number"),
                        ("Street", "street_line1"),
                        {"city": (("City", "name"),)},
                        ("State", "state"),
                        {"subdivision": (("Subdivision", "name"),)},
                    )
                },
                ("Certification date", "certification_date"),
                ("Program State", "state"),
            )
        },
        ("% Improvement", "percent_improvement"),
        ("BPA Incentive", "total_incentive"),
    )


# search.register(LegacyNEEAContact, LegacyNEEAContactSearch)
# search.register(LegacyNEEAPartner, LegacyNEEAPartnerSearch)
# search.register(LegacyNEEAHome, LegacyNEEAHomeSearch)
search.register(LegacyNEEAInspection, LegacyNEEAInspectionSearch)
search.register(LegacyNEEAInspectionIncentive, LegacyNEEAInspectionIncentiveSearch)
# search.register(StandardProtocolCalculator, StandardProtocolCalculatorSearch)
