"""admin.py: Django geocoder"""


from django.contrib import admin

from .models import Geocode, GeocodeResponse

__author__ = "Peter Landry"
__date__ = "12/4/13 5:47 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Peter Landry",
]


class GeocodeResponseInline(admin.TabularInline):
    model = GeocodeResponse
    extra = 0


class GeocodeAdmin(admin.ModelAdmin):
    date_hierarchy = "created_date"
    inlines = [GeocodeResponseInline]
    list_display = ("raw_address", "entity_type")
    list_filter = ("entity_type", "created_date", "modified_date")
    search_fields = ("raw_address",)
    raw_id_fields = ("raw_city",)


class GeocodeResponseAdmin(admin.ModelAdmin):
    date_hierarchy = "created_date"
    list_display = ("geocode", "engine", "created_date")
    list_filter = ("engine", "created_date")
    raw_id_fields = ("geocode",)
    search_fields = ("place",)


admin.site.register(Geocode, GeocodeAdmin)
admin.site.register(GeocodeResponse, GeocodeResponseAdmin)
