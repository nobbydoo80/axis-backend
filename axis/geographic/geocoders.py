"""utils.py: Django geographic"""

import json
import logging
import pprint
import re
from functools import cached_property

from django.utils.http import urlencode
from django.utils.timezone import now
from localflavor.us.us_states import STATES_NORMALIZED

from axis.geographic.models import City, County

log = logging.getLogger(__name__)

__author__ = "Steven Klass"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class Place(object):
    """
    This is a generic container to hold a "place".  This will then give you access to more
    attributes of a geo-coded object in a consistent manner than simply (location (lat, long)).
    """

    def __init__(self, *_args, **kwargs):
        self.street_line1 = kwargs.get("street_line1", None)
        self.street_line2 = kwargs.get("street_line2", None)
        self.city = kwargs.get("city", None)
        self.state = kwargs.get("state", None)
        self.county = kwargs.get("county", None)
        self.country = kwargs.get("country", None)
        self.zipcode = kwargs.get("zipcode", None)

        self.neighborhood = kwargs.get("neighborhood", None)
        self.intersection = kwargs.get("intersection", None)

        self.latitude = kwargs.get("latitude", None)
        self.longitude = kwargs.get("longitude", None)

        self.formatted_address = kwargs.get("formatted_address", None)
        self.entity_type = kwargs.get("entity_type", "street_address")
        self.is_confirmed = kwargs.get("is_confirmed", False)

        self.search_string = kwargs.get("search_string", None)
        self.url_sent = kwargs.get("url_sent", None)
        self.map_url = kwargs.get("map_url", None)
        self.geocoder_engine_name = kwargs.get("geocoder_engine_name", "Unknown")
        self.response = kwargs.get("response", None)
        self.geocode_date = kwargs.get("geocode_date", now())
        self.correlation_distance_km = 0.1  # Distance in km to compare equivelant points

    def __str__(self):
        return self.formatted_address

    def __repr__(self):
        results = ["Confirmed -"] if self.is_confirmed else ["Unconfirmed -"]
        if self.formatted_address:
            results.append("{}".format(self.formatted_address))
        else:
            results.append("Unknown")
        results.append("({})".format(self.geocoder_engine_name))
        return " ".join(results)

    def __eq__(self, other):
        """We really care about the locations.."""
        from .utils.legacy import haversine

        try:
            distance_km = haversine(self.longitude, self.latitude, other.longitude, other.latitude)
        except AttributeError:
            return False
        if distance_km <= self.correlation_distance_km:
            return True
        log.info(
            "Distance between %s and %s is %s km for %s",
            self.geocoder_engine_name,
            other.geocoder_engine_name,
            round(distance_km, 2),
            self.formatted_address,
        )
        return False

    # FIXME: This is... badly inefficient for queries.
    # NO REALLY FIX ME.
    def _city_id(self):
        from .models import City

        if self.city and self.state:  # These should always be available together anyway
            state = STATES_NORMALIZED[self.state.lower()]
            try:
                city = City.objects.find(name=self.city, county__state=state)
            except City.MultipleObjectsReturned as e:
                # TODO: This is is kind of a bad indicator. There shouldn't be more than one city
                # per name/state combination.
                if self.city.lower() != "portland":
                    log.error(
                        "Multiple cities detected for state=%r and name=%r.",
                        state,
                        self.city,
                        exc_info=e,
                    )
                city = City.objects.filter(name=self.city, county__state=state)[0]
            return city.id


class BaseGeocodeBroker(object):
    """
    A Broker is used to interpret the API responses that are unique to each
    API, and be able to do so repeatedly, even on old geocode json stored in
    the models.

    """

    ENGINE = None

    def __init__(self, response):
        if response.engine != self.ENGINE:
            raise ValueError("Unknown geocoding engine", response.engine)
        self.response = response
        self.entity_type = response.geocode.entity_type
        self.search_string = response.geocode.raw_address
        self._place_data = None

    @cached_property
    def place(self):
        """
        Returns a Place object (not the same as a Place model object) so one
        can reliably get at data in the GeocodeResponse.place JSON.

        """
        if self._place_data is not None:
            return self._place_data
        data = self.response.place
        if isinstance(data, str):
            data = json.loads(data)
        self._place_data = self._parse_place_json(data)
        return self._place_data

    def places_count(self):
        return 1

    @cached_property
    def county_object(self):
        if self.place.country != "US" or self.place.county is None:
            return

        from axis.geographic.utils import resolve_county

        county = None
        try:
            county = resolve_county(name=self.place.county, state_abbreviation=self.place.state)
        except County.DoesNotExist:
            pass
        if county is None and self.city_object:
            if self.city_object.county:
                county = self.city_object.county
        return county

    @cached_property
    def city_object(self):
        from axis.geographic.utils import resolve_city

        if self.place.city is None:
            return

        try:
            return resolve_city(
                name=self.place.city,
                county=self.place.county,
                state_abbreviation=self.place.state,
                country=self.place.country,
            )
        except City.DoesNotExist:
            return

    def _parse_place_json(self, data):
        raise NotImplementedError

    def get_formatted_city_address(self, location: Place):
        # We need to align this with our raw address
        formatted_address = f"{location.city}"
        if location.country == "US":
            if location.county:
                formatted_address += f", {location.county}"
            if location.state:
                formatted_address += f" {location.state}"
        else:
            if location.country:
                formatted_address += f" {location.country}"
        return formatted_address


