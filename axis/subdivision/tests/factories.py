"""factory.py: Django subdivision factories"""
import random
import re

from axis.core.utils import random_sequence, random_longitude, random_latitude
from axis.geocoder.models import Geocode
from axis.geographic.tests.factories import city_factory, climate_zone_factory
from ..models import Subdivision

__author__ = "Steven Klass"
__date__ = "1/20/12 1:28 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


def subdivision_factory(**kwargs):
    """A subdivision factory.  get_or_create based on the field 'name', 'builder_org'."""
    city = kwargs.pop("city", None)
    county = kwargs.pop("county", None)
    metro = kwargs.pop("metro", None)
    climate_zone = kwargs.pop("climate_zone", None)
    builder_org = kwargs.pop("builder_org", None)

    geocode = kwargs.pop("geocode", False)

    kwrgs = {
        "name": f"Subdivision {random_sequence(4)}",
        "builder_name": f"Alt {random.randint(1000, 9999)}",
        "cross_roads": f"{random.randint(1000, 9999)} {random_sequence(4)} and {random.randint(1000, 9999)} {random_sequence(4)}",
        "latitude": random_latitude(),
        "longitude": random_longitude(),
        "confirmed_address": False,
        "use_sampling": False,
        "use_metro_sampling": False,
    }

    if not city:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k in ["county", "state"]:
                c_kwrgs[k] = v
            if k.startswith("city__"):
                c_kwrgs[re.sub(r"city__", "", k)] = kwargs.pop(k)
        kwrgs["city"] = city_factory(**c_kwrgs)
        if not county and kwrgs["city"].county:
            kwrgs["county"] = kwrgs["city"].county
        if not kwargs.get("state") and kwrgs["city"].county:
            kwrgs["state"] = kwrgs["city"].county.state
        if not metro and kwrgs["city"].county:
            kwrgs["metro"] = kwrgs["city"].county.metro
        if not climate_zone:
            if kwrgs["city"].county and kwrgs["city"].county.climate_zone:
                kwrgs["climate_zone"] = kwrgs["city"].county.climate_zone
            elif kwrgs["city"].country and kwrgs["city"].country.abbr == "US":
                kwrgs["climate_zone"] = climate_zone_factory()
    else:
        kwrgs["city"] = city

    if not builder_org:
        from axis.company.tests.factories import builder_organization_factory

        c_kwrgs = {"city": kwrgs.get("city")}
        for k, v in list(kwargs.items()):
            if k.startswith("builder_org__"):
                c_kwrgs[re.sub(r"builder_org__", "", k)] = kwargs.pop(k)
        kwrgs["builder_org"] = builder_organization_factory(**c_kwrgs)
    else:
        kwrgs["builder_org"] = builder_org

    kwrgs.update(kwargs)

    if geocode:
        geo = Geocode.objects.get_matches(
            raw_address=None,
            city=kwrgs.get("city"),
            cross_roads=kwrgs.get("cross_roads"),
        )
        kwargs["geocode_response"] = geo[0]

    builder_org = kwrgs.pop("builder_org")
    name = kwrgs.pop("name")
    subdivision, create = Subdivision.objects.get_or_create(
        name=name, builder_org=builder_org, defaults=kwrgs
    )
    if create:
        from axis.relationship.models import Relationship

        Relationship.objects.validate_or_create_relations_to_entity(subdivision, builder_org)
    return subdivision
