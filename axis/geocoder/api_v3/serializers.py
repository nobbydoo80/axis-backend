"""serializers.py: """

import logging
import re
import time

from django.db.models import Q
from localflavor.us.us_states import US_STATES
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from axis.geocoder.engines import GEOCODER_ENGINES
from axis.geocoder.models import Geocode, GeocodeResponse
from axis.geographic.api_v3.serializers import CitySerializer, CountySerializer
from axis.geographic.models import City, County, COUNTRIES, Country, USState
from axis.geographic.tests.factories import real_county_factory
from axis.geographic.utils import resolve_state, resolve_county
from axis.geographic.utils.country import resolve_country
from axis.geographic.utils.legacy import (
    format_geographic_input,
    get_or_create_us_state_object,
)

__author__ = "Artem Hruzd"
__date__ = "04/09/2020 16:22"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

log = logging.getLogger(__name__)


class GeocodeBrokeredResponseSerializer(serializers.ModelSerializer):
    """This is a way to bust out the geocode response info for just the stuff we care about"""

    street_line1 = serializers.CharField(source="broker.place.street_line1", read_only=True)
    street_line2 = serializers.CharField(source="broker.place.street_line2", read_only=True)
    intersection = serializers.CharField(source="broker.place.cross_roads", read_only=True)
    city = serializers.SerializerMethodField(read_only=True)
    city_info = serializers.SerializerMethodField(read_only=True)
    county = serializers.SerializerMethodField(read_only=True)
    county_info = serializers.SerializerMethodField(read_only=True)
    state = serializers.CharField(source="broker.place.state", read_only=True)
    country = serializers.CharField(source="broker.place.country", read_only=True)
    zipcode = serializers.CharField(source="broker.place.zipcode", read_only=True)
    latitude = serializers.FloatField(source="broker.place.latitude", read_only=True)
    longitude = serializers.FloatField(source="broker.place.longitude", read_only=True)
    confirmed_address = serializers.CharField(
        source="broker.place.confirmed_address", read_only=True
    )

    formatted_address = serializers.CharField(
        source="broker.place.formatted_address", read_only=True
    )

    entity_type = serializers.CharField(source="broker.place.entity_type", read_only=True)
    geocode_date = serializers.CharField(source="broker.place.geocode_date", read_only=True)
    engine = serializers.CharField(source="broker.place.engine", read_only=True)
    map_url = serializers.CharField(source="broker.place.map_url", read_only=True)

    class Meta:
        model = GeocodeResponse
        fields = (
            "id",
            "geocode",
            "created_date",
            "street_line1",
            "street_line2",
            "intersection",
            "city",
            "city_info",
            "county",
            "county_info",
            "state",
            "country",
            "zipcode",
            "latitude",
            "longitude",
            "formatted_address",
            "entity_type",
            "engine",
            "confirmed_address",
            "map_url",
            "geocode_date",
        )
        read_only_fields = ["id", "geocode", "place", "created_date"]

    def get_city(self, obj):
        if not obj.broker:
            return None
        try:
            city = obj.broker.city_object
        except ValidationError:
            return None
        return city.pk if city else None

    def get_city_info(self, obj):
        if not obj.broker:
            return None
        try:
            city_obj = obj.broker.city_object
        except ValidationError:
            return None
        serializer = CitySerializer(instance=city_obj)
        return serializer.data

    def get_county(self, obj):
        if not obj.broker:
            return None
        county = obj.broker.county_object
        return county.pk if county else None

    def get_county_info(self, obj):
        if not obj.broker:
            return None
        county_obj = obj.broker.county_object
        serializer = CountySerializer(instance=county_obj)
        return serializer.data


class GeocodeSerializer(serializers.ModelSerializer):
    responses = GeocodeBrokeredResponseSerializer(many=True, read_only=True)
    valid_responses = GeocodeBrokeredResponseSerializer(
        source="get_valid_responses", many=True, read_only=True
    )
    raw_city_info = CitySerializer(source="raw_city", read_only=True)

    class Meta:
        model = Geocode
        fields = (
            "id",
            "raw_address",
            "entity_type",
            "modified_date",
            "created_date",
            "immediate",
            "raw_street_line1",
            "raw_street_line2",
            "raw_zipcode",
            "raw_city",
            "raw_city_info",
            "raw_county",
            "raw_state",
            "raw_cross_roads",
            "responses",
            "valid_responses",
        )


