"""admin.py: Django geographic"""

__author__ = "Steven Klass"
__date__ = "10/8/11 10:43 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]


import logging

from django.contrib import admin

from django.contrib.admin.decorators import register
from axis.geographic.utils.legacy import do_blind_geocode
from .models import Place, Metro, County, City, USState, Country


log = logging.getLogger(__name__)


@register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("pk", "city", "county", "state", "confirmed_address", "geocode_response")
    list_filter = ("confirmed_address", "address_override")
    raw_id_fields = ("geocode_response", "city", "county", "metro", "climate_zone")


class PlaceSaveMixin(object):
    def save_model(self, request, obj, form, change):
        # This will correctly link up the Place / Target object
        if form.cleaned_data.get("address_override"):
            log.debug("Removing Geocoding")
            if obj.geocode_response:
                obj.geocode_response = None
            if obj.place:
                obj.place = None
            obj.save(saved_from_place=True)  # All this is doing is not forcing update Home Obj.
            obj.update_to_place()
        else:
            log.debug("Re-Geocoding %s" % form.cleaned_data)
            obj = do_blind_geocode(obj, **form.cleaned_data)
            obj.save()


@register(Metro)
class MetroAdmin(admin.ModelAdmin):
    ordering = [
        "name",
    ]
    search_fields = ["name"]


@register(County)
class CountyAdmin(admin.ModelAdmin):
    ordering = [
        "state",
        "name",
    ]
    search_fields = ["name", "state", "county_fips"]
    list_filter = ["state"]
    list_display = ("name", "state")


@register(City)
class CityAdmin(admin.ModelAdmin):
    ordering = [
        "county",
        "name",
    ]
    search_fields = ["name", "county__name", "county__state", "place_fips"]
    list_filter = ["county__state", "country"]
    list_display = (
        "name",
        "_county",
        "state",
        "country",
    )
    raw_id_fields = ("county", "country", "geocode_response")

    def _county(self, instance):
        if instance.county:
            return f"{instance.county.name}"


@register(USState)
class USStateAdmin(admin.ModelAdmin):
    list_display = ("abbr", "name")
    search_fields = ("name",)


@register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("abbr", "name")
    search_fields = ("id", "abbr", "name")
