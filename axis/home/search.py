"""search.py: Django home"""


from appsearch.registry import ModelSearch, search

from .models import Home, EEPProgramHomeStatus

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class HomeSearch(ModelSearch):
    display_fields = (
        "lot_number",
        ("Subdivision/MF Development", "subdivision__name"),
        ("Address", "street_line1"),
        "city",
    )

    search_fields = (
        "lot_number",
        {"subdivision": (("Subdivision/MF Development", "name"),)},
        ("Address", "street_line1"),
        ("As entered Address", "geocode_response__geocode__raw_street_line1"),
        ("Street Line 2", "street_line2"),
        {"city": ("name",)},
        {"subdivision": ({"community": ("name",)},)},
        {"county": (("County", "name"),)},
        {"metro": (("Metro", "name"),)},
        {"eep_programs": (("Program name", "name"),)},
        {
            "homestatuses": (
                ("Certification date", "certification_date"),
                ("% Complete", "pct_complete"),
                {"floorplan": ("name",)},
                {"company": (("Rater", "name"),)},
                ("Program State", "state"),
            )
        },
        {"eep_programs": ({"required_checklists": (("Checklist", "name"),)},)},
        # Misc
        ("Confirmed Address", "confirmed_address"),
        ("Custom Home", "is_custom_home"),
        ("Axis ID", "id"),
        {
            "annotations": (
                {"type": (("Annotation type", "name"),)},
                ("Annotation value", "content"),
            )
        },
        {
            "relationships": (
                ("Company Name", "company__name"),
                ("Company Type", "company__company_type"),
            )
        },
    )


class EEPProgramHomeStatusSearch(ModelSearch):
    display_fields = (
        ("Project", "home__street_line1"),
        ("Subdivision/MF Development", "home__subdivision__name"),
        ("Floorplan", "floorplan__name"),
        ("Program State", "state"),
        # ('Sample Set', 'samplesets__slug'),
        ("Certification Date", "certification_date"),
    )

    search_fields = (
        {
            "home": (
                ("Lot Number", "lot_number"),
                ("Street", "street_line1"),
                {"city": (("City", "name"),)},
                {"subdivision": (("Subdivision/MF Development", "name"),)},
            )
        },
        {"eep_program": (("Program", "name"),)},
        {"floorplan": ("name",)},
        "certification_date",
        ("Program State", "state"),
        "pct_complete",
        {"company": (("Rater/Provider", "name"),)},
    )


search.register(Home, HomeSearch)
search.register(EEPProgramHomeStatus, EEPProgramHomeStatusSearch)
