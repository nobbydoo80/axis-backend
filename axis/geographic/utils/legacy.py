"""utils.py: Django geographic"""


import logging
import os
from math import radians, cos, sin, asin, sqrt

from django.core import management
from localflavor.us.us_states import STATE_CHOICES, STATES_NORMALIZED

__author__ = "Steven Klass"
__date__ = "3/19/13 4:31 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from axis.geographic.utils.country import resolve_country

log = logging.getLogger(__name__)


def get_address_designator(obj):
    if hasattr(obj, "address_override") and obj.address_override:
        return " ▵"  # &#9653;
    elif hasattr(obj, "confirmed_address") and obj.confirmed_address:
        return " ◦"  # &#9702;
    return ""


def get_or_create_us_state_object(name):
    """A convenience method for grabbing the US State"""
    from axis.geographic.models import USState

    if isinstance(name, USState):
        return name

    state = STATES_NORMALIZED[name.lower()]
    name = dict(STATE_CHOICES)[state]
    return USState.objects.get_or_create(abbr=state, defaults={"name": name})[0]


def dump_test_data():
    """This simply dumps the test data"""
    from ..models import City, County, Metro

    confirm = "This is going to remove geographic data prior to the dumpdata. Please confirm [N/Y]:"
    answer = input(confirm)
    if answer.lower() not in ["y", "ye", "yes"]:
        return
    City.objects.filter(
        apshome__isnull=True,
        community__isnull=True,
        company__isnull=True,
        home__isnull=True,
        subdivision__isnull=True,
    ).delete()
    County.objects.filter(
        apshome__isnull=True,
        community__isnull=True,
        company__isnull=True,
        home__isnull=True,
        subdivision__isnull=True,
        city__isnull=True,
    ).delete()
    Metro.objects.filter(
        community__isnull=True,
        home__isnull=True,  # samplingaccounting__isnull=True,
        subdivision__isnull=True,
        county__isnull=True,
    ).delete()
    fixture = os.path.abspath("%s/fixtures/test_geographic.json" % os.path.dirname(__file__))
    includes, excludes = ["geographic"], []
    management.call_command(
        "dumpdata",
        *includes,
        format="json",
        indent=4,
        exclude=excludes,
        use_natural_keys=True,
        traceback=True,
        stdout=open(fixture, "w"),
    )


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km


def format_geographic_input(  # noqa: C901
    street_line1=None,
    street_line2=None,
    intersection=None,
    community=None,
    city=None,
    county=None,
    state=None,
    country="US",
    zipcode=None,
    is_multi_family=None,
    **kwargs,
):
    """
    Returns a tuple with a formatted address and entity type for given
    geographic inputs.

    The first member of the tuple will be a string containing the address.
    The second member will be either ``None`` or one of the types in
    ``.models.PLACE_ENTITY_TYPES``

    Usage::

        # Note that we use the ``dict`` method of the QueryDict (request.GET) so
        # that values are a single value, not a list of values.
        address, raw_parts, entity_type = format_geographic_input(**request.GET.dict())

    """
    from axis.community.models import Community
    from ..models import City, County

    # Sometimes intersection is handed to us as ``cross_roads``
    intersection = intersection or kwargs.get("cross_roads", "")

    # Get model objects for anything that we can.
    if country and isinstance(country, str):
        country = resolve_country(country)

    if state:
        try:
            state = STATES_NORMALIZED[state.lower()]
        except KeyError:
            log.error("State not found", exc_info=1, extra={"state": state})
            state = None

    if community:
        try:
            community = int(community)
        except (ValueError, TypeError):
            pass
        if not isinstance(community, Community):
            try:
                community = Community.objects.get(id=community)
            except Community.DoesNotExist:
                log.exception("Community not found", extra={"id": community})

        if isinstance(community, Community):
            # Note that we will now ignore any city, county, and state data and
            # assume we should use that on the community. (We should not be
            # given both anyway.)
            intersection = intersection or community.cross_roads
            city = community.city
            county = city.county
            state = county.state if county else None

    if county:
        try:
            county = int(county)
        except (ValueError, TypeError):
            pass
        if not isinstance(county, County) and isinstance(county, int):
            try:
                county = County.objects.get(id=county)
            except County.DoesNotExist:
                log.error("County not found", exc_info=1, extra={"id": county})
                county = None

        if isinstance(county, County):
            # Note that we will now ignore any state data and assume we should
            # use that on the county. (We should not be given both anyway.)
            state = county.state

    if city:
        try:
            city = int(city)
        except (ValueError, TypeError):
            pass
        if not isinstance(city, City) and isinstance(city, int):
            try:
                city = City.objects.get(id=city)
            except City.DoesNotExist:
                log.exception("City not found", extra={"id": city})
                raise

        if isinstance(city, City):
            if not county:
                county = city.county
            if county and not state:
                state = county.state
            country = city.country

    us_state = None
    if state:
        us_state = get_or_create_us_state_object(state)

    # Now start building up the formatted address.
    address = ""
    raw_parts = {
        "raw_street_line1": street_line1,
        "raw_street_line2": street_line2,
        "raw_zipcode": zipcode,
        "raw_city": city,
        "raw_county": county,
        "raw_country": country,
        "raw_state": us_state,
        "raw_cross_roads": intersection,
    }
    entity_type = None

    if zipcode:
        address = f", {zipcode}"

    if state:
        address = f"{state}{address}"

    # Don't include the county if we are geocoding on the street-level and
    # there is a city.
    if county and (not city or not (intersection or street_line1 or street_line2)):
        entity_type = "county"
        if isinstance(county, County):
            address = "{0}, {1}".format(county.legal_statistical_area_description, address)
        else:
            address = "{0}, {1}".format(county, address)

    if city:
        entity_type = "city"
        if isinstance(city, City):
            address = f"{city.name}, { address.lstrip(', ')}"
        else:
            address = f"{city}, { address.lstrip(', ')}"

    # TODO: Handle neighborhood entity type.

    # Once to the street-level, handle street_lineN before intersection, because
    # the user may have supplied a community and street_lineN. In that case we
    # want to ignore the intersection that community may have, and use street_lineN.
    if street_line1 or street_line2:
        entity_type = "street_address"
        if street_line2 and not is_multi_family:
            address = "{0}, {1}".format(street_line2, address)
        if street_line1:
            address = "{0}, {1}".format(street_line1, address)
    elif intersection:
        entity_type = "intersection"
        address = "{0}, {1}".format(intersection, address)

    if not intersection and country.abbr != "US":
        address += f", {country}"

    # log.debug('{entity_type} address formatted for processing: {address}'.format(
    #           address=address, entity_type=entity_type))

    return (address, raw_parts, entity_type)


