"""equipment.py: """

__author__ = "Artem Hruzd"
__date__ = "10/29/2019 22:22"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from django.contrib import admin
from axis.equipment.models import Equipment


class SponsorsInline(admin.TabularInline):
    model = Equipment.sponsors.through
    raw_id_fields = ("equipment", "company", "approver")


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    exclude = ("sponsors",)
    readonly_fields = ("expired_equipment",)
    inlines = (SponsorsInline,)
    raw_id_fields = ("owner_company", "assignees")
    search_fields = (
        "name",
        "brand",
        "equipment_model",
        "serial",
        "description",
        "calibration_company",
        "notes",
        "owner_company__name",
    )
    list_display = (
        "serial",
        "brand",
        "equipment_model",
        "owner_company",
        "updated_at",
        "created_at",
    )
    list_filter = ("equipment_type",)