class GeocodeInfoSerializer(serializers.ModelSerializer):
    """
    Represents short geocode info version that is usefully
    when you need to display Not confirmed address
    """

    raw_city_info = CitySerializer(source="raw_city", read_only=True)

    class Meta:
        model = Geocode
        fields = (
            "id",
            "raw_address",
            "entity_type",
            "modified_date",
            "created_date",
            "raw_street_line1",
            "raw_street_line2",
            "raw_zipcode",
            "raw_city",
            "raw_city_info",
            "raw_cross_roads",
        )


class GeocodeMixin:
    def get_geographic_responses(self, geocode_id, raw_address):
        MAX_API_WAIT_TIME = 10
        # legacy compatibility

        start_time = time.time()
        geocode = Geocode.objects.get(pk=geocode_id)
        valid_responses = geocode.responses.filter(created_date__gt=geocode.modified_date)

        geocoder_engine_set = set(GEOCODER_ENGINES.keys())
        while set(valid_responses.values_list("engine", flat=True)) != geocoder_engine_set:
            if time.time() - start_time > MAX_API_WAIT_TIME:
                missing = list(
                    geocoder_engine_set - set(valid_responses.values_list("engine", flat=True))
                )
                msg = (
                    "We don't have enough responses (%(total)s) and timed out. Missing "
                    "%(missing)s responses(s) on %(raw_address)r"
                )
                log_method = log.error
                if missing and geocode.responses.count() > 10:
                    # PO Boxes may never geocode so just move along.
                    log_method = log.debug
                    msg += " quieting due to count of responses with missing geocoders"

                log_method(
                    msg,
                    {
                        "total": geocode.responses.count(),
                        "missing": ", ".join(missing),
                        "raw_address": raw_address,
                    },
                )
                break
            time.sleep(0.5)
            geocode = Geocode.objects.get(pk=geocode.pk)
            valid_responses = geocode.responses.filter(created_date__gt=geocode.modified_date)
        return geocode

    def save(self, **kwargs) -> (Geocode, bool):
        """This returns a tuple back of created or not."""

        assert hasattr(self, "_errors"), "You must call `.is_valid()` before calling `.save()`."
        assert not self.errors, "You cannot call `.save()` on a serializer with invalid data."

        # Guard against incorrect use of `serializer.save(commit=False)`
        assert "commit" not in kwargs, (
            "'commit' is not a valid keyword argument to the 'save()' method. "
            "If you need to access data before committing to the database then "
            "inspect 'serializer.validated_data' instead. "
            "You can also pass additional keyword arguments to 'save()' if you "
            "need to set extra attributes on the saved model instance. "
            "For example: 'serializer.save(owner=request.user)'.'"
        )

        assert not hasattr(self, "_data"), (
            "You cannot call `.save()` after accessing `serializer.data`."
            "If you need to access data before committing to the database then "
            "inspect 'serializer.validated_data' instead. "
        )

        validated_data = {**self.validated_data, **kwargs}
        created = False

        if self.instance is not None:
            self.instance = self.update(self.instance, validated_data)
            assert self.instance is not None, "`update()` did not return an object instance."
        else:
            self.instance, created = self.create(validated_data)
            assert self.instance is not None, "`create()` did not return an object instance."
        return self.instance, created


class GeocodeMatchesSerializer(GeocodeMixin, serializers.Serializer):
    street_line1 = serializers.CharField(required=False, allow_blank=True)
    street_line2 = serializers.CharField(required=False, allow_blank=True)
    intersection = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Sometimes intersection is handed to us as cross_roads",
    )
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    zipcode = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        raw_address, raw_parts, entity_type = format_geographic_input(**self.validated_data)
        geocode, created = Geocode.objects.update_or_create(
            raw_address=raw_address, entity_type=entity_type, defaults=raw_parts
        )

        if not created:
            if not geocode.can_be_geocoded:
                log.debug("Address already exists - %s", raw_address)
                return geocode, created
            geocode.save()  # Kick off a geocode - This will updated the modified time
        return (
            self.get_geographic_responses(geocode_id=geocode.id, raw_address=raw_address),
            created,
        )

    def update(self, instance, validated_data):
        raise NotImplementedError

    def to_representation(self, instance):
        raise NotImplementedError

    def validate(self, attrs):
        """Validate that nothing is blank and no conflicts"""
        conflicts = any([attrs.get("street_line1"), attrs.get("street_line2")])
        if attrs.get("intersection") and conflicts:
            raise ValidationError("Street Line 1/2 cannot be combined with an intersection")

        attrs["street_line1"] = attrs.get("street_line1", "")
        attrs["street_line2"] = attrs.get("street_line2", "")
        attrs["intersection"] = attrs.get("intersection", "")
        attrs["zipcode"] = attrs.get("zipcode", "")
        return attrs


