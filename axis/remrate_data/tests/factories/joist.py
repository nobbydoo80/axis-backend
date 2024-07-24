"""joist.py - simulation"""

import logging
import random

from .utils import get_factory_from_fields
from ...models import Joist

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "10/1/20 10:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def joist_factory(simulation, **kwargs):
    """A joist factory"""
    kwrgs = get_factory_from_fields(Joist)
    kwrgs["area"] = random.randint(200, 1200) + random.random()
    location_choices = [
        201,
        202,
        203,
        204,
        205,
        206,
        214,
        215,
        216,
        207,
        208,
        209,
        210,
        211,
        212,
        213,
        217,
    ]
    if simulation.numerical_version >= (16, 1):
        location_choices = [
            217,
            218,
            219,
            220,
            221,
            222,
            201,
            202,
            223,
            204,
            225,
            205,
            206,
            203,
            224,
            213,
            226,
            227,
            228,
            229,
            230,
            231,
            232,
            233,
            234,
            235,
            236,
            237,
            238,
            214,
            215,
            216,
            239,
            240,
            241,
            242,
            243,
            244,
            207,
            208,
            209,
            245,
            246,
            247,
            248,
            210,
            211,
            212,
            249,
            250,
            251,
            252,
        ]

    kwrgs["location"] = random.choice(location_choices)
    kwrgs["u_value"] = 1 / (random.randint(1, 5) + random.random())
    kwrgs.update(kwargs)

    return Joist.objects.create(simulation=simulation, building=simulation.building, **kwrgs)
