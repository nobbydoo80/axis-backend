"""client.py: """

__author__ = "Artem Hruzd"
__date__ = "05/03/2022 19:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from django.contrib import admin
from django.contrib.admin.decorators import register

from axis.customer_hirl.models import HIRLCompanyClient


@register(HIRLCompanyClient)
class HIRLCompanyClientAdmin(admin.ModelAdmin):
    raw_id_fields = ("company",)
    list_display = ("id", "company", "get_company_type", "updated_at", "created_at")
    search_fields = ("id", "company__id", "company__name")

    def get_queryset(self, request):
        return super(HIRLCompanyClientAdmin, self).get_queryset(request).select_related("company")

    @admin.display(ordering="company__company_type", description="Company type")
    def get_company_type(self, obj):
        return obj.company.company_type