class GeocodeCityBrokeredResponseSerializer(serializers.ModelSerializer):
    """This is a way to bust out the geocode response info for just the stuff we care about"""

    name = serializers.CharField(source="broker.place.city", read_only=True)
    county = serializers.SerializerMethodField(read_only=True)
    county_info = serializers.SerializerMethodField(read_only=True)
    state = serializers.CharField(source="broker.place.state", read_only=True)
    country = serializers.CharField(source="broker.place.country", read_only=True)
    latitude = serializers.FloatField(source="broker.place.latitude", read_only=True)
    longitude = serializers.FloatField(source="broker.place.longitude", read_only=True)
    confirmed_address = serializers.CharField(
        source="broker.place.confirmed_address", read_only=True
    )

    formatted_address = serializers.CharField(
        source="broker.place.formatted_address", read_only=True
    )

    entity_type = serializers.CharField(source="broker.place.entity_type", read_only=True)
    geocode_date = serializers.CharField(source="broker.place.geocode_date", read_only=True)
    engine = serializers.CharField(source="broker.place.engine", read_only=True)
    map_url = serializers.CharField(source="broker.place.map_url", read_only=True)

    class Meta:
        model = GeocodeResponse
        fields = (
            "id",
            "geocode",
            "created_date",
            "name",
            "county",
            "county_info",
            "state",
            "country",
            "latitude",
            "longitude",
            "formatted_address",
            "entity_type",
            "engine",
            "confirmed_address",
            "map_url",
            "geocode_date",
        )
        read_only_fields = fields

    def get_county(self, obj):
        if not obj.broker:
            return None
        if obj.broker.place.county:
            county = obj.broker.county_object
            return county.pk if county else None

    def get_county_info(self, obj):
        if not obj.broker:
            return None
        county_obj = obj.broker.county_object
        serializer = CountySerializer(instance=county_obj)
        return serializer.data


city_matcher = re.compile(
    r"^(?P<name>[\w\s\-.',]+) (?P<state_country>[A-Za-z]{2})(,? \((?P<county>.*)\))?$"
)


class GeocodeCitySerializer(serializers.ModelSerializer):
    responses = GeocodeCityBrokeredResponseSerializer(many=True, read_only=True)
    valid_responses = GeocodeCityBrokeredResponseSerializer(
        source="get_valid_responses", many=True, read_only=True
    )
    raw_county_info = CountySerializer(source="county", read_only=True)

    class Meta:
        model = Geocode
        fields = (
            "id",
            "raw_address",
            "entity_type",
            "modified_date",
            "created_date",
            "immediate",
            "raw_county",
            "raw_county_info",
            "raw_state",
            "raw_country",
            "responses",
            "valid_responses",
        )