def save_geocoded_model(obj):
    """Common logic for PlacedModel and Place save() methods."""
    # TODO: This can be moved to Place.save() directly once PlacedModel is gone.
    obj.load_geocode_response_data()
    obj.denormalize_related_references()


def denormalize_related_references(obj):
    """Inspects the target object for extended related fields that we want to copy to it."""

    # Find an extended value for City
    if hasattr(obj, "city") and not obj.city:
        if hasattr(obj, "community") and obj.community:
            log.debug("Gathering city from community")
            obj.city = obj.community.city
        if hasattr(obj, "subdivision") and obj.subdivision:
            log.debug("Gathering city from subdivision")
            obj.city = obj.subdivision.city

    # Pull city fields to local object
    if hasattr(obj, "city") and obj.city:
        obj.county = obj.city.county
    if hasattr(obj, "county") and obj.county:
        if hasattr(obj, "state"):
            obj.state = obj.county.state
        if hasattr(obj, "metro"):
            obj.metro = obj.county.metro
        if hasattr(obj, "climate_zone"):
            obj.climate_zone = obj.county.climate_zone


def denormalize_related_references_dict(data):
    """Performs the same work as ``denormalize_related_references``, but without an object."""
    # Find an extended value for City
    if not data.get("city"):
        if data.get("community"):
            log.debug("Gathering city from community")
            data["city"] = data["community"].city
        if data.get("subdivision"):
            log.debug("Gathering city from subdivision")
            data["city"] = data["subdivision"].city

    # Pull city fields to local object
    if data.get("city"):
        data["county"] = data["city"].county
    if data.get("county"):
        data["state"] = data["county"].state
        if data["county"].metro:
            data["metro"] = data["county"].metro
        if data["county"].climate_zone:
            data["climate_zone"] = data["county"].climate_zone


def load_geocode_response_data(obj):
    """Transplants raw geocoder data to the Place or PlacedModel."""
    # TODO: This can be moved to a method on Place once PlacedModel is gone.
    if obj.geocode_response:
        normalized_data = obj.geocode_response.get_normalized_fields()

        for k, v in normalized_data.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        obj.address_override = False
    else:
        obj.confirmed_address = False
        obj.latitude = None
        obj.longitude = None


def do_blind_geocode(obj, **kwargs):
    """
    Passes through ``kwargs`` to geocoding API and tries to assign a single geocoding match to the
    object.  If more than one candidate match exists, we can't confirm the address.
    """
    from axis.geocoder.models import Geocode
    from axis.geographic.models import Place

    if hasattr(obj, "address_override") and obj.address_override:
        log.warning("Refusing to update b/c address override is enabled")
        return obj

    if obj.geocode_response:
        obj.geocode_response = None
    if obj.place:
        # WARNING: Don't delete the Place because we cannot be sure what other objects reference it.
        obj.place = None

    obj.confirmed_address, obj.address_override = False, False
    obj.save(saved_from_place=True)  # All this is doing is not forcing update Home Obj.

    matches = Geocode.objects.get_matches(**kwargs)
    place_repr = "<%s:%d:%s...>" % (obj.__class__.__name__, obj.pk, str(obj)[:10])
    if matches.count() == 1:
        obj.geocode_response = matches[0]
        obj.load_geocode_response_data()  # Forcibly soak up the new geocoding data
        obj.confirmed_address = True
        log.info("Blind geocode success for {place}".format(place=place_repr))
    else:
        msg = f"Blind geocode failure for {place_repr}: No candidate matches for {kwargs}"
        if matches.count() > 1:
            msg = f"Blind geocode failure for {place_repr}: Can't choose between {matches.count()} candidates"
        log.info(msg)

    denormalize_related_references(obj)
    if not isinstance(obj, Place):
        obj.update_to_place()
    return obj
