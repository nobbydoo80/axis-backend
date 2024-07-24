"""search.py: Incentive Payments"""


from appsearch.registry import ModelSearch, search

from .models import IncentiveDistribution, IPPItem, IncentivePaymentStatus

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class IncentiveDistributionSearch(ModelSearch):
    display_fields = (
        ("Invoice", "invoice_number"),
        ("Customer", "customer__name"),
        ("Customer Type", "customer__company_type"),
        ("Total Value", "total"),
    )

    search_fields = (
        {
            "customer": (
                "name",
                ("Cust. Type (builder/provider)", "company_type"),
            )
        },
        ("Invoice No", "invoice_number"),
        ("Chk Req Date", "check_requested_date"),
        "paid_date",
        ("Total Value", "total"),
        {
            "ippitem": (
                {
                    "home_status": (
                        {"home": ({"subdivision": ("name",)},)},
                        {"eep_program": (("Program", "name"),)},
                    )
                },
            )
        },
    )


class IPPItemSearch(ModelSearch):
    display_fields = (
        ("Invoice", "incentive_distribution__invoice_number"),
        ("Home", "home_status__home__lot_number"),
        ("Address", "home_status__home__street_line1"),
        ("Subdivision", "home_status__home__subdivision__name"),
        ("Program", "home_status__eep_program__name"),
        ("Customer", "incentive_distribution__customer__name"),
        ("Paid Date", "incentive_distribution__paid_date"),
        ("Amount", "cost"),
    )

    search_fields = (
        {
            "incentive_distribution": (
                {"customer": ("name", ("Cust. Type (builder/provider)", "company_type"))},
                ("Check Paid Date", "paid_date"),
            )
        },
        {
            "home_status": (
                {"eep_program": (("Program", "name"),)},
                {
                    "home": (
                        {"subdivision": ("name",)},
                        "lot_number",
                        ("Street Address", "street_line1"),
                    )
                },
            )
        },
        ("Amount Paid (Per Item)", "cost"),
    )


class IncentivePaymentStatusSearch(ModelSearch):
    display_fields = (
        ("Owner", "owner__name"),
        ("Project Program", "home_status__eep_program__name"),
        ("Date Created", "created_on"),
        ("Last Update", "last_update"),
    )

    search_fields = (
        {"owner": ("name",)},
        {"home_status": (("Program", "eep_program__name"),)},
        "created_on",
        "last_update",
    )


search.register(IncentiveDistribution, IncentiveDistributionSearch)
search.register(IPPItem, IPPItemSearch)
search.register(IncentivePaymentStatus, IncentivePaymentStatusSearch)
