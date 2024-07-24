"""factory.py: Django geographic"""

__author__ = "Steven Klass"
__date__ = "4/17/13 9:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging
import os
import random
import re

from django.core import management
from localflavor.us.us_states import STATES_NORMALIZED

from axis.core.utils import (
    random_sequence,
    random_digits,
    random_latitude,
    random_longitude,
)
from axis.geocoder.models import Geocode
from ..models import Metro, ClimateZone, City, County, USState
from ..strings import COUNTY_TYPES

from ..utils.country import resolve_country, get_usa_default

source_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sources")
WORLD_CITIES = os.path.abspath(os.path.join(source_dir, "world_cities.csv.Z"))

log = logging.getLogger(__name__)


def metro_factory(**kwargs):
    """A metro factory.  get_or_create based on the field 'name'"""
    kwrgs = {
        "name": f"Metro {random_sequence(4)}",
        "cbsa_code": f"{random_digits(6)}",
        "is_active": True,
    }
    kwrgs.update(kwargs)
    name = kwrgs.pop("name")
    return Metro.objects.get_or_create(name=name, defaults=kwrgs)[0]


def climate_zone_factory(**kwargs):
    """A county factory.  get_or_create based on the field 'doe_zone'."""
    valid_choices = [
        ("8", None),
        ("7", None),
        ("6", "C"),
        ("6", "B"),
        ("6", "A"),
        ("5", "C"),
        ("5", "B"),
        ("5", "A"),
        ("4", "C"),
        ("4", "B"),
        ("4", "A"),
        ("3", "C"),
        ("3", "B"),
        ("3", "A"),
        ("2", "C"),
        ("2", "B"),
        ("2", "A"),
        ("1", "C"),
        ("1", "B"),
        ("1", "A"),
    ]
    valid_choice = random.choice(valid_choices)
    kwrgs = {
        "zone": valid_choice[0],
        "moisture_regime": valid_choice[1],
        "is_active": True,
    }
    kwrgs.update(kwargs)
    moisture_map = {"A": "moist", "B": "dry", "C": "marine"}
    doe_zone = (
        f"{kwrgs['zone']}_{moisture_map[kwrgs['moisture_regime'].upper()]}"
        if kwrgs["moisture_regime"]
        else f"{kwrgs['zone']}"
    )
    return ClimateZone.objects.get_or_create(doe_zone=doe_zone, defaults=kwrgs)[0]


def county_factory(**kwargs):
    """A county factory.  get_or_create based on the field 'name'."""
    metro = kwargs.pop("metro", None)
    climate_zone = kwargs.pop("climate_zone", None)

    kwrgs = {
        "name": f"County {random_sequence(4)}",
        "state": random.choice(list(set(STATES_NORMALIZED.values()))),
        "county_fips": str(random.randint(1000, 9999)),
        "county_type": random.choice(list(dict(COUNTY_TYPES).keys())),
        "legal_statistical_area_description": f"Description {random_sequence(4)}",
        "ansi_code": random_digits(4),
        "land_area_meters": random_digits(10),
        "water_area_meters": random_digits(10),
        "latitude": random_latitude(),
        "longitude": random_longitude(),
    }
    if "name" in kwargs and "legal_statistical_area_description" not in kwargs:
        kwargs["legal_statistical_area_description"] = kwargs["name"]

    kwrgs.update(kwargs)
    name = kwrgs.pop("name")
    state = kwrgs.pop("state")
    county, create = County.objects.get_or_create(name=name, state=state, defaults=kwrgs)
    if create and (metro or climate_zone):
        county.metro = metro
        county.climate_zone = climate_zone
        county.save()
    return county


def city_factory(**kwargs):
    """A city factory.  get_or_create based on the field 'name'."""
    county = kwargs.pop("county", None)
    country = kwargs.pop("country", None)
    geocode = kwargs.pop("geocode", False)

    kwrgs = {
        "name": f"City {random_sequence(4)}",
        "place_fips": random_digits(10),
        "legal_statistical_area_description": f"Description {random_sequence(4)}",
        "ansi_code": random_digits(10),
        "land_area_meters": int(random_digits(10)),
        "water_area_meters": int(random_digits(10)),
        "latitude": random_latitude(),
        "longitude": random_longitude(),
    }
    if not county:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("county__"):
                c_kwrgs[re.sub(r"county__", "", k)] = kwargs.pop(k)
        if len(c_kwrgs.keys()) == 0:
            c_kwrgs.update(
                {
                    "name": "San Bernardino County",
                    "state": "CA",
                }
            )
        kwrgs["county"] = county_factory(**c_kwrgs)
    else:
        kwrgs["county"] = county

    if not country:
        kwrgs["country"] = get_usa_default()
    else:
        if isinstance(country, str):
            kwrgs["country"] = resolve_country(country)
        else:
            kwrgs["country"] = country

    kwrgs.update(kwargs)
    kwrgs["place_fips"] = kwrgs["place_fips"][:12]

    if geocode:
        geo = Geocode.objects.get_matches(
            raw_address="{} {}".format(kwrgs.get("name"), kwrgs.get("county").state),
            entity_type="city",
        )
        kwargs["geocode_response"] = geo[0]

    name = kwrgs.pop("name")

    return City.objects.get_or_create(name=name, defaults=kwrgs)[0]


def us_states_factory(state, add_all=True):
    """This will generate the US States Model"""
    from localflavor.us.us_states import CONTIGUOUS_STATES, NON_CONTIGUOUS_STATES

    entities = CONTIGUOUS_STATES + NON_CONTIGUOUS_STATES

    query = USState.objects.filter(abbr=state)
    if query.exists():
        return query.first()
    if not add_all:
        try:
            entities = [next(((x, y) for x, y in entities if x == state))]
        except StopIteration:
            raise KeyError(f"Unable to find state {state!r}")
    USState.objects.bulk_create(USState(abbr=abbr, name=name) for abbr, name in entities)
    return USState.objects.get(abbr=state)


def real_county_factory(name=None, state=None, include_cities=True, stdout=None):
    """This will create a full county, climate zones, metros (if applicable) and cities (opt)"""
    # Note there is much better use of this in resolve county
    kw = {}

    if name is None and state is None:
        raise KeyError("You must provide a name or state")
    if name is not None:
        kw["name__iexact"] = name
    if state is not None:
        kw["state__iexact"] = state

    county = County.objects.filter(**kw).first()
    if county:
        return county
    args = ["update_base_geographic_data", "--county", name]
    if state:
        args += ["--state", state]
    if not include_cities:
        args.append("--exclude_cities")
    with open(os.devnull, "w") as stdout:
        management.call_command(*args, stdout=stdout)
    return County.objects.filter(**kw).first()


def real_city_factory(name, state=None, country="US"):
    """This will create a city(s), with county(s) climate zone(s) and metro(s) (if applicable)"""

    country = resolve_country(country)

    if country.abbr != "US" and state is not None:
        raise KeyError("If you use a country don't put a state")
    if country.abbr == "US" and state is None:
        raise KeyError("If you intend to use the US you must provide a state")

    f_kwargs = {"name__iexact": name, "country": country}
    mgmt_args = [
        "update_base_geographic_data",
        "--city",
        name,
        "--country",
        country.abbr,
    ]
    if state:
        f_kwargs["county__state"] = state
        mgmt_args += ["--state", state]
    city = City.objects.filter(**f_kwargs).first()
    if city:
        return city
    else:
        with open(os.devnull, "w") as stdout:
            management.call_command(*mgmt_args, stdout=stdout)
    return City.objects.filter(**f_kwargs).first()
