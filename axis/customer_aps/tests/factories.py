"""factories.py: Django customer_aps"""


import logging
import random
import re
from axis.core.utils import random_longitude, random_latitude, random_digits
from axis.customer_aps.models import APSHome
from axis.customer_aps.utils import geolocate_apshome
from axis.geographic.tests.factories import city_factory, real_city_factory

__author__ = "Steven Klass"
__date__ = "4/15/14 1:19 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def apshome_factory(**kwargs):
    """A factory for creating a apshome"""

    city = kwargs.pop("city", None)
    county = kwargs.pop("county", None)
    metro = kwargs.pop("metro", None)

    geocode = kwargs.pop("geocode", False)

    kwrgs = {
        "premise_id": f"{random_digits(19)}",
        "raw_lot_number": f"{random.randint(1000000000, 9999999999)}",
        "raw_street_number": f"{random.randint(100, 999)}",
        "raw_prefix": "W",
        "raw_street_name": "MAIN",
        "raw_suffix": "ST",
        "raw_street_line_2": f"# {random.randint(100, 999)}",
        "raw_city": "GILBERT",
        "raw_state": "AZ",
        "raw_zip": "85297",
        "lot_number": f"{random.randint(1000000000, 9999999999)}",
        "street_line1": f"{random.randint(100, 999)} W. Main St",
        "street_line2": f"# {random.randint(100, 999)}",
        "latitude": random_latitude(),
        "longitude": random_longitude(),
        "confirmed_address": False,
    }

    if geocode and "street_line1" not in kwargs and "raw_street_number" not in kwargs:
        raise AttributeError("Need a real address")

    if geocode is False:
        if city is None:
            c_kwrgs = {"geocode": geocode}
            for k, v in list(kwargs.items()):
                if k in ["county", "state"]:
                    c_kwrgs[k] = v
                if k.startswith("city__"):
                    c_kwrgs[re.sub(r"city__", "", k)] = kwargs.pop(k)
            if c_kwrgs:
                raise AttributeError("Unexpected City Args.")
            kwrgs["city"] = real_city_factory("Prescott", "AZ")
            if county is None:
                kwrgs["county"] = kwrgs["city"].county
            else:
                kwrgs["county"] = county
            if kwargs.get("state", None) is None:
                kwrgs["state"] = kwrgs["city"].county.state
            if metro is None:
                kwrgs["metro"] = kwrgs["city"].county.metro
            else:
                kwrgs["metro"] = metro
        else:
            kwrgs["city"] = city
            if metro is None:
                kwrgs["metro"] = kwrgs["city"].county.metro

    kwrgs.update(kwargs)

    if geocode:
        geolocation_matches = geolocate_apshome(**kwrgs)
        if len(geolocation_matches) == 1:
            match = geolocation_matches[0]
            geocoded_data = match.get_normalized_fields()
            values = [
                "street_line1",
                "street_line2",
                "state",
                "zipcode",
                "confirmed_address",
                "latitude",
                "longitude",
            ]
            kwrgs.update({k: geocoded_data.get(k, None) for k in values})
            kwrgs["geocode_response"] = match
            kwrgs["city"] = geocoded_data.get("city") if geocoded_data.get("city") else None
            kwrgs["county"] = geocoded_data.get("county") if geocoded_data.get("county") else None

        else:
            log.warning("Fixture producing more than one geocoded address")

    meterset = kwrgs.pop("premise_id")

    apshome, create = APSHome.objects.get_or_create(premise_id=meterset, defaults=kwrgs)

    return apshome
