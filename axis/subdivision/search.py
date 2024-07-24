"""search.py: Subdivision"""


from appsearch.registry import ModelSearch, search
from .models import Subdivision

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class SubdivisionSearch(ModelSearch):
    display_fields = (
        "name",
        "builder_name",
        ("Community", "community__name"),
        "cross_roads",
        "state",
        ("Builder", "builder_org__name"),
    )

    search_fields = (
        "name",
        "builder_name",
        {"community": ("name",)},
        {"county": ("name",)},
        {"metro": ("name",)},
        "cross_roads",
        {"builder_org": (("Builder", "name"),)},
        {"climate_zone": (("Climate Zone", "zone"),)},
        ("Builder Agreement", "builderagreement"),
        {
            "relationships": (
                ("Company Name", "company__name"),
                ("Company Type", "company__company_type"),
            )
        },
    )


search.register(Subdivision, SubdivisionSearch)
