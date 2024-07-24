"""admin.py: Django resnet"""


import logging
from django.contrib import admin
from .models import RESNETContact, RESNETCompany

__author__ = "Steven Klass"
__date__ = "7/25/14 9:53 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class RESNETContactInline(admin.TabularInline):
    """Admin for RESNET Inline Contact"""

    model = RESNETContact
    fields = ["name", "title", "email"]


class RESNETCompanyAdmin(admin.ModelAdmin):
    """Set company admin options and functionality for a given model."""

    ordering = [
        "name",
    ]
    search_fields = ["name", "city", "state"]
    list_display = (
        "name",
        "state",
        "is_provider",
        "is_sampling_provider",
        "is_training_provider",
        "is_watersense_provider",
        "is_active",
    )
    list_filter = ["state"]

    inlines = (RESNETContactInline,)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "street_line1",
                    "street_line2",
                    "city",
                    "state",
                    "zipcode",
                    ("office_phone", "office_fax"),
                    ("provider_id", "resnet_expiration"),
                    ("company",),
                    (
                        "is_provider",
                        "is_sampling_provider",
                        "is_training_provider",
                        "is_watersense_provider",
                        "is_active",
                    ),
                )
            },
        ),
    )


admin.site.register(RESNETCompany, RESNETCompanyAdmin)
