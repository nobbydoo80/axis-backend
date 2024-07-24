"""hers.py: Django factories"""


import random
import re

from .utils import random_digits
from ...models import HERS

__author__ = "Steven K"
__date__ = "01/09/2020 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def hers_factory(**kwargs):
    """A energy factory.  get_or_create based on the field '_result_number'"""
    simulation = kwargs.pop("simulation", None)

    baseline = (
        random.choice(list(range(30, 120)) + list(range(50, 80)) * 5 + list(range(55, 63)) * 10)
        + random.random()
    )
    kwrgs = {
        "_result_number": int(random_digits(6)),
        "rating_number": "XXX",
        "score": baseline,
        "total_cost": 1312.156128,
        "stars": 5.5,
        "reference_heating_consumption": 56.548229,
        "reference_cooling_consumption": 6.210601,
        "reference_hot_water_consumption": 21.127651,
        "reference_lights_appliance_consumption": 25.486813,
        "reference_photo_voltaic_consumption": 0.0,
        "reference_total_consumption": 109.373291,
        "designed_heating_consumption": 30.776655,
        "designed_cooling_consumption": 2.928889,
        "designed_hot_water_consumption": 13.680795,
        "designed_lights_appliance_consumption": 21.95463,
        "designed_photo_voltaic_consumption": 0.0,
        "designed_total_consumption": 69.340965,
        "ny_score": 0.0,
        "passes_2005_epact_tax_credit": False,
        "hers_130_savings": None,
    }

    if not simulation:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("simulation__"):
                c_kwrgs[re.sub(r"simulation__", "", k)] = kwargs.pop(k)
        from . import simulation_factory

        kwrgs["simulation"] = simulation_factory(**c_kwrgs)
    else:
        kwrgs["simulation"] = simulation

    kwrgs.update(kwargs)
    result_number = kwrgs.pop("_result_number")

    return HERS.objects.get_or_create(_result_number=result_number, defaults=kwrgs)[0]
