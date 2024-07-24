"""admin.py: Django remrate"""


import logging
from django.contrib import admin
from axis.remrate.models import RemRateUser, RemRateAccount

__author__ = "Steven Klass"
__date__ = "9/19/11 2:26 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]

log = logging.getLogger(__name__)


class RemRateAccountAdmin(admin.ModelAdmin):
    """Set company admin options and functionality for a given model."""

    model = RemRateAccount
    ordering = [
        "company",
    ]
    search_fields = [
        "company",
        "username",
    ]
    readonly_fields = ("expires", "account_type", "last_validated")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("company", "export_user_account"),
                    ("username", "password"),
                    ("resnet_user_id", "resnet_password"),
                    ("account_type", "expires", "last_validated"),
                )
            },
        ),
    )


admin.site.register(RemRateUser, admin.ModelAdmin)
admin.site.register(RemRateAccount, RemRateAccountAdmin)
