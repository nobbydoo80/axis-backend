"""search.py: Django sampleset"""


import logging
from appsearch.registry import ModelSearch, search
from .models import SampleSet

__author__ = "Steven Klass"
__date__ = "9/11/14 1:11 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SampleSetSearch(ModelSearch):
    display_fields = (
        ("Name", "uuid"),
        "alt_name",
        ("Program", "home_statuses__eep_program__name"),
        ("Home", "home_statuses__home"),
    )

    search_fields = (
        {"owner": ("name",)},
        "alt_name",
        "uuid",
        {
            "home_statuses": (
                {
                    "home": (
                        ("Street", "street_line1"),
                        {"city": ("name",)},
                    )
                },
                {"eep_program": (("Program", "name"),)},
            )
        },
    )


search.register(SampleSet, SampleSetSearch)
