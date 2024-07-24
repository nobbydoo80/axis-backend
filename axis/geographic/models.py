"""models.py: Django geographic"""


import logging
from functools import cached_property

import pytz
from django.apps import apps
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from localflavor.us.models import USStateField

from . import strings
from .managers import ClimateZoneManager, CountyManager, MetroManager, CityManager
from .managers import CountryQuerySet
from .strings import COUNTY_TYPES, DOE_MOISTURE_REGIMES
from .utils.country import get_usa_default
from .utils.legacy import (
    denormalize_related_references,
    save_geocoded_model,
    load_geocode_response_data,
    format_geographic_input,
)

__author__ = "Steven Klass"
__date__ = "10/8/11 9:13 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]

log = logging.getLogger(__name__)
app = apps.get_app_config("geocoder")

COUNTRIES = dict(pytz.country_names)
EXTENDED_COUNTRY_NAMES = {
    "us virgin islands": "VI",
    "u.s. virgin islands": "VI",
    "saint lucia": "LC",
}

SUPPORTED_COUNTRIES = {k: v for k, v in COUNTRIES.items() if k in app.SUPPORTED_COUNTRIES}


class Place(models.Model):
    """
    Container for all geocoded information for a model.  Fields may be null if they don't apply to
    the underlying object, but ALL possible fields must be present here for field synchronization
    to work.

    """

    geocode_response = models.ForeignKey(
        "geocoder.GeocodeResponse",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="place_set",
        help_text=strings.PLACE_HELP_TEXT_GEOCODE_RESPONSE,
    )

    lot_number = models.CharField(max_length=64, blank=True, null=True)
    street_line1 = models.CharField(max_length=100, blank=True, null=True)
    street_line2 = models.CharField(max_length=100, blank=True, null=True)
    zipcode = models.CharField("ZIP Code", max_length=15, blank=True, null=True)
    city = models.ForeignKey(
        "geographic.City",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="place_set",
        help_text=strings.PLACE_HELP_TEXT_CITY,
    )
    county = models.ForeignKey("geographic.County", on_delete=models.CASCADE, blank=True, null=True)

    cross_roads = models.CharField(
        max_length=128, blank=True, help_text=strings.PLACE_HELP_TEXT_CROSS_ROADS
    )

    state = USStateField(null=True, editable=False)
    metro = models.ForeignKey(
        "geographic.Metro", on_delete=models.CASCADE, editable=False, null=True
    )
    climate_zone = models.ForeignKey(
        "geographic.ClimateZone", on_delete=models.CASCADE, editable=False, blank=True, null=True
    )
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    is_multi_family = models.BooleanField(
        default=False,
        verbose_name=strings.PLACEDMODEL_VERBOSE_NAME_MULTI_FAMILY,
        help_text=strings.PLACE_HELP_TEXT_MULTI_FAMILY,
    )
    confirmed_address = models.BooleanField(default=False)
    address_override = models.BooleanField(default=False)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Place"

    def __str__(self):
        # Not the most performant thing, but it is helfpul during development,
        # and will likely not cause any issue with real-world production use.
        address, raw_parts, entity_type = format_geographic_input(
            **{f.name: getattr(self, f.name) for f in self._meta.fields}
        )
        return "{0}: [{1}] {2}".format(
            entity_type.capitalize() if entity_type else "Unk", self.id, address
        )

    def save(self, *args, **kwargs):
        """
        Keeps data in sync with related PlacedModel.

        Note that to have a two way sync we need a way to tell either party
        when it is being updated by the other, to avoid recursion. So we add
        a kwarg that lets us do just that.

        """
        # If save is being called because the related PlacedModel called it,
        # we will skip the data updating.
        if not self.created_date:
            self.created_date = now()

        if not kwargs.pop("saved_from_placed_object", False):
            save_geocoded_model(self)  # Only this line will stay once we remove PlacedModel
            self.sync_to_placedmodels()

        return super(Place, self).save(*args, **kwargs)

    def sync_to_placedmodels(self):
        """TEMPORARY until PlacedModel goes away."""

        related = [
            f
            for f in self._meta.get_fields()
            if (f.one_to_many or f.one_to_one) and f.auto_created and not f.concrete
        ]

        placed_managers = [descriptor.get_accessor_name() for descriptor in related]
        for manager in placed_managers:
            if self.pk:
                for placed_obj in getattr(self, manager).all():
                    placed_obj.update_from_place()
                    placed_obj.save(saved_from_place=True)

    def denormalize_related_references(self):
        """Copies FKs from related fields to local ones."""
        denormalize_related_references(self)

    def load_geocode_response_data(self):
        """Transplants raw geocoder data to the Place or PlacedModel."""
        load_geocode_response_data(self)


