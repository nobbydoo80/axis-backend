"""company_role.py: """

__author__ = "Artem Hruzd"
__date__ = "02/22/2023 00:23"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from django.contrib import admin

from axis.company.models import CompanyRole


@admin.register(CompanyRole)
class CompanyRoleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
    )
    search_fields = ("id", "name", "slug")
