"""admin.py: Django community"""


import logging

from django.contrib import admin
from axis.geographic.admin import PlaceSaveMixin

from axis.relationship.admin import RelationshipTabularInline
from .models import Community

__author__ = "Steven Klass"
__date__ = "3/5/12 1:32 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CommunityAdmin(PlaceSaveMixin, admin.ModelAdmin):
    model = Community
    inlines = (RelationshipTabularInline,)
    search_fields = ["name", "cross_roads", "city__name", "state"]
    list_filter = ["state"]
    raw_id_fields = ("city",)
    exclude = ("geocode_response", "place")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "website",
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
                "fields": ("is_active", ("latitude", "longitude"), "county", "slug"),
            },
        ),
    )


admin.site.register(Community, CommunityAdmin)