class Metro(models.Model):
    """Regional area"""

    objects = MetroManager()

    name = models.CharField(max_length=100, unique=True)
    cbsa_code = models.CharField(max_length=6, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Metropolitan Area"
        verbose_name_plural = "Metropolitan Areas"

    def __str__(self):
        return self.as_string()

    def as_string(self):
        """Returns a label b/c we used __str__ in a serializer before"""
        return self.name

    def natural_key(self):
        return (self.name,)


class ClimateZone(models.Model):
    """As specified by the DOE."""

    objects = ClimateZoneManager()

    zone = models.IntegerField()
    moisture_regime = models.CharField(
        max_length=2, choices=DOE_MOISTURE_REGIMES, blank=True, null=True
    )
    doe_zone = models.CharField(max_length=32, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "DOE Climate Zone"
        verbose_name_plural = "DOE Climate Zones"

    def __str__(self):
        return self.as_string()

    def as_string(self):
        """Returns a label b/c we used __str__ in a serializer before"""
        if self.moisture_regime:
            return "{}{}".format(self.zone, self.moisture_regime)
        return "{}".format(self.zone)

    def natural_key(self):
        return (self.doe_zone,)


class Country(models.Model):
    abbr = models.CharField(max_length=2, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    objects = CountryQuerySet.as_manager()

    def __str__(self):
        return self.abbr

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = [
            "abbr",
        ]


class USState(models.Model):
    abbr = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return "{},  {}".format(self.name, self.abbr)

    class Meta:
        verbose_name = "US State"
        verbose_name_plural = "US States"
        ordering = [
            "abbr",
        ]


class County(models.Model):
    """County Names"""

    objects = CountyManager()

    name = models.CharField(max_length=64)
    state = USStateField()
    county_fips = models.CharField(max_length=12, unique=True)
    county_type = models.CharField(max_length=2, choices=COUNTY_TYPES, null=True)

    # Place fields, shared with City
    legal_statistical_area_description = models.CharField(max_length=64)
    ansi_code = models.CharField(max_length=16, unique=True)
    land_area_meters = models.BigIntegerField()
    water_area_meters = models.BigIntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()

    metro = models.ForeignKey("Metro", on_delete=models.CASCADE, blank=True, null=True)
    climate_zone = models.ForeignKey("ClimateZone", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = "US County"
        verbose_name_plural = "US Counties"
        unique_together = ("legal_statistical_area_description", "state")
        ordering = ["state", "name"]

    def __str__(self):
        return f"{self.name}, {self.state}"

    def natural_key(self):
        return (self.legal_statistical_area_description, self.county_fips)


class City(models.Model):
    """City data"""

    objects = CityManager()

    name = models.CharField(max_length=64)
    county = models.ForeignKey("County", on_delete=models.CASCADE, null=True)
    country = models.ForeignKey("geographic.Country", on_delete=models.CASCADE)

    place_fips = models.CharField(max_length=12)

    # Place fields, shared with County
    legal_statistical_area_description = models.CharField(max_length=64)
    ansi_code = models.CharField(max_length=16)
    land_area_meters = models.BigIntegerField()
    water_area_meters = models.BigIntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()

    geocode_response = models.ForeignKey(
        "geocoder.GeocodeResponse",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Selected by user in case of multiple valid results, "
        "automatically when we have one result and empty when geocode do not have valid "
        "results or the user wants to use his own response",
    )

    class Meta:
        verbose_name = "City/Town"
        verbose_name_plural = "Cities/Towns"
        unique_together = (("place_fips", "county"),)
        ordering = ["country", "county__state", "county", "name"]

    def __str__(self):
        return self.as_string()

    def as_string(self):
        """Returns a label b/c we used __str__ in a serializer before"""
        if self.country.abbr != "US":
            return f"{self.name}, {self.country}"
        return f"{self.name}, {self.county.state} ({self.county.name})"

    def as_simple_string(self):
        if self.country.abbr != "US":
            return f"{self.name}, {self.country}"
        return f"{self.name}, {self.county.state}"

    def natural_key(self):
        return (self.legal_statistical_area_description, self.place_fips, self.country)

    def get_absolute_url(self):
        return reverse("city:view", kwargs=dict(pk=self.pk))

    def save(self, *args, **kwargs):
        """Fills in missing values."""

        # Inspect place_fips
        if not self.place_fips:
            other = City.objects.filter(place_fips__startswith="990").order_by("-id").first()
            if other:
                self.place_fips = int(other.place_fips) + 1
            else:
                self.place_fips = 9900000

        # Generate a description if missing
        if not self.legal_statistical_area_description:
            description = "Unregistered {} ({})".format(self.name, self.place_fips)
            self.legal_statistical_area_description = description

        if not self.ansi_code:
            self.ansi_code = self.place_fips

        if not self.country_id:
            self.country = get_usa_default()

        super(City, self).save(*args, **kwargs)

    @cached_property
    def metro(self):
        return self.county.metro if self.county else None

    @cached_property
    def state(self):
        return self.county.state if self.county else None

    def can_be_edited(self, user):
        if user.has_perm("geographic.change_city"):
            return self.place_fips[:3] == "990"
        return False

    def can_be_deleted(self, user):
        if user.has_perm("geographic.delete_city") and self.place_fips[:3] == "990":
            related_objects = sum(
                (
                    self.home_set.count(),
                    self.company_set.count(),
                    self.subdivision_set.count(),
                    self.community_set.count(),
                )
            )
            if not related_objects:
                return True
        return False
