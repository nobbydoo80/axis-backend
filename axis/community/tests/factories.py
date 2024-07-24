"""factory.py: Django community factories"""


import re
import random

from axis.core.utils import random_sequence, random_digits, random_longitude, random_latitude
from axis.geocoder.models import Geocode
from axis.geographic.tests.factories import city_factory
from ..models import Community

__author__ = "Steven Klass"
__date__ = "1/20/12 1:28 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


def community_factory(**kwargs):
    """A community factory.  get_or_create based on the field 'name', 'builder_org'."""
    city = kwargs.pop("city", None)
    county = kwargs.pop("county", None)
    metro = kwargs.pop("metro", None)

    geocode = kwargs.pop("geocode", False)

    kwrgs = {
        "name": f"Community {random_sequence(4)}",
        "cross_roads": f"{random_digits(4)} {random_sequence(4)} and {random_digits(4)} {random_sequence(4)}",
        "latitude": random_latitude(),
        "longitude": random_longitude(),
        "confirmed_address": False,
        "website": f"https://www.{random_digits(10)}.com/",
    }
    if city is None:
        c_kwrgs = {"geocode": geocode}
        for k, v in list(kwargs.items()):
            if k in ["county", "state"]:
                c_kwrgs[k] = v
            if k.startswith("city__"):
                c_kwrgs[re.sub(r"city__", "", k)] = kwargs.pop(k)
        kwrgs["city"] = city_factory(**c_kwrgs)
        if county is None:
            kwrgs["county"] = kwrgs["city"].county
        if kwargs.get("state", None) is None and kwrgs["city"].county:
            kwrgs["state"] = kwrgs["city"].county.state
        if metro is None and kwrgs["city"].county:
            kwrgs["metro"] = kwrgs["city"].county.metro
    else:
        kwrgs["city"] = city

    kwrgs.update(kwargs)

    if geocode:
        geo = Geocode.objects.get_matches(
            raw_address=None, city=kwrgs.get("city"), cross_roads=kwrgs.get("cross_roads")
        )
        kwargs["geocode_response"] = geo[0]

    name = kwrgs.pop("name")
    city = kwrgs.pop("city")
    community, create = Community.objects.get_or_create(name=name, city=city, defaults=kwrgs)
    return community
