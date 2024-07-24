"""search.py builder agreement"""


from appsearch.registry import ModelSearch, search
from .models import BuilderAgreement

__author__ = "Steven Klass"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class BuilderAgreementSearch(ModelSearch):
    display_fields = (
        "id",
        ("Subdivision", "subdivision__name"),
        ("Builder", "subdivision__builder_org__name"),
        "start_date",
        "expire_date",
        "total_lots",
        "lots_paid",
    )

    search_fields = (
        {"builder_org": (("Builder", "name"),)},
        {"subdivision": ("name",)},
        {"eep_programs": (("Program", "name"),)},
        "start_date",
        "expire_date",
        "comment",
    )


search.register(BuilderAgreement, BuilderAgreementSearch)
