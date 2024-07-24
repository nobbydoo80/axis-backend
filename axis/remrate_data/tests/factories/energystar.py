"""energystar.py: Django factories"""


import random
import re

from .utils import random_digits
from ...models import ENERGYSTAR

__author__ = "Steven K"
__date__ = "01/09/2020 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def energystar_factory(**kwargs):
    """A energy factory.  get_or_create based on the field '_result_number'"""
    simulation = kwargs.pop("simulation", None)

    baseline = (
        random.choice(list(range(30, 120)) + list(range(50, 80)) * 5 + list(range(55, 63)) * 10)
        + random.random()
    )
    kwrgs = {
        "_result_number": int(random_digits(6)),
        "passes_energy_star_v2": True,
        "rating_number": "XXX",
        "energy_star_v2p5_pv_score": baseline,
        "energy_star_v2p5_hers_score": baseline
        + random.choice(
            [0] * 10 + [random.choice(range(0, 10)) + random.random() for _i in range(5)]
        ),
        "energy_star_v2p5_hers_saf_score": baseline,
        "energy_star_v2p5_hers_saf": 0.99,
        "passes_doe_zero": True,
        "doe_zero_hers_score": baseline,
        "doe_zero_saf_score": baseline,
    }
    baseline += random.choice(
        [0] * 10 + [random.choice(range(0, 2)) + random.random() for _i in range(5)]
    )
    kwrgs.update(
        {
            "energy_star_v3_pv_score": baseline,
            "energy_star_v3_hers_score": baseline
            + random.choice(
                [0] * 10 + [random.choice(range(0, 10)) + random.random() for _i in range(5)]
            ),
            "energy_star_v3_hers_saf_score": baseline,
            "energy_star_v3_hers_saf": 0.99,
            "energy_star_v3_hi_pv_score": baseline,
            "energy_star_v3_hi_hers_score": baseline
            + random.choice(
                [0] * 10 + [random.choice(range(0, 10)) + random.random() for _i in range(5)]
            ),
            "energy_star_v3_hi_hers_saf_score": baseline,
            "energy_star_v3_hi_hers_saf": 0.99,
        }
    )
    baseline += random.choice(
        [0] * 10 + [random.choice(range(0, 2)) + random.random() for _i in range(5)]
    )
    kwrgs.update(
        {
            "energy_star_v3p1_pv_score": baseline,
            "energy_star_v3p1_hers_score": baseline
            + random.choice(
                [0] * 10 + [random.choice(range(0, 10)) + random.random() for _i in range(5)]
            ),
            "energy_star_v3p1_hers_saf_score": baseline,
            "energy_star_v3p1_hers_saf": 0.99,
        }
    )

    if not simulation:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("simulation__"):
                c_kwrgs[re.sub(r"simulation__", "", k)] = kwargs.pop(k)
        from .simulation import simulation_factory

        kwrgs["simulation"] = simulation_factory(**c_kwrgs)
    else:
        kwrgs["simulation"] = simulation

    kwrgs.update(kwargs)
    result_number = kwrgs.pop("_result_number")

    return ENERGYSTAR.objects.get_or_create(_result_number=result_number, defaults=kwrgs)[0]
