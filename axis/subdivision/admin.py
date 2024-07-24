"""admin.py: Django subdivision"""


import logging
from django.contrib import admin
from axis.geographic.admin import PlaceSaveMixin
from axis.relationship.admin import RelationshipTabularInline
from axis.subdivision.models import Subdivision

__author__ = "Steven Klass"
__date__ = "3/5/12 1:33 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SubdivisionAdmin(PlaceSaveMixin, admin.ModelAdmin):
    """Inline Document"""

    inlines = (RelationshipTabularInline,)
    list_display = ("pk", "city", "county", "state", "builder_org", "is_active")
    list_filter = (
        "created_date",
        "modified_date",
        "confirmed_address",
        "address_override",
        "use_sampling",
        "use_metro_sampling",
        "is_active",
        "state",
    )
    search_fields = ("name", "builder_name", "city__name", "state")
    raw_id_fields = ("city", "builder_org")
    exclude = ("geocode_response", "place")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("name", "builder_name"),
                    "builder_org",
                    "community",
                    ("cross_roads", "city"),
                    (
                        "confirmed_address",
                        "address_override",
                    ),
                )
            },
        ),
        (
            "Advanced options",
            {
                "classes": ("collapse",),
                "fields": (
                    "is_active",
                    ("latitude", "longitude"),
                    ("use_sampling", "use_metro_sampling"),
                    "county",
                ),
            },
        ),
    )


admin.site.register(Subdivision, SubdivisionAdmin)
