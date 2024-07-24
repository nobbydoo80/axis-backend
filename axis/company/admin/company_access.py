__author__ = "Artem Hruzd"
__date__ = "02/22/2023 00:23"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib import admin

from axis.company.models import CompanyAccess


@admin.register(CompanyAccess)
class CompanyAccessAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "company",
        "user",
    )
    raw_id_fields = (
        "company",
        "user",
    )
    search_fields = (
        "id",
        "company__name",
        ("user__first_name", "user__last_name"),
        "user__username",
    )
    list_filter = ("roles",)
    filter_horizontal = ("roles",)


class CompanyAccessInlineAdmin(admin.TabularInline):
    model = CompanyAccess
    extra = 0
    raw_id_fields = (
        "company",
        "user",
    )
    filter_horizontal = ("roles",)
