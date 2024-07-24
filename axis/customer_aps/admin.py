"""admin.py: Django customer_aps"""


from django.contrib import admin

from axis.customer_aps.models import APSHome
from axis.home.models import Home

__author__ = "Steven Klass"
__date__ = "8/7/13 9:19 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class APSHomeAdmin(admin.ModelAdmin):
    """Set company admin options and functionality for a given model."""

    ordering = [
        "premise_id",
    ]
    search_fields = ["premise_id", "raw_street_number", "city__name", "state"]
    list_display = (
        "premise_id",
        "raw_street_number",
        "raw_prefix",
        "raw_street_name",
        "raw_suffix",
        "raw_city",
        "raw_zip",
        "confirmed_address",
        "address_override",
    )
    list_filter = ["confirmed_address", "raw_city"]
    raw_id_fields = ("city", "home")
    exclude = ("county", "place", "geocode_response")

    def formfield_for_dbfield(self, db_field, **kwargs):
        """Get the right queryset"""
        if db_field.name == "home":
            kwargs["queryset"] = Home.objects.filter(apshome__isnull=True, state="AZ")
        return super(APSHomeAdmin, self).formfield_for_dbfield(db_field, **kwargs)


admin.site.register(APSHome, APSHomeAdmin)
