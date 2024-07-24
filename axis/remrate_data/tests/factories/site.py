"""site.py: Django factories"""

import logging
import random

from .utils import random_sequence
from ...models import Site

__author__ = "Steven K"
__date__ = "01/09/2020 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


def site_factory(simulation, _result_number, **kwargs):
    suffix = kwargs.pop("suffix", random_sequence(4))

    climate_zones = [
        "8",
        "7",
        "6C",
        "6B",
        "6A",
        "5C",
        "5B",
        "5A",
        "4C",
        "4B",
        "4A",
        "3C",
        "3B",
        "3A",
        "2C",
        "2B",
        "2A",
        "1C",
        "1B",
        "1A",
    ]

    kwrgs = {
        "site_label": suffix,
        "climate_zone": random.choice(climate_zones),
        "city_number": random.randint(1, 500),
        "elevation": random.randint(1, 9000),
        "num_heating_season_days": random.randint(1, 365),
        "num_cooling_season_days": random.randint(1, 365),
        "heating_days_b65": random.randint(1, 365),
        "cooling_days_b74": random.randint(1, 365),
        "ashrae_weather_and_shielding_factor": random.randint(1, 365),
        "annual_windspeed": random.randint(1, 20),
        "annual_ambient_air_temperature": random.randint(50, 90),
    }
    kwrgs.update(kwargs)
    return Site.objects.get_or_create(
        simulation=simulation, _result_number=_result_number, defaults=kwrgs
    )[0]