class GeocodeCityMatchesSerializer(GeocodeMixin, serializers.Serializer):
    name = serializers.CharField(required=True)
    county = serializers.PrimaryKeyRelatedField(
        queryset=County.objects.all(), required=False, allow_null=True
    )
    state = serializers.ChoiceField(choices=US_STATES, required=False, allow_null=True)
    country = serializers.ChoiceField(choices=COUNTRIES, required=False, allow_null=True)

    def validate_country(self, attr):
        return resolve_country(attr)

    @classmethod
    def parse_one_liner(
        cls,
        name: str | int | City | None,
        county: County | str | None = None,
        state: USState | str = None,
        country: Country | str = None,
    ):
        """This will allow you to pass in a string of city and state and it will figure it out"""

        # To do a proper replacement we need the in order for longest to shortest
        STATES = dict(US_STATES)
        for short in sorted(STATES, key=lambda k: len(STATES[k]), reverse=True):
            long = str(STATES[short])
            if long.lower() in name.lower():
                name = re.sub(r"\b%s\b" % long, short, name, flags=re.IGNORECASE)
                break

        for short in sorted(COUNTRIES, key=lambda k: len(COUNTRIES[k]), reverse=True):
            long = COUNTRIES[short]
            if long.lower() in name.lower():
                name = re.sub(r"\b%s\b" % long, short, name, flags=re.IGNORECASE)
                break

        match = city_matcher.match(name)
        if match:
            _name = match.group("name").rstrip(",")
            state_country = match.group("state_country")
            if match.group("county"):
                name = _name
                state = state_country
                county = match.group("county")
            else:
                try:
                    if state is None:
                        state = resolve_state(state_country)
                        name = _name
                    else:
                        raise KeyError
                except KeyError:
                    try:
                        if country is None:
                            country = resolve_country(state_country.strip())
                            name = _name
                    except KeyError:
                        pass

        if country and not isinstance(country, Country):
            country = resolve_country(country)

        if country is None and any([state, county]):
            country = resolve_country("US")

        if country and country.abbr == "US":
            if state and not isinstance(state, USState):
                state = resolve_state(state)
            if county:
                if not isinstance(county, County):
                    county = resolve_county(county, state)
                if not state:
                    state = resolve_state(county.state)
            else:
                if not state:
                    if not state:
                        raise ValidationError("You must have a state for US based countries")
                    # If we have a state - we will need these for later
                    real_county_factory(state=state.abbr)

        if country and country.abbr != "US" and any([state, county]):
            raise ValidationError("You cannot combine county / state with non US countries")

        return {"name": name, "state": state, "county": county, "country": country}

    @classmethod
    def get_existing_city_query(
        cls,
        name: str | City | None,
        county: County | None = None,
        state: USState | None = None,
        country: Country | None = None,
    ):
        # Note this is replicated in resolve city
        query = Q(name__iexact=name) | Q(legal_statistical_area_description__iexact=name)
        if country:
            query &= Q(country=country)
            if country.abbr != "US":
                query &= Q(county__isnull=True)
        if county:
            query &= Q(county=county)
        if state:
            query &= Q(county__state=state.abbr if isinstance(state, USState) else state)

        return query

    def validate(self, attrs):
        """Validate this does not already exist"""
        attrs = self.parse_one_liner(
            attrs["name"], attrs.get("county"), attrs.get("state"), attrs.get("country")
        )
        if attrs.get("country").abbr != "US" and any([attrs.get("county"), attrs.get("state")]):
            raise ValidationError(
                f"Country {attrs.get('country')} cannot be combined with county and or state"
            )
        if attrs.get("country").abbr == "US" and not any([attrs.get("county"), attrs.get("state")]):
            raise ValidationError(f"Country {attrs.get('country')} must use county and or state")
        if attrs.get("county"):
            if attrs.get("state"):
                if attrs["county"].state != attrs["state"].abbr:
                    raise ValidationError(
                        f"County {attrs.get('county')} does not equal provided "
                        f"state {attrs['state']}"
                    )
            attrs["state"] = attrs["county"].state
        query = self.get_existing_city_query(**attrs)
        objects = City.objects.filter(query)
        if objects.exists():
            raise ValidationError(f"{objects.first()} already exists {query}")
        return attrs

    def create(self, validated_data):
        county = validated_data.get("county")
        if validated_data["country"].abbr != "US":
            raw_address = f"{validated_data['name']}, {validated_data['country'].abbr}"
            raw_state = None
        else:
            raw_state = get_or_create_us_state_object(validated_data["state"])
            raw_address = f"{validated_data['name']}, {raw_state.abbr}"
            if county:
                raw_address = f"{validated_data['name']}, {county.name} {raw_state.abbr}"

        geocode, created = Geocode.objects.get_or_create(
            raw_address=raw_address,
            entity_type="city",
            defaults={
                "immediate": True,
                "raw_county": county,
                "raw_state": raw_state,
                "raw_country": validated_data["country"],
            },
        )
        if not created:
            if not geocode.can_be_geocoded:
                return geocode, created
            geocode.save()  # Kick off a geocode - This will update the modified time

        return (
            self.get_geographic_responses(geocode_id=geocode.id, raw_address=raw_address),
            created,
        )

    def update(self, instance, validated_data):
        raise NotImplementedError

    def to_representation(self, instance):
        raise NotImplementedError
