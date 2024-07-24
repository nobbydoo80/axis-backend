"""admin.py: Django floorplan"""


import logging

from django.contrib import admin

from axis.relationship.admin import RelationshipTabularInline
from axis.subdivision.models import FloorplanApproval
from .models import Floorplan

__author__ = "Steven Klass"
__date__ = "3/3/12 5:47 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class FloorplanApprovalInline(admin.TabularInline):
    model = FloorplanApproval
    # fk_name =
    extra = 0


class FloorplanAdmin(admin.ModelAdmin):
    """Floorplan Admin"""

    model = Floorplan
    raw_id_fields = ("remrate_target", "owner", "ekotrope_houseplan", "simulation")
    search_fields = ["owner__name", "name", "slug", "id"]
    list_display = ("id", "name", "remrate_target")
    inlines = (
        RelationshipTabularInline,
        FloorplanApprovalInline,
    )


admin.site.register(Floorplan, FloorplanAdmin)
