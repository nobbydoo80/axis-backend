"""searchs.py: Geographic"""


from appsearch.registry import ModelSearch, search
from .models import City

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class CitySearch(ModelSearch):
    display_fields = (
        ("City", "name"),
        ("County", "county__name"),
        ("Metro", "county__metro__name"),
        ("state", "county__state"),
    )

    search_fields = (
        ("Name", "name"),
        {
            "county": (
                "name",
                {"metro": ("name",)},
                "state",
            )
        },
    )


search.register(City, CitySearch)
