"""admin.py: Django incentive_payment"""


import logging

from django.contrib import admin

from axis.annotation.admin import AnnotationAdmin
from .models import IncentiveDistribution, IPPItem

__author__ = "Steven Klass"
__date__ = "10/11/12 2:46 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class IPPItemInline(admin.StackedInline):
    model = IPPItem
    fk_name = "incentive_distribution"
    readonly_fields = ("home_status",)
    extra = 0
    can_delete = False
    fieldsets = ((None, {"fields": (("home_status", "cost"))}),)


class IncentiveDistributionAdmin(admin.ModelAdmin):
    model = IncentiveDistribution
    list_display = ("invoice_number", "company", "customer", "status")
    search_fields = ("customer__name", "invoice_number", "customer__name")
    inlines = (IPPItemInline, AnnotationAdmin)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "company",
                    "invoice_number",
                    ("customer", "check_to_name"),
                    ("check_requested", "check_requested_date"),
                    ("is_paid", "paid_date"),
                    ("status", "check_number"),
                    ("total"),
                )
            },
        ),
        (
            "Advanced options",
            {
                "classes": ("collapse",),
                "fields": ("comment",),
            },
        ),
    )


admin.site.register(IncentiveDistribution, IncentiveDistributionAdmin)
