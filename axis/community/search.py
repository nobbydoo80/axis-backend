"""search.py: Django search"""


from appsearch.registry import ModelSearch, search

from .models import Community

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class CommunitySearch(ModelSearch):
    display_fields = (
        "name",
        "cross_roads",
        "state",
    )

    search_fields = (
        "name",
        {
            "subdivision": (
                "name",
                "builder_name",
            )
        },
        {"county": ("name",)},
        {"metro": ("name",)},
        "cross_roads",
        {
            "relationships": (
                ("Company Name", "company__name"),
                ("Company Type", "company__company_type"),
            )
        },
    )


search.register(Community, CommunitySearch)