class GoogleBroker(BaseGeocodeBroker):
    """Turn a Google GeocodeResponse into ```Place``` objects."""

    ENGINE = "Google"
    ENTITY_MAP = dict(
        county="administrative_area_level_2",
        city="locality",
        street_address="street_address",
        neighborhood="neighborhood",
        intersection="intersection",
    )

    def _parse_place_json(self, place):
        from axis.geographic.utils import resolve_country

        location = Place(
            geocoder_engine_name=self.ENGINE,
            response=place,  # record the json result
            search_string=self.search_string,
            entity_type=self.entity_type,
        )

        log.debug("{} - {}".format(location.geocoder_engine_name, pprint.pformat(place)))

        def get_component(label, type="short_name"):
            return next(
                (x for x in place.get("address_components", []) if label in x.get("types", [])),
                {},
            ).get(type)

        location.country = resolve_country(get_component("country")).abbr
        location.suite = get_component("subpremise")
        location.street_number = get_component("street_number")
        location.route = get_component("route")
        location.city = get_component("locality", "long_name")
        location.county = get_component("administrative_area_level_2")
        location.state = get_component("administrative_area_level_1")
        location.zipcode = get_component("postal_code")
        location.neighborhood = get_component("neighborhood")

        try:
            formatted_address, f_country = place.get("formatted_address", "").rsplit(",", 1)
        except ValueError:
            formatted_address = place.get("formatted_address", "")
            f_country = ""

        # We want the country to be removed for everywhere but the US and keep it simple (short)
        if f_country.strip() != "USA":
            formatted_address += f", {location.country}"

        if self.entity_type == "city":
            formatted_address = self.get_formatted_city_address(location)

        location.formatted_address = formatted_address
        if location.entity_type == "intersection":
            location.intersection = formatted_address.split(", ")[0]

        if location.street_number and location.route:
            location.street_line1 = " ".join([location.street_number, location.route])
        if location.suite:
            location.street_line2 = location.suite

        location.latitude = float(place.get("geometry", {}).get("location", {}).get("lat", 0))
        location.longitude = float(place.get("geometry", {}).get("location", {}).get("lng", 0))

        # If we got the type we are looking for mark it as good to go..
        if location.entity_type:
            data_types = place.get("types", [])
            if self.ENTITY_MAP[location.entity_type] in data_types:
                location.is_confirmed = True
            elif location.entity_type == "street_address":
                if "premise" in data_types or "subpremise" in data_types:
                    location.is_confirmed = True

        # We don't want to worry about counties / states outside of US
        if location.country != "US":
            location.county = None
            location.state = None

        map_url = "https://maps.google.com/?" + urlencode(dict(q=self.search_string))
        location.map_url = map_url
        # log.debug(f"{location.geocoder_engine_name} - {pprint.pformat(location.__dict__)}")
        return location


class BingBroker(BaseGeocodeBroker):
    """Turn a Google GeocodeResponse into a ```Place``` object."""

    ENGINE = "Bing"
    ENTITY_MAP = dict(
        county="AdminDivision2",
        city="PopulatedPlace",
        street_address="Address",
        neighborhood="Neighborhood",
        intersection="RoadIntersection",
    )

    def get_formatted_city_address(self, location: Place):
        # We need to align this with our raw address
        formatted_address = f"{location.city}"
        if location.country == "US":
            if location.county:
                formatted_address += f", {location.county}"
            if location.state:
                formatted_address += f" {location.state}"
        else:
            if location.country:
                formatted_address += f" {location.country}"
        return formatted_address

    def _parse_place_json(self, place):
        """Get the location, lat, lng from a single json place."""

        from axis.geographic.utils import resolve_country

        location = Place(
            geocoder_engine_name=self.ENGINE,
            response=place,
            search_string=self.search_string,
            entity_type=self.entity_type,
        )
        # log.debug("{} - {}".format(location.geocoder_engine_name, pprint.pformat(place)))
        county_replacements = [
            # (r"City of Fairfax", "Fairfax"),
            (r"Co\.", "County"),
            (r"C\.A\.", "Census Area"),
        ]
        if place.get("address"):
            address = place["address"]
            if "countryRegionIso2" in address:
                location.country = resolve_country(address.get("countryRegionIso2")).abbr
            else:
                location.country = resolve_country(address.get("countryRegion")).abbr
            if address.get("adminDistrict2"):
                co_name = address.get("adminDistrict2", "")
                for i in county_replacements:
                    co_name = re.sub(i[0], i[1], co_name)
                location.county = co_name
            if location.entity_type == "intersection":
                location.intersection = address.get("addressLine")
            else:
                location.street_line1 = address.get("addressLine")
            location.city = address.get("locality")
            location.state = address.get("adminDistrict")
            location.zipcode = address.get("postalCode")
            location.formatted_address = address.get("formattedAddress")

        if self.entity_type == "city":
            location.formatted_address = self.get_formatted_city_address(location)

        if place.get("point"):
            latitude, longitude = place["point"]["coordinates"]
            location.latitude = float(latitude)
            location.longitude = float(longitude)

        matching_entity = False
        if location.entity_type:
            matching_entity = self.ENTITY_MAP[location.entity_type] == place.get("entityType")
        location.is_confirmed = matching_entity

        if place.get("confidence") != "High":
            location.is_confirmed = False

        # We don't want to worry about counties / states outside of US
        if location.country != "US":
            location.county = None
            location.state = None

        map_url = "//www.bing.com/maps/?" + urlencode(dict(v=2, where1=self.search_string))
        location.map_url = map_url
        # log.debug(
        #     "{} - {}".format(location.geocoder_engine_name, pprint.pformat(location.__dict__))
        # )
        return location


def get_broker(geocode_response):
    brokers = [b for b in [GoogleBroker, BingBroker] if b.ENGINE == geocode_response.engine]
    if brokers:
        return brokers[0](geocode_response)
    return None
