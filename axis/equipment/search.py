"""search.py: Search"""


from appsearch.registry import ModelSearch, search

from axis.equipment.models import Equipment

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class EquipmentSearch(ModelSearch):
    display_fields = (
        ("Company", "owner_company"),
        ("Brand", "brand"),
        ("Model", "equipment_model"),
        ("Serial", "serial"),
    )
    search_fields = (
        "brand",
        "equipment_model",
        "serial",
        "calibration_company",
        {"owner_company": ("name",)},
        {"sponsors": ("name",)},
    )

    def user_has_perm(self, user):
        return True


search.register(Equipment, EquipmentSearch)
