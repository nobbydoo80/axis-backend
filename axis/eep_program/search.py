"""search.py: Search"""


from appsearch.registry import ModelSearch, search
from .models import EEPProgram

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class EEPProgramSearch(ModelSearch):
    display_fields = (
        ("Name", "name"),
        ("Min HERs Score", "min_hers_score"),
        ("Builder Incentive Amount", "builder_incentive_dollar_value"),
    )

    search_fields = (
        "name",
        "comment",
    )


search.register(EEPProgram, EEPProgramSearch)
