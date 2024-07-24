"""models.py: Django geocoder"""


import logging

from django.apps import apps
from django.conf import settings
from django.db import models
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError

from axis.core.fields import AxisJSONField
from .engines import GEOCODER_ENGINE_CHOICES, GEOCODER_ENGINES
from .managers import GeocodeManager, GeocodeReponseManager

__author__ = "Peter Landry"
__date__ = "2/20/14 4:18 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Peter Landry",
    "Steven Klass",
]

from ..geographic.models import Country

from ..geographic.utils.country import get_usa_default, resolve_country

log = logging.getLogger(__name__)
app = apps.get_app_config("geocoder")

GEOCODER_RESPONSE_TIMEOUT = 4
GEOCODER_ELAPSED_TIME_TO_RECODE = settings.GEOCODER_ELAPSED_TIME_TO_RECODE


class Geocode(models.Model):
    """Record geocodes independent of their use."""

    objects = GeocodeManager()

    raw_address = models.CharField(blank=False, null=False, max_length=250)

    entity_type = models.CharField(max_length=50, default="street_address")

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    immediate = models.BooleanField(default=False)

    # Components of raw_address, which is not allowed blank, but these individual parts are
    raw_street_line1 = models.CharField(max_length=100, blank=True)
    raw_street_line2 = models.CharField(max_length=100, blank=True)
    raw_zipcode = models.CharField(max_length=15, blank=True)
    raw_city = models.ForeignKey("geographic.City", on_delete=models.CASCADE, blank=True, null=True)
    raw_county = models.ForeignKey(
        "geographic.County", on_delete=models.CASCADE, blank=True, null=True
    )
    raw_state = models.ForeignKey(
        "geographic.USState", on_delete=models.CASCADE, blank=True, null=True
    )
    raw_country = models.ForeignKey("geographic.Country", on_delete=models.CASCADE, null=True)

    raw_cross_roads = models.CharField(max_length=128, blank=True)

    class Meta:
        unique_together = (
            "raw_address",
            "entity_type",
        )

    def __str__(self):
        return "{0}: {1}".format(self.entity_type.capitalize(), self.raw_address)

    def get_engine_instance(self, engine):
        kwargs = {
            "timeout": app.GEOCODER_DEFAULT_TIMEOUT,
        }
        return GEOCODER_ENGINES[engine](**kwargs)

    @property
    def can_be_geocoded(self):
        """This determines whether or not to geocode an address based on time"""

        now_minus_mod = (now() - self.modified_date).seconds
        if now() > self.modified_date and now_minus_mod < GEOCODER_ELAPSED_TIME_TO_RECODE:
            return False
        if now() > self.modified_date and now_minus_mod > GEOCODER_ELAPSED_TIME_TO_RECODE:
            if not self.responses.count():
                log.debug("No responses and time elapsed - Allow update")
                return True
            else:
                try:
                    if not self.responses.confirmed().count():
                        log.debug(
                            "Stale responses returned on %s and they were "
                            "not confirmed - Allow "
                            "update",
                            self.modified_date.strftime("%m/%d/%y %H:%M:%S"),
                        )
                        return True
                except (KeyError, AttributeError):
                    log.debug(
                        "Stale responses returned on %s and unable to parse results - Allow "
                        "update",
                        self.modified_date.strftime("%m/%d/%y %H:%M:%S"),
                    )
                    return True
        return False

    def get_valid_responses(self, only_confirmed=True):
        valid_responses = self.responses

        if only_confirmed:
            valid_responses = self.responses.confirmed()

        valid_responses = valid_responses.statistically_likely()
        log.info(
            f"Identified {valid_responses.count()} {'confirmed ' if only_confirmed else ''}"
            f"statistically likely responses based on input"
        )
        return valid_responses.logically_reduce().all()

    def save(self, **kwargs):
        if not self.raw_country_id and self.raw_city:
            self.raw_country = self.raw_city.country

        return super(Geocode, self).save(**kwargs)


class GeocodeResponse(models.Model):
    """Record per-engine geocoding responses."""

    geocode = models.ForeignKey(Geocode, on_delete=models.CASCADE, related_name="responses")
    engine = models.CharField(
        choices=GEOCODER_ENGINE_CHOICES, max_length=32, blank=False, null=False
    )
    place = AxisJSONField(blank=True, default=dict)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = GeocodeReponseManager()

    def __str__(self):
        return "{0}: {1}".format(self.engine, self.broker.place.formatted_address)

    class Meta:
        ordering = ["-engine"]  # Google first...

    @property
    def broker(self):
        """Returns an appropriate broker instance for this response."""
        # TODO: Once geographic is refactored, move the logic from the get_broker
        # function into this method, and drop the function.
        from axis.geographic.geocoders import get_broker

        return get_broker(self)

    def get_normalized_fields(self, return_city_as_string=False):  # noqa: C901
        """
        Returns the raw geocoded data using field names we want to inspect.  In normal circumstances
        the result of this will be directly copied over to the PlacedModel/Place instance, but this
        is also used in bulk processing when a model instance isn't yet prepared for saving.
        """
        from axis.geographic.models import City, County

        place = self.broker.place
        data = {}

        if place.latitude:
            data["latitude"] = place.latitude
        if place.longitude:
            data["longitude"] = place.longitude
        if place.street_line1:
            data["street_line1"] = place.street_line1
        if place.street_line2:
            data["street_line2"] = place.street_line2
        if place.intersection:
            data["cross_roads"] = place.intersection
        if place.zipcode:
            data["zipcode"] = place.zipcode
        if place.state:
            data["state"] = place.state
        if place.country:
            data["country"] = resolve_country(place.country)
        if place.county:
            data["county"] = None
            if place.country == "US":
                try:
                    data["county"] = County.objects.get_by_string(place.county, state=data["state"])
                except County.DoesNotExist:
                    log.exception(
                        f"County {place.county} not found in {place.state}, {place.country}"
                    )
                except County.MultipleObjectsReturned:
                    log.exception(
                        f"Multiple Counties found for {place.county} in {place.state}, {place.country}"
                    )

        if place.city:
            if return_city_as_string:
                data["city"] = place.city
            else:
                _kw = {"country": resolve_country(place.country)}
                if data.get("county"):
                    _kw["county"] = data.get("county")
                if data.get("state"):
                    _kw["county__state"] = data.get("state")
                try:
                    data["city"] = City.objects.get(name__iexact=place.city, **_kw)
                except City.MultipleObjectsReturned:
                    data["city"] = City.objects.filter(name__iexact=place.city, **_kw).first()
                except City.DoesNotExist:
                    from axis.geocoder.api_v3.serializers import (
                        GeocodeCityBrokeredResponseSerializer,
                    )
                    from axis.geographic.api_v3.serializers import BaseCitySerializer

                    _city_data = GeocodeCityBrokeredResponseSerializer(instance=self).data
                    serializer = BaseCitySerializer(data=_city_data)
                    try:
                        serializer.is_valid(raise_exception=True)
                    except ValidationError:
                        data["city"] = None
                    else:
                        data["city"] = serializer.save()
                if data.get("county") is None and data["city"] and data["city"].county:
                    data["county"] = data["city"].county

        data["confirmed_address"] = place.is_confirmed
        return data
